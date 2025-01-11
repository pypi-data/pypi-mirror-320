from http import HTTPStatus
from typing import Optional, Any


class BaseException(Exception):
    """Base exception class for all custom exceptions"""

    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary format"""
        error_dict = {"message": self.message, "status_code": self.status_code}
        if self.error_code:
            error_dict["error_code"] = self.error_code
        if self.details:
            error_dict["details"] = self.details
        return error_dict


class DuplicateValueException(BaseException):
    """Raised when a duplicate value is found where uniqueness is required"""

    def __init__(
        self,
        message: str = "Duplicate value found",
        error_code: str = "DUPLICATE_VALUE",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.CONFLICT,
            error_code=error_code,
            details=details,
        )


class NotFoundException(BaseException):
    """Raised when a requested resource is not found"""

    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.NOT_FOUND,
            error_code=error_code,
            details=details,
        )


class ValidationException(BaseException):
    """Raised when data validation fails"""

    def __init__(
        self,
        message: str = "Validation error",
        error_code: str = "VALIDATION_ERROR",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code=error_code,
            details=details,
        )


class UnauthorizedException(BaseException):
    """Raised when authentication fails or user lacks required permissions"""

    def __init__(
        self,
        message: str = "Unauthorized access",
        error_code: str = "UNAUTHORIZED",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED,
            error_code=error_code,
            details=details,
        )


class ConfigurationException(BaseException):
    """Raised when there are configuration related errors"""

    def __init__(
        self,
        message: str = "Configuration error",
        error_code: str = "CONFIG_ERROR",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code=error_code,
            details=details,
        )


class DatabaseException(BaseException):
    """Raised when database operations fail"""

    def __init__(
        self,
        message: str = "Database operation failed",
        error_code: str = "DB_ERROR",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code=error_code,
            details=details,
        )


class ExternalServiceException(BaseException):
    """Raised when external service calls fail"""

    def __init__(
        self,
        message: str = "External service error",
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_GATEWAY,
            error_code=error_code,
            details=details,
        )


class InvalidInputException(BaseException):
    """Raised when input data is invalid"""

    def __init__(
        self,
        message: str = "Invalid input",
        error_code: str = "INVALID_INPUT",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code=error_code,
            details=details,
        )


class BusinessLogicException(BaseException):
    """Raised when business logic rules are violated"""

    def __init__(
        self,
        message: str = "Business logic violation",
        error_code: str = "BUSINESS_LOGIC_ERROR",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            error_code=error_code,
            details=details,
        )


class FileOperationException(BaseException):
    """Raised when file operations fail"""

    def __init__(
        self,
        message: str = "File operation failed",
        error_code: str = "FILE_ERROR",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code=error_code,
            details=details,
        )


class ConnectionException(BaseException):
    """Raised when network or service connection fails"""

    def __init__(
        self,
        message: str = "Connection failed",
        error_code: str = "CONNECTION_ERROR",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            error_code=error_code,
            details=details,
        )


class RateLimitException(BaseException):
    """Raised when rate limits are exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        error_code: str = "RATE_LIMIT_EXCEEDED",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            error_code=error_code,
            details=details,
        )


class TimeoutException(BaseException):
    """Raised when operations timeout"""

    def __init__(
        self,
        message: str = "Operation timed out",
        error_code: str = "TIMEOUT",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.GATEWAY_TIMEOUT,
            error_code=error_code,
            details=details,
        )


class ForbiddenException(BaseException):
    """Raised when user is authenticated but lacks permission to access a resource"""

    def __init__(
        self,
        message: str = "Access forbidden",
        error_code: str = "FORBIDDEN",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.FORBIDDEN,
            error_code=error_code,
            details=details,
        )
