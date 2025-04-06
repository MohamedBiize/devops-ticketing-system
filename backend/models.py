# backend/models.py

import enum
# Make sure all necessary imports are here
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as DBEnum, Boolean # Added Boolean if used later
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base # Relative import

# --- Enums (UserRole, TicketStatus, TicketPriority - Keep As Is) ---
class UserRole(enum.Enum): EMPLOYE = "Employé"; TECHNICIEN = "Technicien"; ADMIN = "Admin"
class TicketStatus(enum.Enum): OUVERT = "Ouvert"; EN_COURS = "En cours"; RESOLU = "Résolu"; FERME = "Fermé"
class TicketPriority(enum.Enum): FAIBLE = "Faible"; MOYENNE = "Moyenne"; ELEVEE = "Élevée"; CRITIQUE = "Critique"


# --- User Model (Add comments relationship) ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(DBEnum(UserRole), nullable=False)
    date_inscription = Column(DateTime(timezone=True), server_default=func.now())

    tickets_created = relationship("Ticket", back_populates="creator", foreign_keys="[Ticket.creator_id]")
    tickets_assigned = relationship("Ticket", back_populates="technician", foreign_keys="[Ticket.technician_id]")
    comments = relationship("Comment", back_populates="creator") # <-- ADD THIS RELATIONSHIP


# --- Ticket Model (Add comments relationship) ---
class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    status = Column(DBEnum(TicketStatus), default=TicketStatus.OUVERT, nullable=False)
    priority = Column(DBEnum(TicketPriority), default=TicketPriority.MOYENNE, nullable=False)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_mise_a_jour = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    creator = relationship("User", back_populates="tickets_created", foreign_keys=[creator_id])
    technician = relationship("User", back_populates="tickets_assigned", foreign_keys=[technician_id])
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan") # <-- ADD THIS RELATIONSHIP (added cascade)


# --- <<< ADD COMMENT MODEL BELOW >>> ---

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())

    # Foreign Keys
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    ticket = relationship("Ticket", back_populates="comments")
    creator = relationship("User", back_populates="comments")

# --- <<< END OF ADDED MODEL >>> ---