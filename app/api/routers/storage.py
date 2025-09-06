from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.core.supabase import get_supabase_client
from app.api.routers.auth import get_current_user
import uuid

supabase = get_supabase_client()
router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post("/upload/profile-pic")
async def upload_profile_pic(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    user_id = user["uid"]
    try:
        file_ext = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"

        file_bytes = await file.read()
        supabase.storage.from_("user-profile-pics").upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )

        # Public URL
        url = supabase.storage.from_("user-profile-pics").get_public_url(file_name)

        # Update user's profile picture
        update_response = (
            supabase.table("users")
            .update({"profile_pic_url": url})
            .eq("uid", user_id)
            .execute()
        )

        if update_response.error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update profile picture: {update_response.error.message}",
            )

        return {"profile_pic_url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
