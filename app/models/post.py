from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from typing import List



class Post(BaseModel):
    pid: str
    owner_id: str
    content: str
    avatar_user : Optional[str] =None
    created_at: datetime = datetime.now(timezone.utc)
    #updated_at: Optional[datetime] = None
    likes: int = 0
    dislikes : int = 0
    is_verified: bool = False

    class Config:
        orm_mode = True

class PostContentRequest(BaseModel):
    pid: str
    content: str

class PostVerificationRequest(BaseModel):
    pid: str
    content: str
    context: List[str]

class ShowPost(BaseModel):
    pid : str
    content: str
    
    # Author info (subset of User)
    author_name: str
    author_display_name: Optional[str] = None
    author_avatar: Optional[str] = None

    # Engagement
    likes: int = 0
    dislikes: int = 0
    score: int = 0
    comments_count: int = 0
    is_liked_by_current_user: bool = False
    #is_saved_by_current_user: bool = False --same as the edit case 

    # Context
    community_id: Optional[str] = None
    community_name: Optional[str] = None
    tags: Optional[List[str]] = []

    # Verification / Moderation
    is_verified: bool = False
    moderation_status: str = "pending"

    # Timestamps
    created_at: datetime
    #updated_at: Optional[datetime] = None
    #edited: bool = False --For now we are not gonna have any edit button in the post 

    class Config:
        orm_mode = True




