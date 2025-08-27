from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

class RagResponse(str, Enum):    
    """
    The response from the RAG pipeline.
    """
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    PERSONAL_OPINION = "personal_opinion"
    MISINFORMATION = "misinformation"
    FACTUAL_ERROR = "factual_error"
    OTHER = "other"

class RagRequest(BaseModel):
    """
    The request to the RAG pipeline.
    """
    post_id: str = Field(..., description="The ID of the post to be verified")
    post_content: str = Field(..., description="The content of the post to be verified")
    context: List[str] = Field(..., description="The context to be used for verification")