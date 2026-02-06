"""
Request/Response Schemas

Pydantic models for API request and response validation.
"""
from pydantic import BaseModel, Field, validator


class ChatRequest(BaseModel):
    """Schema for chat request"""
    query: str = Field(..., description="User query for the dairy farming assistant")
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        if len(v) > 1000:
            raise ValueError('Query too long (max 1000 characters)')
        return v.strip()


class ChatResponse(BaseModel):
    """Schema for chat response"""
    answer: str = Field(..., description="Assistant's response")


class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")


class RebuildResponse(BaseModel):
    """Schema for rebuild index response"""
    message: str = Field(..., description="Rebuild confirmation message")


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str = Field(..., description="Error message")
