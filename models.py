"""
Database models for Belaguru Bhajan Portal
"""
import json
import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ensure data directory exists
os.makedirs("./data", exist_ok=True)

Base = declarative_base()


class Bhajan(Base):
    """Bhajan model - ALL columns must match database schema exactly"""
    __tablename__ = "bhajans"
    
    # Column order matches database schema from PRAGMA table_info
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    lyrics = Column(Text, nullable=False)
    manual_tags = Column(Text, nullable=True)  # Legacy column
    auto_tags = Column(Text, nullable=True)  # Legacy column
    language = Column(String(50), nullable=True)
    tone = Column(String(255), nullable=True)
    detected_raga = Column(String(255), nullable=True)
    related_deities = Column(Text, nullable=True)
    pdf_filename = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime, nullable=True)
    tags = Column(Text, default="")  # JSON array as string
    uploader_name = Column(Text, default="Unknown")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, default=None)  # Soft delete timestamp
    youtube_url = Column(String(500), default=None, nullable=True)  # YouTube video URL
    mp3_file = Column(Text, nullable=True)  # MP3 audio file path
    
    def get_tags(self):
        """Parse tags from JSON string"""
        try:
            return json.loads(self.tags) if self.tags else []
        except:
            return []
    
    def set_tags(self, tags_list):
        """Set tags from list"""
        self.tags = json.dumps(tags_list)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "lyrics": self.lyrics,
            "tags": self.get_tags(),
            "uploader_name": self.uploader_name,
            "youtube_url": self.youtube_url,
            "mp3_file": self.mp3_file,  # Now works correctly with full column mapping
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# Database setup
DATABASE_URL = "sqlite:///./data/portal.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
