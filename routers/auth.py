from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import Auth
from models import User
import utils
import oauth


router = APIRouter()


@router.post("/", status_code=status.HTTP_200_OK)
def login(user_credentials: Auth, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    access_token = oauth.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "first_name": user.first_name, "last_name": user.last_name}
