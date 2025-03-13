from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL Connection
DATABASE_URL = "postgresql://postgres:password@localhost:5432/ticketing_system"

engine = create_engine(DATABASE_URL, echo=True)  # Added echo=True to debug

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
