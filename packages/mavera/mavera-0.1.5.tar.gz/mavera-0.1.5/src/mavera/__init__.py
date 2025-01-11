# src/mavera/__init__.py
from .client import Mavera
from .models import ChatRequest, ChatResponse
from .exceptions import MaveraError, AuthenticationError, PersonaNotFoundError

__all__ = ['Mavera', 'MaveraError', 'AuthenticationError', 'PersonaNotFoundError']


__version__ = "0.1.0"