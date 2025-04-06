import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as DBEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # To get current time from the database server
from .database import Base
# Define Enums based on PDF requirements [cite: 4]
class UserRole(enum.Enum):
    EMPLOYE = "Employé"
    TECHNICIEN = "Technicien"
    ADMIN = "Admin"

class TicketStatus(enum.Enum):
    OUVERT = "Ouvert"
    EN_COURS = "En cours"
    RESOLU = "Résolu"
    FERME = "Fermé"

class TicketPriority(enum.Enum):
    FAIBLE = "Faible"
    MOYENNE = "Moyenne"
    ELEVEE = "Élevée"
    CRITIQUE = "Critique"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # 'nom' in PDF [cite: 4]
    email = Column(String, unique=True, index=True, nullable=False)
    # Renamed 'password' to 'hashed_password' for clarity - we will implement hashing next!
    hashed_password = Column(String, nullable=False) # 'mot_de_passe' in PDF [cite: 4]
    # Added 'role' field using Enum [cite: 4]
    role = Column(DBEnum(UserRole), nullable=False)
    # Added 'date_inscription' field with automatic timestamp [cite: 4]
    date_inscription = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships: A user can create many tickets and be assigned many tickets
    tickets_created = relationship("Ticket", back_populates="creator", foreign_keys="[Ticket.creator_id]")
    tickets_assigned = relationship("Ticket", back_populates="technician", foreign_keys="[Ticket.technician_id]")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False) # 'titre' in PDF [cite: 4]
    description = Column(String, nullable=False)
    # Updated 'status' to use Enum, with default [cite: 4]
    status = Column(DBEnum(TicketStatus), default=TicketStatus.OUVERT, nullable=False)
    # Updated 'priority' to use Enum, with default [cite: 4]
    priority = Column(DBEnum(TicketPriority), default=TicketPriority.MOYENNE, nullable=False)
    # Added 'date_creation' with automatic timestamp [cite: 4]
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    # Added 'date_mise_a_jour' with automatic update timestamp [cite: 4]
    date_mise_a_jour = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Renamed 'user_id' to 'creator_id' for clarity, linked to User.id [cite: 4]
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Added 'technician_id', linked to User.id, can be NULL [cite: 4]
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships: Link back to the User model
    # Link to the User who created the ticket
    creator = relationship("User", back_populates="tickets_created", foreign_keys=[creator_id])
    # Link to the User (technician) assigned to the ticket
    technician = relationship("User", back_populates="tickets_assigned", foreign_keys=[technician_id])