from sqlalchemy import Column, Integer, String, Boolean, DateTime, text, ForeignKey
from base import Base
from datetime import datetime
from sqlalchemy.orm import relationship


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(String(2000), nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_at = Column(DateTime, server_default=text('now()'), nullable=False)
    updated_at = Column(DateTime, server_default=text(
        'now()'), onupdate=datetime.now(), nullable=False)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User")
    description = Column(String(255), nullable=True)
    sentiment = Column(String(50), nullable=False, server_default='NEUTRAL')
    summary = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)

    votes = relationship("Vote", back_populates="post", cascade="all, delete")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=text('now()'), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    votes = relationship("Vote", back_populates="user", cascade="all, delete")


class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey(
        "posts.id", ondelete="CASCADE"), primary_key=True)

    user = relationship("User", back_populates="votes")
    post = relationship("Post", back_populates="votes")
