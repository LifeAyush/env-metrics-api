from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.models import User
from app.config import settings
from app.database import get_db
from app.exceptions import AuthenticationError
from app.logger import setup_logger

logger = setup_logger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT access token
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("sub")
        
        if email is None:
            logger.warning("JWT token missing 'sub' claim")
            raise AuthenticationError("Invalid token format")
            
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise AuthenticationError("Invalid or expired token")
    except Exception as e:
        logger.error(f"Unexpected error during JWT decoding: {e}")
        raise AuthenticationError("Token validation failed")

    try:
        # Get user from database
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            logger.warning(f"User not found for email: {email}")
            raise AuthenticationError("User not found")
            
        logger.debug(f"User authenticated successfully: {email}")
        return user
        
    except Exception as e:
        logger.error(f"Database error while fetching user {email}: {e}")
        raise AuthenticationError("Failed to validate user")
