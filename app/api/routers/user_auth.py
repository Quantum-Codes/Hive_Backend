import app
from fastapi import Request, APIRouter,Depends,HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import RedirectResponse
from typing import List,Optional
from app.core.config import APISettings
from app.utils.supabase_client import get_supabase_client
from datetime import datetime,timedelta

supabase = get_supabase_client()
REDIRECT_URL = APISettings().callback_url

# this tells FastAPI to look for "Authorization: Bearer <token>"
bearer_scheme = HTTPBearer()
#TODO make the data base file for the corresponding shcemas and make the functions filled by tommorow and do the rest things  also  have a  look into using hte multiple subroutes for the single route 


router = APIRouter(
    prefix= '/user',
    tags=['Users']
)

@router.get("/login")
async def login_with_google():
    try:
        oauth_response = supabase.auth.sign_in_with_oauth(
            {"provider": "google", "options": {"redirect_to": REDIRECT_URL}}
        )
        return RedirectResponse(url=oauth_response.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/callback")
async def auth_callback(request: Request):
    """
    this receives the authorization code and exchanges it for a user session.
    """
    try:
        code = request.query_params.get("code")

        if not code:
            raise HTTPException(status_code=400, detail="Authorization code not found in request.")

        session_response = supabase.auth.exchange_code_for_session(
            {"auth_code": code, "code_verifier": None}
        )

        if session_response.error:
            raise HTTPException(
                status_code=session_response.error.status,
                detail=session_response.error.message,
            )
        
        user_data = session_response.user.model_dump()

        user_id = user_data.get("id")
        email = user_data.get("email")
        created_at = user_data.get("created_at")
        
        full_name = user_data.get("user_metadata", {}).get("full_name", "")

        username = email.split("@")[0] if email else ""

        supabase.table("users").upsert({
            "uid": user_id,
            "email": email,
            "full_name": full_name,
            "username": username,
            'created_at' : created_at,
            'bio' : "Hey there ! I am using HIVE right now"
            
            ## TODO profile_pic_url

        }).execute()

        
        return {"message": "User successfully authenticated!", "user_data": user_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        token = credentials.credentials
        user_from_jwt = supabase.auth.get_user_from_jwt(token)
        if not user_from_jwt:
            raise HTTPException(status_code=401, detail="Not logged in")
        user_id = user_from_jwt.id
        profile_response = supabase.table("users").select("*").eq("uid", user_id).execute()
        if not profile_response.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        return profile_response.data[0]
    except Exception as e:
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