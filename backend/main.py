# backend/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Still needed for login form
from sqlalchemy.orm import Session
from datetime import timedelta

# Import engine, Base from database.py and get_db dependency
from .database import engine, Base, get_db
from . import models
# Import all needed security functions and schemas
from .security import (
    hash_password,
    # verify_password, # Not directly used in main.py anymore
    authenticate_user,
    create_access_token,
    get_current_user, # Need this dependency for protected routes
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from . import schemas

app = FastAPI(title="Ticketing System API")

# Create database tables (Consider Alembic for production)
print("Attempting to create database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("Tables checked/created successfully.")
except Exception as e:
    print(f"Error creating tables: {e}")


# --- Endpoints ---

# Inside main.py
@app.get("/", tags=["Default"])
def read_root(): # <-- REMOVED database dependency
    """Root endpoint."""
    # <-- ADDED print statement
    return {"message": "Hello from the Ticketing System API!"}


@app.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Registers a new user."""
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_pwd = hash_password(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_pwd,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Logs in a user using email and password (OAuth2 Password Flow)."""
    user = authenticate_user(email=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # Use config value from security.py
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserRead, tags=["Users"])
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Gets the current logged-in user's details (requires authentication)."""
    return current_user

# --- Ticket endpoints will go here later ---