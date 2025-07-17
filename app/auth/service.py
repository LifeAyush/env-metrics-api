from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import User
from app.schemas import SignupRequest, LoginRequest
from app.auth.utils import hash_password, verify_password, create_access_token
from app.exceptions import DatabaseError, AuthenticationError, ValidationError
from app.logger import setup_logger

logger = setup_logger(__name__)

def get_user_by_email(email: str, db: Session) -> User | None:
    """
    Get user by email address.
    
    Args:
        email: User's email address
        db: Database session
        
    Returns:
        User object if found, None otherwise
    """
    try:
        user = db.query(User).filter(User.email == email).first()
        logger.debug(f"User lookup for email: {email}, found: {user is not None}")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching user by email {email}: {e}")
        raise DatabaseError("Failed to fetch user")
    except Exception as e:
        logger.error(f"Unexpected error while fetching user by email {email}: {e}")
        raise DatabaseError("Unexpected error occurred")

def create_user(request: SignupRequest, db: Session) -> User:
    """
    Create a new user.
    
    Args:
        request: Signup request data
        db: Database session
        
    Returns:
        Created user object
        
    Raises:
        DatabaseError: If database operation fails
        ValidationError: If user data is invalid
    """
    try:
        # Validate email format (basic check)
        if not request.email or '@' not in request.email:
            raise ValidationError("Invalid email format")
        
        # Validate password strength
        if len(request.password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        new_user = User(
            email=request.email,
            hashed_password=hash_password(request.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User created successfully: {request.email}")
        return new_user
        
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating user {request.email}: {e}")
        db.rollback()
        raise DatabaseError("Failed to create user")
    except ValidationError:
        # Re-raise validation errors
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating user {request.email}: {e}")
        db.rollback()
        raise DatabaseError("Unexpected error occurred")

def authenticate_user(request: LoginRequest, db: Session) -> str | None:
    """
    Authenticate user and return JWT token.
    
    Args:
        request: Login request data
        db: Database session
        
    Returns:
        JWT token if authentication successful, None otherwise
        
    Raises:
        DatabaseError: If database operation fails
        AuthenticationError: If authentication fails
    """
    try:
        user = get_user_by_email(request.email, db)
        
        if not user:
            logger.warning(f"Login attempt with non-existent email: {request.email}")
            raise AuthenticationError("Invalid credentials")
        
        if not verify_password(request.password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {request.email}")
            raise AuthenticationError("Invalid credentials")
        
        token = create_access_token({"sub": user.email})
        logger.info(f"Successful login for user: {request.email}")
        return token
        
    except (DatabaseError, AuthenticationError):
        # Re-raise these specific exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during authentication for {request.email}: {e}")
        raise DatabaseError("Authentication failed due to system error")
