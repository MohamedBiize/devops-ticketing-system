from fastapi import FastAPI
from database import engine, Base
import models  # Explicitly import models

app = FastAPI()

# Ensure models are registered
print("Registering models...")
Base.metadata.create_all(bind=engine)
print("Tables should now be created!")

@app.get("/")
def read_root():
    return {"message": "Hello, DevOps Ticketing System!"}
