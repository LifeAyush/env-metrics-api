from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.auth import service
from app.database import get_db
from app.schemas import SignupRequest, LoginRequest

router = APIRouter()

@router.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    if service.get_user_by_email(request.email, db):
        raise HTTPException(status_code=400, detail="Email already registered")
    service.create_user(request, db)
    return {"message": "User created successfully"}

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    token = service.authenticate_user(request, db)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}
