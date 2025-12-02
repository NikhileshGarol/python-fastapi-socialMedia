from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from fastapi import UploadFile, File


class UserBase(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class VoteOut(BaseModel):
    user: UserResponse

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    description: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = None


    class Config:
        orm_mode = True


class PostCreate(PostBase):
    pass


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    updated_at: datetime
    user: UserResponse
    sentiment: str
    summary: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: PostResponse
    votes: List[VoteOut]
    votes_count: int

    class Config:
        orm_mode = True


class Auth(BaseModel):
    email: EmailStr
    password: str


class VoteBase(BaseModel):
    post_id: int
    dir: int  # 1 for upvote, 0 for remove vote

class ContentRequest(BaseModel):
    context: str