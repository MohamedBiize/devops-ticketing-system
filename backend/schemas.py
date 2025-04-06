# backend/schemas.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List # Ensure List is imported if used elsewhere

# Import Enums directly from models
from .models import UserRole, TicketStatus, TicketPriority

# --- User Schemas (Existing) ---
# ... (UserCreate, UserRead) ...
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    date_inscription: datetime
    class Config: from_attributes = True # Updated from orm_mode

# --- Token Schemas (Existing) ---
# ... (Token, TokenData) ...
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


# --- Ticket Schemas (Existing & New) ---
class TicketBase(BaseModel):
    title: str
    description: str
    priority: Optional[TicketPriority] = None

class TicketCreate(TicketBase):
    pass

class TicketRead(TicketBase):
    id: int
    status: TicketStatus
    priority: TicketPriority
    date_creation: datetime
    date_mise_a_jour: datetime
    creator_id: int
    technician_id: Optional[int] = None
    class Config: from_attributes = True # Updated from orm_mode

# --- <<< ADD TICKET UPDATE SCHEMA BELOW >>> ---

class TicketUpdate(BaseModel):
    # All fields are optional for updates
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    # We might handle technician_id assignment separately or with authorization
    # technician_id: Optional[int] = None

# --- <<< END OF ADDED SCHEMA >>> ---