# backend/security.py

import enum # Keep if needed elsewhere, though not directly used here
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
# --- Need these for get_current_user dependency ---
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# --- Import schemas and models ---
from . import models, schemas
from .database import get_db

# --- OAuth2 Scheme Definition ---
# tokenUrl should match the path operation path of your token endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# --- JWT Configuration ---
# !!! IMPORTANT: Use environment variables for secrets in production!
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" # Replace with your generated key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token validity period

# --- Password Hashing Context ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hashes a plain password using the configured context."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(email: str, password: str, db: Session) -> Optional[models.User]:
    """Authenticates a user based on email and password."""
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None # User not found
    if not verify_password(password, user.hashed_password):
        return None # Incorrect password
    return user # Authentication successful

def verify_access_token(token: str, credentials_exception) -> schemas.TokenData:
    """Decodes and verifies the JWT token, returns token data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub") # 'sub' is standard claim for subject
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """Dependency to get the current user based on the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user