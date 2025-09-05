from fastapi import Request, APIRouter,Depends,HTTPException,Header,Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import RedirectResponse
from typing import Optional
from app.core.config import APISettings
from app.core.supabase import get_supabase_client
from app.core.config import settings

supabase = get_supabase_client()
REDIRECT_URL = APISettings().callback_url

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


def decode_supabase_token(token: str):
    user = supabase.auth.get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


@router.post("/defaults")
async def login(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Authorization header missing or invalid")

    token = authorization.split(" ")[1]
    user_from_jwt = decode_supabase_token(token)
    uid = user_from_jwt.id
    if not uid:
        raise HTTPException(status_code=400, detail="UID not found in token")

    auth_response = supabase.auth.api.get_user(uid)
    if not auth_response.user:
        raise HTTPException(status_code=404, detail="UID not found in authentication table")

    user_response = supabase.table("users").select("*").eq("uid", uid).execute()
    if user_response.data:
        return {"message": "User already exists", "uid": uid}

    # Extract info from token
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
        "profile_url": " "
    }).execute()

    if insert_response.error:
        raise HTTPException(status_code=500, detail=insert_response.error.message)

    return {"message": "User created successfully", "uid": uid}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        token = credentials.credentials
        user_from_jwt = supabase.auth.get_user(token)
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