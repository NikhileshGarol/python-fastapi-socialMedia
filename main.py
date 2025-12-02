from fastapi import FastAPI
from routers import post, users, auth, vote, chat
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="My Project API",
    description="Crud API with FastAPI and MySQL",
    version="1.0.0"
)
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="uploads"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router, prefix="/posts", tags=["Posts"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/login", tags=["Authentication"])
app.include_router(vote.router, prefix="/vote", tags=["Votes"])
app.include_router(chat.router, tags=["Chat"])