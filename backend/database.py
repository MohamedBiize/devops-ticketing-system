from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session

# PostgreSQL Connection
DATABASE_URL = "postgresql://postgres:password@localhost:5432/ticketing_system"

engine = create_engine(DATABASE_URL, echo=True)  # Added echo=True to debug

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Dependency function to get a DB session per request.
    Ensures the session is always closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()