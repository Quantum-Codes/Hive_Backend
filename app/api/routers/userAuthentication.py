from fastapi import APIRouter,Depends,HTTPException,Request
from typing import List,Optional
from app.models import schemas,databases
from fastapi.security import OAuth2PasswordBearer
from app.core import security
from datetime import datetime,timedelta

verify_password = security.veriyPassword
supabase = databases.supabase
hash_password = security.hashPassword


# this tells FastAPI to look for "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
#TODO make the data base file for the corresponding shcemas and make the functions filled by tommorow and do the rest things  also  have a  look into using hte multiple subroutes for the single route 


router = APIRouter(
    prefix= '/user',
    tags=['Users']
)

# signup (register new user)
@router.post("/signup",response_model=schemas.ShowUser)
def signup(user: schemas.SignUp):
    existing_user =  supabase.table('users').select('*').eq('email',user.email).execute()
    existing_userName = supabase.table('users').select('*').eq('username',user.displayName).execute()
    if existing_user.data :
            raise HTTPException(status_code=400, detail="Email already registered")   
    if existing_userName.data : 
            raise HTTPException(status_code=400, detail="Username already exists ")   

    hashed_pw = hash_password(user.password)
    response = supabase.table("users").insert({
        "full_name": user.name,
        "email": user.email,
        "hashed_password": hashed_pw,
        'username' : user.displayName,
        'bio' : user.bio,
        'created_at' : datetime.now().isoformat(),
        'profile_pic_url' : user.avatar
    }).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Error creating user")
    
    return response.data[0]


# login (sign in with email + password)
@router.post("/login")
def login(user: schemas.Login):
    result = supabase.table("users").select("*").eq("email", user.email).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    db_user = result.data[0]
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = Oauth_token.create_access_token(
        data={"sub": db_user["email"]},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": token, "token_type": "bearer"}





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


# refresh access token (optional, if using refresh tokens)

# refresh
@router.post("/refresh")
def refresh_token():
    #payload = Oauth_token.decode_access_token(token)
    #new_token = Oauth_token.create_access_token(data={"sub": payload.get("sub")}, expires_delta=timedelta(minutes=30))
    return {"access_token": "Token refreshed", "token_type": "bearer"}

 