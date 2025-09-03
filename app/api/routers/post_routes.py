from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.models import schemas
from app.utils.supabase_client import get_supabase_client
from . import user_auth
import datetime
from typing import List

router = APIRouter(
    prefix='/post',
    tags=["Posts"]
)

supabase = get_supabase_client()

#  Upload media + create a post
@router.post('/', response_model=schemas.ShowPost)
def create_post(
    post: schemas.Post,
    user = Depends(user_auth.get_current_user)
):
    new_post = {
        'pid': post.pid,
        'owner_id': user['uid'],
        'content': post.content,
        'media_url': post.media_url,  # frontend must provide this from /storage/upload/media
        'created_at': datetime.utcnow(),
        'likes': 0,
        'dislikes': 0,
        'is_verified': False,
    }

    res = supabase.table('posts').insert(new_post).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail='Error creating the post')

    return {
        "pid": res.data[0]["pid"],
        "content": res.data[0]["content"],
        "media_url": res.data[0]["media_url"],
        "author_name": user["name"],
        "author_display_name": user.get("displayName"),
        "author_avatar": user.get("avatar"),
        "likes": 0,
        "dislikes": 0,
        "score": 0,
        "comments_count": 0,
        "is_verified": False,
        "moderation_status": "pending",
        "created_at": res.data[0]["created_at"],
    }

#  Get all posts
@router.get('/', response_model=List[schemas.ShowPost])
def get_all_posts():
    res = supabase.table('posts').select('*').execute()
    return res.data


#  Get current user's posts
@router.get('/me', response_model=List[schemas.ShowPost])
def my_posts(user = Depends(user_auth.get_current_user)):
    res = supabase.table('posts').select('*').eq('owner_id', user['uid']).execute()
    return res.data


#  Get single post by pid
@router.get('/{pid}', response_model=schemas.ShowPost)
def get_single_post(pid: str):
    res = supabase.table('posts').select('*').eq('pid', pid).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Post not found")
    return res.data


#  Delete post
@router.delete('/{pid}')
def delete_post(pid: str, user = Depends(user_auth.get_current_user)):
    res = supabase.table('posts').select('*').eq('pid', pid).single().execute()

    if not res.data or res.data['owner_id'] != user['uid']:
        raise HTTPException(status_code=403, detail='Not authorized')

    supabase.table('posts').delete().eq('pid', pid).execute()
    return {"message": f"Post with id {pid} deleted successfully"}

@router.put('/{pid}', response_model=schemas.ShowPost)
def update_post(
    pid: str,
    post: schemas.Post,
    user = Depends(user_auth.get_current_user)
):
    res = supabase.table('posts').select('*').eq('pid', pid).single().execute()
    if not res.data or res.data['owner_id'] != user['uid']:
        raise HTTPException(status_code=403, detail='Not authorized')

    updated = supabase.table('posts').update({
        'content': post.content,
        'media_url': post.media_url or res.data['media_url']
    }).eq('pid', pid).execute()

    return updated.data[0]
