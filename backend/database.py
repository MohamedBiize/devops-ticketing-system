# backend/database.py

from sqlalchemy import create_engine, NullPool # <-- IMPORT NullPool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "postgresql://postgres:password@localhost:5432/ticketing_system"

# ADD poolclass=NullPool to disable pooling for testing
engine = create_engine(DATABASE_URL, echo=True, poolclass=NullPool) # <-- ADDED poolclass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Keep the get_db function with print statements from the previous step
def get_db():
    """Dependency function to get a DB session per request."""
    print("\n--- DEBUG: Entering get_db ---")
    db = None
    try:
        print("--- DEBUG: Calling SessionLocal() ---")
        db = SessionLocal()
        print(f"--- DEBUG: SessionLocal() returned: {db} ---")
        yield db
        print("--- DEBUG: Yielded session successfully ---")
    finally:
        if db:
            print(f"--- DEBUG: In finally block, closing session {db} ---")
            db.close()
            print("--- DEBUG: Session closed ---")
        else:
            print("--- DEBUG: In finally block, db object was not created ---")
    print("--- DEBUG: Exiting get_db ---\n")