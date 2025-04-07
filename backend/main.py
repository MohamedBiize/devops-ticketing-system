# backend/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_,func # <-- IMPORT or_ FOR COMBINING FILTERS
from datetime import timedelta
from typing import List, Dict

# Import engine, Base from database.py and get_db dependency
from .database import engine, Base, get_db # Make sure 'Base' is listed here!
from . import models # Need models for UserRole check and querying
# Import all needed security functions and schemas
from .security import (
    hash_password,
    # verify_password, # Not directly used here
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from . import schemas

app = FastAPI(title="Ticketing System API")

origins = [
    "http://localhost:5173", # Default Vite React port
    "http://localhost:3000", # Default Create React App port
    "http://127.0.0.1:5173",
    # Add any other ports/origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Allows specified origins
    allow_credentials=True, # Allows cookies (not used here yet, but often needed)
    allow_methods=["*"], # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allows all headers
)

# Create database tables (Consider Alembic for production)
# print("Attempting to create database tables...") # Optional: Keep or remove startup prints
print("Attempting to create database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("Tables checked/created successfully.")
except Exception as e:
    print(f"Error during startup table check: {e}")

# --- Endpoints ---

@app.get("/", tags=["Default"])
def read_root(db: Session = Depends(get_db)):
    """Root endpoint."""
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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserRead, tags=["Users"])
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Gets the current logged-in user's details (requires authentication)."""
    return current_user


@app.post("/tickets", response_model=schemas.TicketRead, status_code=status.HTTP_201_CREATED, tags=["Tickets"])
def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Creates a new support ticket (requires authentication)."""
    new_ticket = models.Ticket(
        title=ticket.title,
        description=ticket.description,
        creator_id=current_user.id
    )
    if ticket.priority is not None:
        new_ticket.priority = ticket.priority
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket


@app.get("/tickets", response_model=List[schemas.TicketRead], tags=["Tickets"])
def read_tickets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieves a list of tickets based on user role.
    - Admins see all tickets.
    - Technicians see tickets created by or assigned to them.
    - Employees see tickets created by them.
    Requires authentication.
    """
    if current_user.role == models.UserRole.ADMIN:
        tickets = db.query(models.Ticket).all()
    elif current_user.role == models.UserRole.TECHNICIEN:
        tickets = db.query(models.Ticket).filter(
            or_(models.Ticket.technician_id == current_user.id,
                models.Ticket.creator_id == current_user.id)
        ).all()
    elif current_user.role == models.UserRole.EMPLOYE:
        tickets = db.query(models.Ticket).filter(models.Ticket.creator_id == current_user.id).all()
    else: # Should not happen with valid roles, but include for safety
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role not recognized")

    return tickets


@app.get("/tickets/{ticket_id}", response_model=schemas.TicketRead, tags=["Tickets"])
def read_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieves a specific ticket by its ID, checking authorization based on role.
    Requires authentication. Returns 404 if not found, 403 if not authorized.
    """
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Authorization checks
    is_authorized = False
    if current_user.role == models.UserRole.ADMIN:
        is_authorized = True
    elif current_user.role == models.UserRole.TECHNICIEN:
        if ticket.technician_id == current_user.id or ticket.creator_id == current_user.id:
            is_authorized = True
    elif current_user.role == models.UserRole.EMPLOYE:
        if ticket.creator_id == current_user.id:
            is_authorized = True

    if not is_authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this ticket")

    return ticket


@app.put("/tickets/{ticket_id}", response_model=schemas.TicketRead, tags=["Tickets"])
def update_ticket(
    ticket_id: int,
    ticket_update: schemas.TicketUpdate, # Request body now includes optional technician_id
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Updates an existing ticket by its ID.

    Requires authentication. Authorization based on role:
    - Admin: Can update all fields (title, desc, status, priority, technician_id).
    - Technician: Can update title, desc, status, priority ONLY for tickets assigned to them.
    - Employee: Cannot update tickets via this endpoint.
    Returns 404 if the ticket is not found.
    Returns 403 if not authorized.
    """
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if db_ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Get the raw update data
    update_data = ticket_update.dict(exclude_unset=True)

    # --- Authorization & Update Logic ---
    can_update_other_fields = False
    can_update_assignment = False

    # Check if user is Admin
    if current_user.role == models.UserRole.ADMIN:
        can_update_other_fields = True
        can_update_assignment = True

    # Check if user is Technician and assigned
    elif current_user.role == models.UserRole.TECHNICIEN:
        if db_ticket.technician_id == current_user.id:
            can_update_other_fields = True
        # Technicians cannot re-assign via this endpoint by default
        can_update_assignment = False

    # Handle technician_id update separately (only if Admin is allowed)
    if 'technician_id' in update_data:
        if not can_update_assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to assign technicians to this ticket"
            )
        # If authorized (Admin), update the assignment
        setattr(db_ticket, 'technician_id', update_data['technician_id'])
        # Remove it from update_data so it's not processed again below
        del update_data['technician_id']

    # Handle updates for other fields (title, description, status, priority)
    if update_data: # Check if there are any other fields left to update
        if not can_update_other_fields:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update other fields on this ticket"
            )
        # Update remaining fields
        for key, value in update_data.items():
            setattr(db_ticket, key, value)
    # --- End Authorization & Update Logic ---

    # Commit and refresh
    db.commit()
    db.refresh(db_ticket)

    return db_ticket

# ... (Keep the delete_ticket endpoint and any other code below) ...



@app.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tickets"])
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Deletes a ticket (Admin only)."""
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete tickets"
        )
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    db.delete(db_ticket)
    db.commit()
    return None

# --- <<< ADD ADMIN STATS ENDPOINT BELOW >>> ---

@app.get("/stats", response_model=schemas.StatsResponse, tags=["Admin", "Statistics"])
def get_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Require authentication
):
    """
    Retrieves ticket statistics (Admin only).

    Returns total ticket count, counts by status, and counts by priority.
    Requires authentication and ADMIN role.
    """
    # --- Authorization Check ---
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access statistics"
        )
    # --------------------------

    # Calculate total tickets
    total_tickets = db.query(models.Ticket).count()

    # Calculate counts by status
    status_counts_query = db.query(
        models.Ticket.status, func.count(models.Ticket.id)
    ).group_by(models.Ticket.status).all()
    # Initialize dict with all statuses set to 0
    tickets_by_status = {status: 0 for status in models.TicketStatus}
    # Populate dict with actual counts from query
    for status, count in status_counts_query:
        tickets_by_status[status] = count

    # Calculate counts by priority
    priority_counts_query = db.query(
        models.Ticket.priority, func.count(models.Ticket.id)
    ).group_by(models.Ticket.priority).all()
    # Initialize dict with all priorities set to 0
    tickets_by_priority = {priority: 0 for priority in models.TicketPriority}
    # Populate dict with actual counts from query
    for priority, count in priority_counts_query:
        tickets_by_priority[priority] = count

    # Construct and return the response object
    return schemas.StatsResponse(
        total_tickets=total_tickets,
        tickets_by_status=tickets_by_status,
        tickets_by_priority=tickets_by_priority
    )

# --- <<< END OF ADMIN STATS ENDPOINT >>> ---
@app.post("/tickets/{ticket_id}/comments", response_model=schemas.CommentRead, status_code=status.HTTP_201_CREATED, tags=["Comments"])
def create_comment_for_ticket(
    ticket_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Require authentication
):
    """
    Adds a comment to a specific ticket.

    Requires authentication. User must be authorized to view the ticket.
    Returns the created comment.
    """
    # Check if ticket exists and user can view it (reuse logic from read_ticket)
    try:
        # Call read_ticket logic to check existence and authorization
        # We don't need the return value here, just the checks inside it
        read_ticket(ticket_id=ticket_id, db=db, current_user=current_user)
    except HTTPException as e:
        # Re-raise if ticket not found (404) or user not authorized (403)
         raise e

    # Create the comment
    new_comment = models.Comment(
        content=comment.content,
        ticket_id=ticket_id,
        creator_id=current_user.id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@app.get("/tickets/{ticket_id}/comments", response_model=List[schemas.CommentRead], tags=["Comments"])
def read_comments_for_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Require authentication
):
    """
    Retrieves all comments for a specific ticket.

    Requires authentication. User must be authorized to view the ticket.
    Returns a list of comments.
    """
    # Check if ticket exists and user can view it (reuse logic from read_ticket)
    try:
        read_ticket(ticket_id=ticket_id, db=db, current_user=current_user)
    except HTTPException as e:
        raise e

    # Get comments for the ticket, ordered by creation date
    comments = db.query(models.Comment)\
                 .filter(models.Comment.ticket_id == ticket_id)\
                 .order_by(models.Comment.date_creation)\
                 .all()
    return comments

# --- <<< END OF COMMENT ENDPOINTS >>> ---