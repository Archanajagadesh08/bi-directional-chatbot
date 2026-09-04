from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.auth_schema import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import create_user,authenticate_user,create_access_token, validate_access_token
security= HTTPBearer()
#get the current authenticated
def get_current_user(
        credentials : HTTPAuthorizationCredentials = Depends(security),
        db:Session = Depends(get_db)
):
    token = credentials.credentials
    user = validate_access_token(token,db)
    if not user:
        raise HTTPException(
            status_code=401,detail="Invalid or expired token"
        )
    return user
#register a new user
router = APIRouter(prefix="/auth",tags=["Authentication"])
@router.post("/register")
def register(data:RegisterRequest,db: Session=Depends(get_db)):
    user = create_user(db,data)
    if not user:
        raise HTTPException(
            status_code=400, detail="passwords do not match"
        )
    return {
        "message":"user registered successfully"
    }
#Login an existing user
@router.post("/login",response_model=TokenResponse)
def login(data : LoginRequest,db:Session = Depends(get_db)):
    user = authenticate_user(db,data)
    if not user:
        raise HTTPException(
            status_code= 401, detail= "Invalid email or password"
        )
    access_token = create_access_token(str(user.user_id))
    return{
        "access_token": access_token,
        "token_type":"bearer"
    }
@router.get("/me")
def get_me(curret_user= Depends(get_current_user)):
    return{
        "user_id": str(curret_user.user_id),
        "username": curret_user.username,
        "email": curret_user.email
    }