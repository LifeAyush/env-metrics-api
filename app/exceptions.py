from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class MetricsAPIException(HTTPException):
    """Base exception for Metrics API."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra_data = extra_data or {}

class AuthenticationError(MetricsAPIException):
    """Raised when authentication fails."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTH_ERROR"
        )

class AuthorizationError(MetricsAPIException):
    """Raised when user is not authorized to perform an action."""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR"
        )

class ValidationError(MetricsAPIException):
    """Raised when input validation fails."""
    
    def __init__(self, detail: str = "Validation error", field_errors: Optional[Dict[str, str]] = None):
        extra_data = {"field_errors": field_errors} if field_errors else {}
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            extra_data=extra_data
        )

class ResourceNotFoundError(MetricsAPIException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str = "Resource", resource_id: Optional[str] = None):
        detail = f"{resource_type} not found"
        if resource_id:
            detail += f" with id: {resource_id}"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND"
        )

class DatabaseError(MetricsAPIException):
    """Raised when database operations fail."""
    
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR"
        )

class ExternalServiceError(MetricsAPIException):
    """Raised when external service calls fail."""
    
    def __init__(self, service_name: str, detail: str = "External service error"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service_name}: {detail}",
            error_code="EXTERNAL_SERVICE_ERROR"
        ) 