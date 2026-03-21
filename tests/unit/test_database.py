"""Unit tests for database operations"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models import Bhajan, init_db, Base

# Test database URL (use in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)

def test_create_bhajan(db_session):
    """Test creating a bhajan"""
    bhajan = Bhajan(
        title="Test Bhajan",
        lyrics="Om Namah Shivaya"
    )
    
    db_session.add(bhajan)
    db_session.commit()
    
    # Retrieve and verify
    saved = db_session.query(Bhajan).filter_by(title="Test Bhajan").first()
    assert saved is not None
    assert saved.title == "Test Bhajan"

def test_search_bhajan(db_session):
    """Test searching bhajans"""
    # Add test data
    bhajans = [
        Bhajan(title="Rama Bhajan", lyrics="Shri Rama Chandra"),
        Bhajan(title="Krishna Bhajan", lyrics="Hare Krishna"),
        Bhajan(title="Shiva Stotram", lyrics="Om Namah Shivaya"),
    ]
    
    for b in bhajans:
        db_session.add(b)
    db_session.commit()
    
    # Search for "Rama"
    results = db_session.query(Bhajan).filter(
        Bhajan.title.ilike('%Rama%') | Bhajan.lyrics.ilike('%Rama%')
    ).all()
    
    assert len(results) >= 1

def test_bhajan_required_fields(db_session):
    """Test that required fields are enforced"""
    # Title is required, should work without deity
    bhajan = Bhajan(title="Valid Bhajan", lyrics="Test")
    db_session.add(bhajan)
    db_session.commit()
    
    # Should succeed
    assert bhajan.id is not None
