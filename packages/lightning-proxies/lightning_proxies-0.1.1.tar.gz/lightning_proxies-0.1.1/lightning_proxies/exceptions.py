class APIError(Exception):
    """Base exception for API errors."""
    pass

class AuthenticationError(APIError):
    """Exception for authentication errors."""
    pass

class InvalidParameterError(APIError):
    """Exception for invalid parameter errors."""
    pass
