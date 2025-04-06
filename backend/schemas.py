# backend/schemas.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional # Keep Optional if needed elsewhere, though not strictly necessary for these specific models yet.

# Import the Enum directly from models to reuse it
from .models import UserRole

# Schema for creating a user (request body)
class UserCreate(BaseModel):
    name: str
    email: EmailStr # Pydantic type for email validation
    password: str # Plain password received from user
    role: UserRole # Use the Enum defined in models.py

    # Example for Pydantic configuration if needed later
    # class Config:
    #     orm_mode = True # Allows mapping directly to ORM models if needed elsewhere

# Schema for reading user data (response body)
# Excludes sensitive data like password
class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    date_inscription: datetime

    # This tells Pydantic to read data even if it's not a dict,
    # but an ORM model (or any other arbitrary object with attributes).
    class Config:
        orm_mode = True