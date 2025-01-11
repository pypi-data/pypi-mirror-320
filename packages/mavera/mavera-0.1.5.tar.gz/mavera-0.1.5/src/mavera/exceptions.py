# src/mavera/exceptions.py
class MaveraError(Exception):
    """Base exception for Mavera errors"""
    pass

class AuthenticationError(MaveraError):
    """Raised when authentication fails"""
    pass

class PersonaNotFoundError(MaveraError):
    """Raised when a persona is not found"""
    pass