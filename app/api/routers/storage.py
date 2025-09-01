from fastapi import APIRouter, File, UploadFile, HTTPException
from models import databases
import uuid

supabase = databases.supabase
router = APIRouter(prefix="/storage", tags=["Storage"])

# Upload profile picture
@router.post("/upload/profile-pic")
async def upload_profile_pic(file: UploadFile = File(...)):
    try:
        file_ext = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"

        # Upload to the user-profile-pics bucket
        supabase.storage.from_("user-profile-pics").upload(file_name, file.file)

        # Public URL
        url = f"{supabase.storage.from_('user-profile-pics').get_public_url(file_name)}"
        return {"profile_pic_url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Upload user media (images, videos, etc.)
@router.post("/upload/media")
async def upload_media(file: UploadFile = File(...)):
    try:
        file_ext = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"

        # Upload to the user-media bucket
        supabase.storage.from_("user-media").upload(file_name, file.file)

        # Public URL
        url = f"{supabase.storage.from_('user-media').get_public_url(file_name)}"
        return {"media_url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
