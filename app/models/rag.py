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
    source: str = Field(..., description="The source of the content to be verified")
    title: str = Field(..., description="The title of the content to be verified")
    content: List[str] = Field(..., description="The content to be verified")
    article_summary: Optional[str] = Field(..., description="The summary of the content to be verified")
    date_published: Optional[datetime] = Field(..., description="The date the content was published")