# src/mavera/models.py
from pydantic import BaseModel
from typing import Dict, Any, List

class ChatRequest(BaseModel):
    persona: str
    message: str

class ChatCompletionMessage(BaseModel):
    content: str
    role: str

class ChatChoice(BaseModel):
    finish_reason: str
    index: int
    message: ChatCompletionMessage

class ChatResponse(BaseModel):
    persona: str
    response: str  # We'll simplify to just return the message content

class ResearchQueryRequest(BaseModel):
    research_query: str
