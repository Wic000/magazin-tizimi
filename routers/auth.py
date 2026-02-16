"""Autentifikatsiya API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import LoginRequest, Token, UserCreate
from auth import authenticate_user, create_access_token, get_password_hash

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Login yoki parol noto'g'ri")
    token = create_access_token(data={"sub": user.username})
    return Token(
        access_token=token,
        user={
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name or user.username,
            "role": user.role
        }
    )


@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Bu foydalanuvchi nomi band")
    user = User(
        username=data.username,
        password_hash=get_password_hash(data.password),
        full_name=data.full_name,
        role=data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "role": user.role}
