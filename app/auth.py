from fastapi import status, Depends, HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import schemas
from datetime import datetime, timedelta

import jwt
from sqlalchemy.orm import Session
import models
import database

SECRET_KEY = "TEST"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 800

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
    
def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data : dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else: 
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp':expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(db: Session, username : str):
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db:Session, username:str, password:str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except jwt.exceptions.InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.RoleEnum.user and current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user

def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=400, detail='User is not admin')
    return current_user