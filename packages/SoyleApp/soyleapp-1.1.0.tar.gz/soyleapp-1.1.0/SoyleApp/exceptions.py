class SoyleAppError(Exception):
    """Base exception class for SoyleApp"""
    pass

class AuthenticationError(SoyleAppError):
    """Raised when there are authentication issues"""
    pass

class APIError(SoyleAppError):
    """Raised when the API returns an error"""
    pass

class ValidationError(SoyleAppError):
    """Raised when input validation fails"""
    pass

class InsufficientBalanceError(SoyleAppError):
    """Raised when user doesn't have enough balance"""
    pass
