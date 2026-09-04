from sqlalchemy.orm import Session
from app.database.models import User
from app.schemas.auth_schema import RegisterRequest,LoginRequest
from passlib.context import CryptContext
from datetime import datetime, timedelta,timezone
from uuid import UUID
from jose import jwt
import os
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY","dev-secret-key")
ALGORITHM = "HS256"
#hash password before storing in database
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str):
    return pwd_context.verify(password, password_hash)
#create and save new user in database
def create_user(db: Session, data: RegisterRequest):
    if data.password != data.confirm_password:
        return None
    user = User(
        username=data.username, email=data.email, password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
#Authenticate user
def authenticate_user(db: Session, data: LoginRequest):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return None
    if not verify_password(data.password, user.password_hash):
        return None
    return user
#Generate JWT access token
def create_access_token(user_id):
    expire = datetime.now(timezone.utc)+ timedelta(minutes=30)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
#Validate JWT access token
def validate_access_token(token: str, db: Session):
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = db.query(User).filter(User.user_id == UUID(user_id)).first()
        if not user:
            return None
        return user
    except Exception:
        return None