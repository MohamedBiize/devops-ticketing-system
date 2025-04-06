# backend/schemas.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Dict

# Import Enums directly from models
from .models import UserRole, TicketStatus, TicketPriority

# --- User Schemas ---
class UserCreate(BaseModel): name: str; email: EmailStr; password: str; role: UserRole
class UserRead(BaseModel): id: int; name: str; email: EmailStr; role: UserRole; date_inscription: datetime; 
class Config: from_attributes = True

# --- Token Schemas ---
class Token(BaseModel): access_token: str; token_type: str
class TokenData(BaseModel): email: Optional[str] = None

# --- Ticket Schemas ---
class TicketBase(BaseModel): title: str; description: str; priority: Optional[TicketPriority] = None
class TicketCreate(TicketBase): pass
class TicketRead(TicketBase): id: int; status: TicketStatus; priority: TicketPriority; date_creation: datetime; date_mise_a_jour: datetime; creator_id: int; technician_id: Optional[int] = None; 
class Config: from_attributes = True

# --- UPDATE TicketUpdate SCHEMA BELOW ---
class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    technician_id: Optional[int] = None # <-- ADD THIS LINE (Allow assigning/unassigning)
# --- END OF UPDATE ---

# --- <<< ADD STATS SCHEMA BELOW >>> ---

class StatsResponse(BaseModel):
    total_tickets: int
    tickets_by_status: Dict[TicketStatus, int] # Count for each status enum member
    tickets_by_priority: Dict[TicketPriority, int] # Count for each priority enum member

# --- <<< END OF ADDED SCHEMA >>> ---

# --- <<< ADD COMMENT SCHEMAS BELOW >>> ---

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    # Only content is needed from user input
    pass

class CommentRead(CommentBase):
    id: int
    date_creation: datetime
    ticket_id: int
    creator_id: int
    # Optional: Add nested creator info later if needed
    # creator: UserRead

    class Config:
        from_attributes = True # Use Pydantic V2 syntax

# --- <<< END OF ADDED SCHEMAS >>> ---