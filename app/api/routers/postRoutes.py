from fastapi import APIRouter,Depends,HTTPException
from models import schemas,databases
from . import userAuthentication
from core import Oauth_token
import datetime
from typing import List
router = APIRouter(
    prefix= '/post',
    tags=["Posts"]
)

supabase = databases.supabase

#To upload a post 
@router.post('/',response_model=schemas.ShowPost)
def createPost(post : schemas.Post,user = Depends(userAuthentication.get_current_user)):
    new_post = {
        'pid' : post.pid,
        'owner_id' : post.owner_id,
        'content' : post.content,
        'media_url' : post.media_url,
        'created_at' : datetime.utcnow(),
        'likes' : 0,
        'dislikes' : 0,
        'is_verified' : False,
    }
    res = supabase.table('posts').insert(new_post).execute()
    if not res.data:
            raise HTTPException(status_code= 400,detail = 'Error creating the post')
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


#To get all post
@router.get('/',response_class=List[schemas.ShowPost])
def getAllPost():
        res = supabase.table('posts').select('*').execute()
        return res
#get current user posts
@router.get('/me',response_class= List[schemas.ShowPost])
def myPosts(user = Depends(userAuthentication.get_current_user)):
    res = supabase.table('posts').select('*').eq(user['uid'],'owner_id').execute()
    return res.data

#get single post based on the uid of post 
@router.get('/{pid}',response_class=schemas.ShowPost)
def get_single_post(pid: str):  
    res = supabase.table('posts').select('*').eq('pid',pid).single().execute()
    if not res.data:
            raise HTTPException(status_code= 404,detail="Post not found")
    
    return res.data


#delete post 
@round.delete('/{pid}')
def delete_post(pid : str,user = Depends(userAuthentication.get_current_user)):
    res = supabase.table('posts').select('*').eq('pid',pid).single().execute()

    if not res.data or res.data['owner_id'] != user['uid']:
        raise HTTPException(status_code= 403,detail= 'Not authorized')
    supabase.table('posts').delete().eq('pid',pid).execute()

    return f'Post with id {pid} deleted succesfully '

#Update post 
@router.put('/{pid}',response_model=schemas.ShowPost)
def update_Post(pid : str, post : schemas.Post,user = Depends(userAuthentication.get_current_user)):
        res= supabase.table('posts').select('*').eq('pid',pid).single().execute()
        if not res.data or res.data['owner_id'] != user['uid']:
                raise HTTPException(status_code= 403,detail= 'Not authorized')
        
        updated = supabase.table('posts').update({'content' : post.content,
                                                  'media_url' : post.media_url
                                                  }).eq('pid',pid).execute()
        
        return updated.data

