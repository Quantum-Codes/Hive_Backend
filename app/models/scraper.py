from pydantic import BaseModel
from typing import List
from datetime import datetime


class ScraperResult(BaseModel):
    source: str
    date_published: datetime
    title: str
    article_summary: str
    content: List[str]