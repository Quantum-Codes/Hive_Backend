from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.models import post, rag
from app.core.supabase import get_supabase_client
from . import auth
from datetime import datetime
from typing import List
from redis import Redis
from rq import Queue
from app.services.verification_service import verify_post


router = APIRouter(
    prefix='/post',
    tags=["Posts"]
)


redis_conn = Redis(host='localhost', port=6379)
task_queue = Queue(connection=redis_conn)

supabase = get_supabase_client()


#  Upload media + create a post
@router.post('/', response_model=post.ShowPost)
def create_post(
    post_data: post.Post,
    user = Depends(auth.get_current_user)
):
    new_post = {
        'owner_id': user['uid'],
        'content': post_data.content,
        'created_at': datetime.utcnow().isoformat(),
        'likes': 0,
        'dislikes': 0,
        "verification_status": rag.RagResponse.UNVERIFIED,
    }

    res = supabase.table('posts').insert(new_post).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail='Error creating the post')
    
    # Queue verification task with error handling
    try:
        task_queue.enqueue(
            verify_post, 
            post.PostContentRequest(pid=res.data[0]["pid"], content=post_data.content),
            job_timeout='10m'  # Set timeout for verification task
        )
    except Exception as e:
        # Log the error but don't fail the post creation
        print(f"Failed to queue verification task for post {res.data[0]['pid']}: {str(e)}")
        # Optionally, you could set verification status to error here
        # supabase.table('posts').update({"verification_status": "error"}).eq("pid", res.data[0]["pid"]).execute()
    return {
        "pid": res.data[0]["pid"],
        "content": res.data[0]["content"],
        "owner_id": user["uid"],
        "author_name": user.get("username"),
        "likes": 0,
        "dislikes": 0,
        "score": 0,
        "comments_count": 0,
        "verification_status": rag.RagResponse.UNVERIFIED,
        "created_at": res.data[0]["created_at"],
    }


def insert_author_name(posts: List[dict]) -> List[dict]:
    for post in posts:
        user_res = supabase.table('users').select('username, full_name, profile_pic_url').eq('uid', post['owner_id']).single().execute()
        if user_res.data:
            post['author_name'] = user_res.data.get('username')
            post['author_display_name'] = user_res.data.get('full_name')
            post['author_avatar'] = user_res.data.get('profile_pic_url')
        else:
            post['author_name'] = 'Unknown'
            post['author_display_name'] = None
            post['author_avatar'] = None
    
    return posts

#  Get all posts
@router.get('/', response_model=List[post.ShowPost])
def get_all_posts():
    res = supabase.table('posts').select('*').execute()
    return insert_author_name(res.data)


#  Get user's posts
@router.get('/users/{uid}/posts', response_model=List[post.ShowPost])
def user_posts(uid: str):
    res = supabase.table('posts').select('*').eq('owner_id', uid).execute()
    return insert_author_name(res.data)


#  Get single post by pid
@router.get('/{pid}', response_model=post.ShowPost)
def get_single_post(pid: str):
    res = supabase.table('posts').select('*').eq('pid', pid).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Post not found")
    return insert_author_name([res.data])[0]


#  Delete post
@router.delete('/{pid}')
def delete_post(pid: str, user = Depends(auth.get_current_user)):
    res = supabase.table('posts').select('*').eq('pid', pid).single().execute()

    if not res.data or res.data['owner_id'] != user['uid']:
        raise HTTPException(status_code=403, detail='Not authorized')

    supabase.table('posts').delete().eq('pid', pid).execute()
    return {"message": f"Post with id {pid} deleted successfully"}

@router.put('/{pid}', response_model=post.ShowPost)
def update_post(
    pid: str,
    post_content: str,
    user = Depends(auth.get_current_user)
):
    res = supabase.table('posts').select('*').eq('pid', pid).single().execute()
    if not res.data or res.data['owner_id'] != user['uid']:
        raise HTTPException(status_code=403, detail='Not authorized')

    updated = supabase.table('posts').update({
        'content': post_content,
    }).eq('pid', pid).execute()

    return insert_author_name([updated.data[0]])[0]



@router.post("/{pid}/like")
def like_post(pid: str, user=Depends(auth.get_current_user)):
    res = supabase.table("posts").select("likes").eq("pid", pid).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Post not found")

    new_likes = res.data["likes"] + 1
    supabase.table("posts").update({"likes": new_likes}).eq("pid", pid).execute()
    return {"pid": pid, "likes": new_likes}


@router.post("/{pid}/dislike")
def dislike_post(pid: str, user=Depends(auth.get_current_user)):
    res = supabase.table("posts").select("dislikes").eq("pid", pid).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Post not found")

    new_dislikes = res.data["dislikes"] + 1
    supabase.table("posts").update({"dislikes": new_dislikes}).eq("pid", pid).execute()
    return {"pid": pid, "dislikes": new_dislikes}
