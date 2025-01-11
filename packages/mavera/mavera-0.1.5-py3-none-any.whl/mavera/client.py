from typing import Dict, Any
import httpx
from .models import ChatRequest, ChatResponse
from .exceptions import MaveraError, AuthenticationError
from .database import PersonaDB, PersonaNotFoundError
import logging

class Mavera:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.mavera.io/v1",
        timeout: float = 180.0  # Default timeout set to 180 seconds
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client = httpx.Client(
            headers={
                "X-Mavera-API-Key": api_key,
                "Content-Type": "application/json"
            },
            timeout=httpx.Timeout(self.timeout)  # Set timeout for the client
        )

        # Configure logging for the SDK
        logging.basicConfig(level=logging.WARNING)  # Default to WARNING
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

    def chat(self, persona: str, message: str) -> Dict[str, Any]:
        """
        Send a chat message to a specific persona.
        """
        try:
            response = self._client.post(
                f"{self.base_url}/chat",
                json={
                    "persona": persona,
                    "message": message
                }
            )
            
            if response.status_code == 404:
                error_detail = response.json().get("detail", "Persona not found")
                raise PersonaNotFoundError(error_detail)
                
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                error_detail = e.response.json().get("detail", "Persona not found")
                raise PersonaNotFoundError(error_detail)
            raise MaveraError(f"API request failed: {str(e)}")

    def research(self, research_query: str) -> Dict[str, Any]:
        """
        Send a research query to the Mavera research endpoint and return the synthesized response.
        """
        try:
            response = self._client.post(
                f"{self.base_url}/research",
                json={
                    "research_query": research_query
                }
            )
            
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API Key")
            raise MaveraError(f"API request failed: {str(e)}")
