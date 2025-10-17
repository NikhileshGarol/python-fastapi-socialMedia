from fastapi import FastAPI, status, HTTPException, Depends, APIRouter, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Post, User, Vote
from schemas import PostCreate, PostResponse, PostOut
import oauth
from typing import List, Optional
from sqlalchemy import func
from ai_models import sentiment_analyzer, summarizer
import os
from uuid import uuid4


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


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth.get_current_user),
    file: Optional[UploadFile] = File(None)
):
    print('email', current_user)
    # Run sentiment analysis
    result = sentiment_analyzer(content)[0]
    sentiment = result["label"]

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


@router.get("/", response_model=List[PostOut])
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

    post_query.update(updated_post.dict(), synchronize_session=False)
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

    summary_result = summarizer(
        post.content, min_length=25, do_sample=False
    )[0]
    post_query.update(
        {"summary": summary_result["summary_text"]}, synchronize_session=False)
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
