from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from models import Post, User, Vote
from schemas import PostCreate, PostResponse, PostOut
import oauth
from typing import List, Optional
from sqlalchemy import func

router = APIRouter()
# Base.metadata.create_all(bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth.get_current_user)):
    print('email', current_user)
    db_post = Post(user_id=current_user.id, **post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.get("/", response_model=List[PostOut])
def get_posts(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # posts = db.query(Post).filter(Post.title.contains(
    #     search)).limit(limit).offset(skip).all()
    results = db.query(Post, func.count(Vote.post_id).label("votes")).join(
        Vote, Vote.post_id == Post.id, isouter=True).group_by(Post.id).filter(Post.title.contains(
            search)).limit(limit).offset(skip).all()

    return results


@router.get("/{id}", response_model=PostOut)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(Post, func.count(Vote.post_id).label("votes")).join(
        Vote, Vote.post_id == Post.id, isouter=True).group_by(Post.id).filter(Post.id == id).first()
    if post:
        return post
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
def update_post(id: int, updated_post: PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(Post).filter(Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return {"data": post_query.first()}
