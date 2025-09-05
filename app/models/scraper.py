from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ScraperResult(BaseModel):
    source: str
    date_published: Optional[datetime] = None
    title: str
    article_summary: Optional[str] = None
    content: List[str]