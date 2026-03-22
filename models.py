"""
Database models for Belaguru Bhajan Portal
"""
import json
import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Ensure data directory exists
os.makedirs("./data", exist_ok=True)

Base = declarative_base()


class TagTaxonomy(Base):
    """Tag Taxonomy model - hierarchical tag system"""
    __tablename__ = "tag_taxonomy"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("tag_taxonomy.id", ondelete="SET NULL"), nullable=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    level = Column(Integer, nullable=False, default=0, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Self-referential relationship for hierarchy
    parent = relationship("TagTaxonomy", remote_side=[id], backref="children")
    
    # Relationships to translations and synonyms
    translations = relationship("TagTranslation", back_populates="tag", cascade="all, delete-orphan")
    synonyms = relationship("TagSynonym", back_populates="tag", cascade="all, delete-orphan")


class TagTranslation(Base):
    """Tag Translation model - multi-language support"""
    __tablename__ = "tag_translations"
    
    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tag_taxonomy.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(10), nullable=False, index=True)
    translation = Column(String(100), nullable=False)
    
    # Relationship back to tag
    tag = relationship("TagTaxonomy", back_populates="translations")


class TagSynonym(Base):
    """Tag Synonym model - search aliases"""
    __tablename__ = "tag_synonyms"
    
    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tag_taxonomy.id", ondelete="CASCADE"), nullable=False, index=True)
    synonym = Column(String(100), nullable=False, unique=True, index=True)
    
    # Relationship back to tag
    tag = relationship("TagTaxonomy", back_populates="synonyms")


class BhajanTag(Base):
    """Bhajan-Tag Association model - many-to-many with metadata"""
    __tablename__ = "bhajan_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    bhajan_id = Column(Integer, ForeignKey("bhajans.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("tag_taxonomy.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(50), default="manual", index=True)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    bhajan = relationship("Bhajan", back_populates="taxonomy_tags")
    tag = relationship("TagTaxonomy")


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
    tags = Column(Text, default="[]")  # JSON array as string (backward compatibility)
    uploader_name = Column(String(100), default="Anonymous")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, default=None)  # Soft delete timestamp
    youtube_url = Column(String(500), default=None, nullable=True)  # YouTube video URL
    mp3_file = Column(Text, nullable=True)  # MP3 audio file path
    
    # Relationship to taxonomy tags
    taxonomy_tags = relationship("BhajanTag", back_populates="bhajan")
    
    def get_tags(self):
        """Parse tags from JSON string (backward compatibility)"""
        try:
            return json.loads(self.tags) if self.tags else []
        except:
            return []
    
    def set_tags(self, tags_list):
        """Set tags from list (backward compatibility)"""
        self.tags = json.dumps(tags_list)
    
    def get_all_tags(self):
        """
        Get all tags - both old JSON tags and new taxonomy tags
        Returns dict with 'json_tags' and 'taxonomy_tags'
        """
        return {
            "json_tags": self.get_tags(),
            "taxonomy_tags": [
                {
                    "id": bt.tag.id,
                    "name": bt.tag.name,
                    "category": bt.tag.category,
                    "source": bt.source,
                    "confidence": bt.confidence
                }
                for bt in self.taxonomy_tags
            ]
        }
    
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


# Database setup - configurable via environment variable
DATABASE_PATH = os.environ.get("DATABASE_PATH", "./data/portal.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_database_path() -> str:
    """Get current database file path (for direct sqlite3 connections)"""
    return DATABASE_PATH


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
