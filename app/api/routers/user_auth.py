#<<<<<<< HEAD
import app
from fastapi import Request,  APIRouter,Depends,HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import List,Optional
from app.core.config import APISettings
from app.utils.supabase_client import get_supabase_client
#<<<<<<< HEAD:app/api/routers/userAuthentication.py
from app.core.config import APISettings

from app.utils.supabase_client import get_supabase_client
#=======
from fastapi import APIRouter,Depends,HTTPException,Request
from typing import List,Optional
from app.models import schemas,databases
from fastapi.security import OAuth2PasswordBearer
#>>>>>>> 811137cb9e2efe8703e8c2b7652fcac5194fd146
#=======
#>>>>>>> f292d0c3df85fd1be1e3f39d0a6e845edfbb0150:app/api/routers/user_auth.py
from datetime import datetime,timedelta

supabase = get_supabase_client()
api_settings = APISettings()
REDIRECT_URL = api_settings.callback_url

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
        
        return {"message": "User successfully authenticated!", "user_data": user_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/me")
#<<<<<<< HEAD:app/api/routers/userAuthentication.py
def get_current_user(request : Request):
    email = request.cookies.get('email')
    result = supabase.table("users").select("*").eq("email", email).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return result.data[0]




# logout (invalidate session)
@router.post("/logout")
def logout():
    return {"msg": "Logout successful (JWT will expire automatically)"}

#<<<<<<< HEAD
#=======

# refresh access token (optional, if using refresh tokens)

# refresh
@router.post("/refresh")
def refresh_token():
    #payload = Oauth_token.decode_access_token(token)
    #new_token = Oauth_token.create_access_token(data={"sub": payload.get("sub")}, expires_delta=timedelta(minutes=30))
    return {"access_token": "Token refreshed", "token_type": "bearer"}

 
#>>>>>>> 811137cb9e2efe8703e8c2b7652fcac5194fd146
#=======
def get_current_logged_in_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):

    try:
        token = credentials.credentials
        user_from_jwt = supabase.auth.get_user_from_jwt(token)
        
        if not user_from_jwt:
            raise HTTPException(status_code=401, detail="Not logged in")
            
        user_id = user_from_jwt.id
        profile_response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not profile_response.data:
            # If a user exists in auth.users but has no entry in the users table.
            raise HTTPException(status_code=404, detail="User profile not found")
            
        return {"message": "User is authenticated.", "user": profile_response.data[0]}
        
    except Exception as e:
        # Catch any errors during the process and return a 401 Unauthorized response.
        raise HTTPException(status_code=401, detail=f"Invalid token or user not found: {str(e)}")


@router.get("/logout")
def logout_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        supabase.auth.sign_out() # uses Authorization header
        return {"message": "User successfully logged out."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#>>>>>>> f292d0c3df85fd1be1e3f39d0a6e845edfbb0150:app/api/routers/user_auth.py
