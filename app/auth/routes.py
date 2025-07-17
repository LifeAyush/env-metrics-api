from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.auth import service
from app.database import get_db
from app.schemas import SignupRequest, LoginRequest
from app.exceptions import AuthenticationError, ValidationError, DatabaseError
from app.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        request: User registration data
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        ValidationError: If user data is invalid
        DatabaseError: If database operation fails
    """
    try:
        # Check if user already exists
        if service.get_user_by_email(request.email, db):
            logger.warning(f"Signup attempt with existing email: {request.email}")
            raise ValidationError("Email already registered")
        
        service.create_user(request, db)
        logger.info(f"User signup successful: {request.email}")
        return {"message": "User created successfully"}
        
    except (ValidationError, DatabaseError):
        # Re-raise these specific exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during signup for {request.email}: {e}")
        raise DatabaseError("Failed to create user")

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.
    
    Args:
        request: User login credentials
        db: Database session
        
    Returns:
        Access token and token type
        
    Raises:
        AuthenticationError: If credentials are invalid
        DatabaseError: If database operation fails
    """
    try:
        token = service.authenticate_user(request, db)
        logger.info(f"User login successful: {request.email}")
        return {"access_token": token, "token_type": "bearer"}
        
    except (AuthenticationError, DatabaseError):
        # Re-raise these specific exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login for {request.email}: {e}")
        raise DatabaseError("Authentication failed due to system error")
