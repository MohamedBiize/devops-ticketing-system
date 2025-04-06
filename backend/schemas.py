# backend/schemas.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Import the Enum directly from models to reuse it
from .models import UserRole # Make sure this is a relative import

# Schema for creating a user (request body)
class UserCreate(BaseModel):
    name: str
    email: EmailStr # Pydantic type for email validation
    password: str # Plain password received from user
    role: UserRole # Use the Enum defined in models.py

# Schema for reading user data (response body)
# Excludes sensitive data like password
class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    date_inscription: datetime

    class Config:
        orm_mode = True


# <<< --- ADD THESE SCHEMAS BELOW --- >>>

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    # Use email as the identifier within the token, or user id
    email: Optional[str] = None
    # You could also include user_id: Optional[int] = None

# <<< --- END OF ADDED SCHEMAS --- >>>