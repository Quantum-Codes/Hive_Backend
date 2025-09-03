"""
Scraper Models and Data Structures

This module contains data models and schemas for web scraping functionality.
It defines the structure for scraped content, scraping requests, and results.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, HttpUrl, Field


class ContentType(str, Enum):
    """Types of content that can be scraped."""
    NEWS_ARTICLE = "news_article"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    FACT_CHECK = "fact_check"
    ACADEMIC_PAPER = "academic_paper"
    FORUM_POST = "forum_post"
    OTHER = "other"


class ScrapingStatus(str, Enum):
    """Status of scraping operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"


class ScrapedContent(BaseModel):
    """Model for scraped content from web sources."""
    
    id: Optional[str] = Field(None, description="Unique identifier for scraped content")
    url: HttpUrl = Field(..., description="Source URL of the content")
    title: Optional[str] = Field(None, description="Title of the content")
    content: Optional[str] = Field(None, description="Main text content")
    author: Optional[str] = Field(None, description="Author of the content")
    publish_date: Optional[datetime] = Field(None, description="Publication date")
    content_type: ContentType = Field(ContentType.OTHER, description="Type of content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    scraped_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when content was scraped")
    language: Optional[str] = Field(None, description="Language of the content")
    word_count: Optional[int] = Field(None, description="Number of words in content")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScrapingRequest(BaseModel):
    """Model for scraping requests."""
    
    id: Optional[str] = Field(None, description="Unique request identifier")
    urls: List[HttpUrl] = Field(..., description="URLs to scrape")
    content_types: List[ContentType] = Field(default=[ContentType.OTHER], description="Expected content types")
    max_depth: int = Field(1, ge=1, le=5, description="Maximum crawling depth")
    follow_links: bool = Field(False, description="Whether to follow internal links")
    user_agent: Optional[str] = Field(None, description="Custom user agent string")
    timeout: int = Field(30, ge=5, le=300, description="Request timeout in seconds")
    rate_limit_delay: float = Field(1.0, ge=0.1, le=10.0, description="Delay between requests")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Request creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScrapingResult(BaseModel):
    """Model for scraping operation results."""
    
    request_id: str = Field(..., description="Associated request ID")
    status: ScrapingStatus = Field(..., description="Scraping operation status")
    scraped_content: List[ScrapedContent] = Field(default=[], description="Successfully scraped content")
    failed_urls: List[HttpUrl] = Field(default=[], description="URLs that failed to scrape")
    error_messages: List[str] = Field(default=[], description="Error messages from failed attempts")
    total_urls: int = Field(0, description="Total number of URLs processed")
    successful_scrapes: int = Field(0, description="Number of successful scrapes")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Scraping start time")
    end_time: Optional[datetime] = Field(None, description="Scraping completion time")
    execution_time: Optional[float] = Field(None, description="Total execution time in seconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WebsiteInfo(BaseModel):
    """Model for website information and scraping configuration."""
    
    domain: str = Field(..., description="Website domain")
    name: Optional[str] = Field(None, description="Website name")
    base_url: HttpUrl = Field(..., description="Base URL of the website")
    content_selectors: Dict[str, str] = Field(default_factory=dict, description="CSS selectors for content extraction")
    rate_limit: float = Field(1.0, description="Rate limit in requests per second")
    user_agent: Optional[str] = Field(None, description="Preferred user agent")
    headers: Dict[str, str] = Field(default_factory=dict, description="Additional headers")
    is_javascript_required: bool = Field(False, description="Whether JavaScript rendering is required")
    reliability_score: float = Field(1.0, ge=0.0, le=1.0, description="Reliability score of the source")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last configuration update")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScrapingError(BaseModel):
    """Model for scraping errors."""
    
    url: HttpUrl = Field(..., description="URL that caused the error")
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Detailed error message")
    status_code: Optional[int] = Field(None, description="HTTP status code if applicable")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    retry_count: int = Field(0, description="Number of retry attempts")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Database models (if using SQLAlchemy or similar ORM)
class ScrapedContentDB:
    """Database model for scraped content (ORM representation)."""
    pass


class ScrapingRequestDB:
    """Database model for scraping requests (ORM representation)."""
    pass


class WebsiteInfoDB:
    """Database model for website information (ORM representation)."""
    pass


# Utility functions for model validation and conversion
def validate_url_list(urls: List[str]) -> List[HttpUrl]:
    """Validate and convert string URLs to HttpUrl objects."""
    validated_urls = []
    for url in urls:
        try:
            validated_urls.append(HttpUrl(url))
        except ValueError as e:
            raise ValueError(f"Invalid URL format: {url} - {e}")
    return validated_urls


def calculate_execution_time(start_time: datetime, end_time: datetime) -> float:
    """Calculate execution time in seconds between two datetime objects."""
    return (end_time - start_time).total_seconds()


def create_scraping_summary(result: ScrapingResult) -> Dict[str, Any]:
    """Create a summary of scraping results."""
    success_rate = (result.successful_scrapes / result.total_urls * 100) if result.total_urls > 0 else 0
    
    return {
        "request_id": result.request_id,
        "status": result.status,
        "total_urls": result.total_urls,
        "successful_scrapes": result.successful_scrapes,
        "failed_scrapes": len(result.failed_urls),
        "success_rate": round(success_rate, 2),
        "execution_time": result.execution_time,
        "average_content_length": sum(len(content.content or "") for content in result.scraped_content) / len(result.scraped_content) if result.scraped_content else 0
    }
