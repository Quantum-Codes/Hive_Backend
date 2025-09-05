from fastapi import Request, APIRouter,Depends,HTTPException,Header,Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import RedirectResponse
from typing import Optional
from app.core.config import APISettings
from app.core.supabase import get_supabase_client
from datetime import datetime,timedelta
from app.core.config import settings
import traceback

supabase = get_supabase_client()

# this tells FastAPI to look for "Authorization: Bearer <token>"
bearer_scheme = HTTPBearer()
#TODO make the data base file for the corresponding shcemas and make the functions filled by tommorow and do the rest things  also  have a  look into using hte multiple subroutes for the single route 


router = APIRouter(
    prefix= '/user',
    tags=['Users']
)



def polished_str(searchTxt : str):
    return searchTxt.strip().lower()

@router.get("/search")
def search_users(name: str = Query(..., description="Search string for username")):
    search_str = polished_str(name)

    if not search_str:
        raise HTTPException(status_code=400, detail="Search string cannot be empty")

    res = supabase.table("users").select("*").ilike("username", f"%{search_str}%").execute()

    if not res.data:
        raise HTTPException(status_code=404, detail="No users found")

    return res.data or []



def decode_supabase_token(token: str):
    """
    Validate Supabase JWT token using Supabase's built-in verification.
    This is more secure than manual JWT decoding.
    """
    try:
        # Use Supabase's built-in JWT verification instead of manual decoding
        user_response = supabase.auth.get_user(token)
        if not user_response:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_response
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")


@router.post("/defaults")
async def login(authorization: Optional[str] = Header(None)):
    """
    Create user profile from JWT token if it doesn't exist.
    This endpoint is called after successful OAuth authentication.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Authorization header missing or invalid")

    token = authorization.split(" ")[1]
    
    try:
        # Use standardized token validation
        user_from_jwt = supabase.auth.get_user(token)
        print(user_from_jwt)
        print(type(user_from_jwt))
        if not user_from_jwt:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        uid = user_from_jwt.user.id
        if not uid:
            raise HTTPException(status_code=400, detail="UID not found in token")

        # Check if user already exists
        user_response = supabase.table("users").select("*").eq("uid", uid).execute()
        if user_response.data:
            return {"message": "User already exists", "uid": uid}

        # Extract user info from JWT
        email = user_from_jwt.email
        full_name = user_from_jwt.user_metadata.get("full_name", "") if user_from_jwt.user_metadata else ""
        username = email.split("@")[0] if email else ""

        # Insert into users table
        insert_response = supabase.table("users").insert({
            "uid": uid,
            "email": email,
            "full_name": full_name,
            "username": username,
            "bio": "Hey there! I am using HIVE right now",
            "profile_pic_url": ""  # Fixed field name consistency
        }).execute()

        if insert_response.error:
            raise HTTPException(status_code=500, detail=insert_response.error.message)

        return {"message": "User created successfully", "uid": uid}
        
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        token = credentials.credentials
        print(token)
        user_from_jwt = supabase.auth.get_user(token)
        if not user_from_jwt:
            raise HTTPException(status_code=401, detail="Not logged in")
        user_id = user_from_jwt.user.id
        profile_response = supabase.table("users").select("*").eq("uid", user_id).execute()
        if not profile_response.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        return profile_response.data[0]
    except Exception as e:
        # print traceback for debugging
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=401, detail=f"Invalid token or user not found: {str(e)}")


@router.get("/users/me")
def get_current_logged_in_user(user=Depends(get_current_user)):
    return {"message": "User is authenticated.", "user": user}


@router.get("/logout")
def logout_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        supabase.auth.sign_out() # uses Authorization header
        return {"message": "User successfully logged out."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))