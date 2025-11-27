from fastapi import FastAPI, status, HTTPException, Depends, APIRouter, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Post, User, Vote
from schemas import PostCreate, PostResponse, PostOut
import oauth
from typing import List, Optional
from sqlalchemy import func
from ai_models import sentiment_analyzer, summarizer
from datetime import datetime
from llm_service import LLMService
import os
from uuid import uuid4
from services.mcp_client import MCPClient


router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
# Base.metadata.create_all(bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth.get_current_user),
    file: Optional[UploadFile] = File(None)
):
    print('email', current_user)
    # Run sentiment analysis via MCP sentiment tool with local fallback
    sentiment = None
    try:
        sentiment_payload = {"text": content}
        sentiment_result = MCPClient.invoke_tool("sentiment", sentiment_payload)
        if isinstance(sentiment_result, dict):
            sentiment = sentiment_result.get("sentiment")
    except Exception as exc:
        print("MCP sentiment tool failed:", exc)

    if not sentiment:
        result = sentiment_analyzer(content)[0]
        sentiment = result["label"]

    sentiment = (sentiment or "NEUTRAL").strip()
    if len(sentiment) > 50:
        sentiment = sentiment[:50]

    image_url = None
    if file:
        file_ext = os.path.splitext(file.filename)[1]
        new_filename = f"{uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        image_url = f"/static/{new_filename}"
    print(image_url)
    post = Post(
        title=title,
        content=content,
        image_url=image_url,
        user_id=current_user.id,
        sentiment=sentiment,
    )

    db_post = post
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.get("", response_model=List[PostOut])
def get_posts(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    posts = (
        db.query(Post)
        .options(joinedload(Post.votes).joinedload(Vote.user))
        .filter(Post.title.contains(search))
        .order_by(Post.created_at.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )
    result = []
    for post in posts:
        votes = [{"user": vote.user} for vote in post.votes]
        votes_count = len(post.votes)
        result.append({
            "Post": post,
            "votes": votes,
            "votes_count": votes_count
        })
    return result


@router.get("/{id}", response_model=PostOut)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(Post).options(joinedload(Post.votes).joinedload(
        Vote.user)).filter(Post.id == id).first()
    if post:
        votes = [{"user": vote.user} for vote in post.votes]
        votes_count = len(post.votes)
        return {
            "Post": post,
            "votes": votes,
            "votes_count": votes_count
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Post with id {id} not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth.get_current_user)):
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authoried to perform this action")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}


@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_post(id: int, updated_post: PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth.get_current_user)):
    post_query = db.query(Post).filter(Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform this action")

    update_data = updated_post.dict()
    update_data['updated_at'] = datetime.now()

    post_query.update(update_data, synchronize_session=False)
    db.commit()
    return post_query.first()


@router.post("/{id}/summarize", status_code=status.HTTP_200_OK, response_model=PostResponse)
def summarize_post(id: int, db: Session = Depends(get_db)):
    post_query = db.query(Post).filter(Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    # if post.user_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="Not authorized to summarize this post")
    if not post.content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Post content is empty, cannot summarize.")

    # summary_result = summarizer(
    #     post.content, min_length=25, do_sample=False
    # )[0]
    # post_query.update(
    #     {"summary": summary_result["summary_text"]}, synchronize_session=False)

        # 1) Ask MCP server for any additional context (optional)
    try:
        context = MCPClient.get_resource("post_meta", params={"post_id": post.id})
    except Exception:
        context = {}
        # 2) Invoke MCP tool 'summarize' (this tool is implemented server-side)
    payload = {"text": post.content, "context": context}
    try:
        tool_result = MCPClient.invoke_tool("summarize", payload)
        summary_text = tool_result.get("summary")
    except Exception as e:
        # fallback: either raise or fallback to provider directly
        raise HTTPException(status_code=500, detail=f"MCP tool error: {e}")
    
    #     # Summarize via Perplexity
    # summary_text = LLMService.summarize_text(post.content)
        # SAFETY NET
    summary_text = summary_text[:500]
    post_query.update({"summary": summary_text}, synchronize_session=False)
    db.commit()
    db.refresh(post)
    return post


@router.post("/upload-image/{id}", status_code=status.HTTP_200_OK)
def upload_image(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth.get_current_user)
):
    post_query = db.query(Post).filter(Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=404, detail=f"Post {id} not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    file_ext = os.path.splitext(file.filename)[1]
    new_filename = f"{uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    image_url = f"/static/{new_filename}"
    post.image_url = image_url   # Save directly to DB
    db.commit()
    db.refresh(post)

    return {"image_url": image_url}
