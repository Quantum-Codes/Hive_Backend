<<<<<<< HEAD
import app
from fastapi import Request, APIRouter,Depends,HTTPException, RedirectResponse
import app
from fastapi import Request, APIRouter,Depends,HTTPException, RedirectResponse
from typing import List,Optional
from app.core.config import APISettings
from app.utils.supabase_client import get_supabase_client
from app.core.config import APISettings
from app.utils.supabase_client import get_supabase_client
=======
from fastapi import APIRouter,Depends,HTTPException,Request
from typing import List,Optional
from app.models import schemas,databases
from fastapi.security import OAuth2PasswordBearer
from app.core import security
>>>>>>> 811137cb9e2efe8703e8c2b7652fcac5194fd146
from datetime import datetime,timedelta

supabase = get_supabase_client()
REDIRECT_URL = APISettings.callback_url
supabase = get_supabase_client()
REDIRECT_URL = APISettings.callback_url

# this tells FastAPI to look for "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
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




# get currently logged in user (from JWT token)
@router.get("/users/me")
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

<<<<<<< HEAD
=======

# refresh access token (optional, if using refresh tokens)

# refresh
@router.post("/refresh")
def refresh_token():
    #payload = Oauth_token.decode_access_token(token)
    #new_token = Oauth_token.create_access_token(data={"sub": payload.get("sub")}, expires_delta=timedelta(minutes=30))
    return {"access_token": "Token refreshed", "token_type": "bearer"}

 
>>>>>>> 811137cb9e2efe8703e8c2b7652fcac5194fd146
