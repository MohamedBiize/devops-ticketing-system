# backend/main.py

from fastapi import FastAPI, Depends, HTTPException, status # <-- Added HTTPException, status
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from . import models
from .security import hash_password, verify_password
from . import schemas

app = FastAPI(title="Ticketing System API")

# Create database tables on startup (Consider Alembic for production)
print("Attempting to create database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("Tables checked/created successfully.")
except Exception as e:
    print(f"Error creating tables: {e}")


# Root endpoint (example)
@app.get("/")
def read_root(db: Session = Depends(get_db)):
    print(f"Database session received: {db}") # Example log
    return {"message": "Hello from the Ticketing System API!"}


# --- <<< ADD THE USER REGISTRATION ENDPOINT BELOW >>> ---

@app.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user.
    - Takes user details (name, email, password, role) in the request body.
    - Hashes the password before saving.
    - Checks if email already exists.
    - Returns the created user's data (excluding password).
    """
    # Check if user with this email already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_pwd = hash_password(user.password)

    # Create new User database object
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_pwd, # Store the hashed password
        role=user.role
    )

    # Add to session, commit, and refresh
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # Refresh to get DB-generated data like ID, date_inscription

    return new_user # FastAPI uses response_model (UserRead) to filter output

# --- <<< END OF USER REGISTRATION ENDPOINT >>> ---

# --- Other endpoints will go here later ---