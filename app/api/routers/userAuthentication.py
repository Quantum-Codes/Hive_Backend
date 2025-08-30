from fastapi import APIRouter,Depends,HTTPException
from typing import List,Optional
from models import schemas
from fastapi.security import OAuth2PasswordBearer
from models import schemas
from core import security,Oauth_token
from models import databases
from datetime import timedelta

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
    if existing_user.data:
            raise HTTPException(status_code=400, detail="Email already registered")   
    hashed_pw = hash_password(user.password)
    response = supabase.table("users").insert({
        "name": user.name,
        "email": user.email,
        "password": hashed_pw
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
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = Oauth_token.create_access_token(
        data={"sub": db_user["email"]},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": token, "token_type": "bearer"}





# get currently logged in user (from JWT token)
@router.get("/users/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = Oauth_token.decode_access_token(token)
    email: str = payload.get("sub")
    result = supabase.table("users").select("*").eq("email", email).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return result.data[0]




# logout (invalidate session)
@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    return {"msg": "Logout successful (JWT will expire automatically)"}


# refresh access token (optional, if using refresh tokens)

# refresh
@router.post("/refresh")
def refresh_token(token: str = Depends(oauth2_scheme)):
    payload = Oauth_token.decode_access_token(token)
    new_token = Oauth_token.create_access_token(data={"sub": payload.get("sub")}, expires_delta=timedelta(minutes=30))
    return {"access_token": new_token, "token_type": "bearer"}

 