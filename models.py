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
    """Bhajan model"""
    __tablename__ = "bhajans"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    lyrics = Column(Text, nullable=False)
    tags = Column(Text, default="[]")  # JSON array as string
    uploader_name = Column(String(100), default="Anonymous")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, default=None)  # Soft delete timestamp
    
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
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
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
