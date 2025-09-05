from fastapi import APIRouter, File, UploadFile, HTTPException,Depends
from app.core.supabase import get_supabase_client
from app.api.routers.user_auth import get_current_user
import uuid

supabase = get_supabase_client()
router = APIRouter(prefix="/storage", tags=["Storage"])


# Upload profile picture
@router.post("/upload/profile-pic")
async def upload_profile_pic(
    file: UploadFile = File(...),
    user : dict = Depends(get_current_user)  # however you get the logged-in user id
):
    user_id = user["uid"]
    try:
        file_ext = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"

        # Upload to the user-profile-pics bucket
        supabase.storage.from_("user-profile-pics").upload(file_name, file.file)

        # Public URL
        url = supabase.storage.from_("user-profile-pics").get_public_url(file_name)

        # ✅ Update user's table with new profile pic
        supabase.table("users").update({"profile_pic_url": url}).eq("uid", user_id).execute()

        return {"profile_pic_url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/media")
async def upload_media(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)  # get logged in user row
):
    try:
        file_ext = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"

        # Upload to the user-media bucket
        supabase.storage.from_("user-media").upload(file_name, file.file)

        # Public URL
        url = supabase.storage.from_("user-media").get_public_url(file_name)

        # ✅ Insert into posts table (only owner_id and media_url exist)
        supabase.table("posts").insert({
            "owner_id": user["uid"],   # use uid from users table
            "media_url": url
        }).execute()

        return {"media_url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
