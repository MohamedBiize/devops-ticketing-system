# backend/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Still needed for login form
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

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

@app.post("/tickets", response_model=schemas.TicketRead, status_code=status.HTTP_201_CREATED, tags=["Tickets"])
def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Require authentication
):
    """
    Creates a new support ticket.

    Requires authentication. The logged-in user will be set as the creator.
    - Takes ticket details (title, description, optional priority) in request body.
    - Returns the created ticket's data.
    """
    # Create a new Ticket database object
    new_ticket = models.Ticket(
        title=ticket.title,
        description=ticket.description,
        creator_id=current_user.id # Set creator to the logged-in user's ID
        # Status defaults to 'OUVERT' in the model
        # Priority defaults to 'MOYENNE' in the model unless provided
    )
    # If priority was provided in the request, set it
    if ticket.priority is not None:
        new_ticket.priority = ticket.priority

    # Add to session, commit, and refresh
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket) # Get DB-generated values like id, dates, default status

    return new_ticket # FastAPI uses response_model (TicketRead)

# --- <<< END OF TICKET CREATION ENDPOINT >>> ---

# --- Other ticket endpoints (GET, PUT, DELETE) will go here later ---

@app.get("/tickets", response_model=List[schemas.TicketRead], tags=["Tickets"])
def read_tickets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Require authentication
    # Add skip: int = 0, limit: int = 100 later for pagination
):
    """
    Retrieves a list of all tickets.

    Requires authentication.
    (Currently returns all tickets, filtering based on role to be added later).
    """
    tickets = db.query(models.Ticket).all() # Gets all tickets for now
    return tickets

# --- <<< END OF GET TICKETS ENDPOINT >>> ---

# --- Other ticket endpoints (GET by ID, PUT, DELETE) will go here later ---

# --- <<< ADD GET TICKET BY ID ENDPOINT BELOW >>> ---

@app.get("/tickets/{ticket_id}", response_model=schemas.TicketRead, tags=["Tickets"])
def read_ticket(
    ticket_id: int, # Path parameter to identify the ticket
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Require authentication
):
    """
    Retrieves a specific ticket by its ID.

    Requires authentication.
    (Currently allows any authenticated user to retrieve any ticket,
     authorization based on role/ownership to be added later).
    Returns 404 if the ticket is not found.
    """
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Add authorization checks here later (e.g., if current_user.role == ... or ticket.creator_id == current_user.id)

    return ticket

# --- <<< END OF GET TICKET BY ID ENDPOINT >>> ---

# --- Other ticket endpoints (PUT, DELETE) will go here later ---

# --- <<< ADD UPDATE TICKET ENDPOINT BELOW >>> ---

@app.put("/tickets/{ticket_id}", response_model=schemas.TicketRead, tags=["Tickets"])
def update_ticket(
    ticket_id: int,
    ticket_update: schemas.TicketUpdate, # Request body with optional fields
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Require authentication
):
    """
    Updates an existing ticket by its ID.

    Requires authentication. Allows updating title, description, status, priority.
    (Authorization checks based on role/ownership to be added later).
    Returns 404 if the ticket is not found.
    """
    # Fetch the existing ticket
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if db_ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # --- Authorization check placeholder ---
    # Add checks here later, e.g.:
    # if current_user.role == models.UserRole.EMPLOYE and db_ticket.creator_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this ticket")
    # elif current_user.role == models.UserRole.TECHNICIEN and db_ticket.technician_id != current_user.id and db_ticket.creator_id != current_user.id:
         # Allow technicians maybe more flexibility? Needs definition.
    #     pass # Or raise forbidden if they can only update assigned/own
    # --------------------------------------

    # Get the update data dictionary, excluding fields that were not set
    update_data = ticket_update.dict(exclude_unset=True)

    # Update the ticket object attributes
    for key, value in update_data.items():
        setattr(db_ticket, key, value)

    # Commit the changes (SQLAlchemy tracks changes to db_ticket)
    db.commit()
    # Refresh the object to get any updated fields from DB (like date_mise_a_jour)
    db.refresh(db_ticket)

    return db_ticket

# --- <<< END OF UPDATE TICKET ENDPOINT >>> ---

# --- DELETE endpoint will go here later ---

# --- <<< ADD DELETE TICKET ENDPOINT BELOW >>> ---

@app.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tickets"])
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Require authentication
):
    """
    Deletes a ticket by its ID.

    Requires authentication and ADMIN role.
    Returns 204 No Content on success.
    Returns 404 if the ticket is not found.
    Returns 403 if the user is not an Admin.
    """
    # --- Authorization Check ---
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete tickets"
        )
    # --------------------------

    # Fetch the ticket to delete
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if db_ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Delete the ticket
    db.delete(db_ticket)
    db.commit()

    # Return None for 204 No Content response
    return None

# --- <<< END OF DELETE TICKET ENDPOINT >>> ---