from sqlalchemy.orm import Session

from app.models import User
from app.schemas import SignupRequest, LoginRequest
from app.auth.utils import hash_password, verify_password, create_access_token

def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(request: SignupRequest, db: Session) -> User:
    new_user = User(
        email=request.email,
        hashed_password=hash_password(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(request: LoginRequest, db: Session) -> str | None:
    user = get_user_by_email(request.email, db)
    if not user or not verify_password(request.password, user.hashed_password):
        return None
    return create_access_token({"sub": user.email})
