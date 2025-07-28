# backend/main.py

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# --- Database Imports ---
import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, Column, Integer, String, DateTime
import datetime

# --- Database Setup ---
DATABASE_URL = "sqlite:///./journal.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()

# --- Database Model (our table) ---
class Entry(Base):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

# Create the database tables
Base.metadata.create_all(bind=engine)

# --- Pydantic Model (for request body) ---
class JournalEntry(BaseModel):
    text: str

# --- FastAPI App ---
app = FastAPI()

origins = [
    "http://127.0.0.1:5500", # Live Server default
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency to get DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoint (Updated) ---
@app.post("/api/journal")
def save_journal_entry(entry: JournalEntry, db: Session = Depends(get_db)):
    # Create a new entry object from our DB model
    new_entry = Entry(text=entry.text)
    
    # Add it to the session and commit to the database
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry) # Refresh to get the new ID and date

    print(f"Saved entry ID {new_entry.id} to database.")
    
    # Return a success message
    return {"message": "Journal entry saved successfully!", "llm_response": "Thank you for sharing. Your thoughts have been saved."}

# Add this new Pydantic model at the top with your other models.
# This defines the data shape for a single entry being sent back.
class EntryResponse(BaseModel):
    id: int
    text: str
    created_date: datetime.datetime

    class Config:
        from_attributes = True

# Add this new endpoint function to your main.py
@app.get("/api/journal/entries", response_model=list[EntryResponse])
def get_all_entries(db: Session = Depends(get_db)):
    """
    This endpoint retrieves all journal entries from the database.
    """
    entries = db.query(Entry).order_by(Entry.created_date.desc()).all()
    return entries