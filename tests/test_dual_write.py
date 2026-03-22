"""
Test Dual-Write Strategy for Tags

Tests that bhajans write tags to BOTH:
1. Old JSON field (tags column)
2. New bhajan_tags table

Ensures backward compatibility during migration period.
"""
import os
import sys
import json
import pytest
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Base, Bhajan
from dual_write import (
    dual_write_tags,
    read_bhajan_tags,
    get_tag_id_by_name,
    USE_TAG_TAXONOMY
)


@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    
    # Create tag taxonomy tables
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tag_taxonomy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                parent_id INTEGER,
                category VARCHAR(50) NOT NULL,
                level INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                CHECK (category IN ('deity', 'type', 'composer', 'temple', 'guru', 'day', 'occasion', 'theme', 'root'))
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS bhajan_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bhajan_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                source VARCHAR(50) DEFAULT 'manual',
                confidence REAL DEFAULT 1.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(bhajan_id, tag_id)
            )
        """))
        
        # Insert test tags
        conn.execute(text("""
            INSERT INTO tag_taxonomy (id, name, category, level) VALUES
            (1, 'hanuman', 'deity', 0),
            (2, 'rama', 'deity', 0),
            (3, 'krishna', 'deity', 0),
            (4, 'bhajan', 'type', 0),
            (5, 'aarti', 'type', 0)
        """))
        
        conn.commit()
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session, engine
    
    session.close()
    engine.dispose()


def test_create_bhajan_with_string_tags(test_db):
    """Test CREATE with tags as array of strings (old format)"""
    session, engine = test_db
    
    # Create bhajan with string tags
    bhajan = Bhajan(
        title="Test Bhajan 1",
        lyrics="Hanuman Chalisa lyrics here",
        uploader_name="Test User"
    )
    session.add(bhajan)
    session.commit()
    session.refresh(bhajan)
    
    # Dual write tags
    tag_names = ["hanuman", "bhajan"]
    dual_write_tags(session, bhajan.id, tag_names, source="manual")
    
    # Verify JSON field was written
    session.refresh(bhajan)
    stored_tags = bhajan.get_tags()
    assert set(stored_tags) == set(tag_names), f"JSON tags mismatch: {stored_tags}"
    
    # Verify bhajan_tags table was written
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT tag_id FROM bhajan_tags WHERE bhajan_id = :bid ORDER BY tag_id"
        ), {"bid": bhajan.id})
        tag_ids = [row[0] for row in result]
    
    assert len(tag_ids) == 2, f"Expected 2 tags in bhajan_tags, got {len(tag_ids)}"
    assert 1 in tag_ids, "Hanuman tag_id=1 should be in bhajan_tags"
    assert 4 in tag_ids, "Bhajan tag_id=4 should be in bhajan_tags"


def test_create_bhajan_with_tag_ids(test_db):
    """Test CREATE with tags as array of tag_ids (new format)"""
    session, engine = test_db
    
    # Create bhajan
    bhajan = Bhajan(
        title="Test Bhajan 2",
        lyrics="Rama Stuti lyrics here",
        uploader_name="Test User"
    )
    session.add(bhajan)
    session.commit()
    session.refresh(bhajan)
    
    # Dual write with tag_ids
    tag_ids = [2, 4]  # rama, bhajan
    dual_write_tags(session, bhajan.id, tag_ids, source="manual")
    
    # Verify bhajan_tags table
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT tag_id FROM bhajan_tags WHERE bhajan_id = :bid ORDER BY tag_id"
        ), {"bid": bhajan.id})
        stored_tag_ids = [row[0] for row in result]
    
    assert stored_tag_ids == [2, 4], f"Tag IDs mismatch: {stored_tag_ids}"
    
    # Verify JSON field has tag names
    session.refresh(bhajan)
    stored_tags = bhajan.get_tags()
    assert set(stored_tags) == {"rama", "bhajan"}, f"JSON tags should have names: {stored_tags}"


def test_update_bhajan_clears_old_tags(test_db):
    """Test UPDATE removes old tags before adding new ones"""
    session, engine = test_db
    
    # Create bhajan with initial tags
    bhajan = Bhajan(
        title="Test Bhajan 3",
        lyrics="Krishna Bhajan lyrics",
        uploader_name="Test User"
    )
    session.add(bhajan)
    session.commit()
    session.refresh(bhajan)
    
    # Initial tags
    dual_write_tags(session, bhajan.id, ["krishna", "bhajan"], source="manual")
    
    # Update with new tags
    dual_write_tags(session, bhajan.id, ["hanuman", "aarti"], source="manual")
    
    # Verify old tags removed
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT tag_id FROM bhajan_tags WHERE bhajan_id = :bid ORDER BY tag_id"
        ), {"bid": bhajan.id})
        tag_ids = [row[0] for row in result]
    
    assert tag_ids == [1, 5], f"Should only have new tags [1=hanuman, 5=aarti], got {tag_ids}"
    
    # Verify JSON field updated
    session.refresh(bhajan)
    stored_tags = bhajan.get_tags()
    assert set(stored_tags) == {"hanuman", "aarti"}, f"JSON should have new tags: {stored_tags}"


def test_read_bhajan_prefers_taxonomy(test_db):
    """Test READ prefers bhajan_tags table over JSON field"""
    session, engine = test_db
    
    # Create bhajan
    bhajan = Bhajan(
        title="Test Bhajan 4",
        lyrics="Test lyrics",
        uploader_name="Test User"
    )
    # Set JSON tags manually (simulating old data)
    bhajan.set_tags(["old-tag-1", "old-tag-2"])
    session.add(bhajan)
    session.commit()
    session.refresh(bhajan)
    
    # Add tags to taxonomy table
    dual_write_tags(session, bhajan.id, ["rama", "bhajan"], source="manual")
    
    # Read should prefer taxonomy
    tags = read_bhajan_tags(session, bhajan.id)
    assert set(tags) == {"rama", "bhajan"}, f"Should read from taxonomy, not JSON: {tags}"


def test_read_bhajan_fallback_to_json(test_db):
    """Test READ falls back to JSON field if taxonomy empty"""
    session, engine = test_db
    
    # Create bhajan with only JSON tags (no taxonomy entries)
    bhajan = Bhajan(
        title="Test Bhajan 5",
        lyrics="Test lyrics",
        uploader_name="Test User"
    )
    bhajan.set_tags(["json-only-tag"])
    session.add(bhajan)
    session.commit()
    session.refresh(bhajan)
    
    # Read should fallback to JSON
    tags = read_bhajan_tags(session, bhajan.id)
    assert tags == ["json-only-tag"], f"Should fallback to JSON: {tags}"


def test_feature_flag_disabled(test_db, monkeypatch):
    """Test dual-write disabled when USE_TAG_TAXONOMY=false"""
    session, engine = test_db
    
    # Disable feature flag
    monkeypatch.setenv("USE_TAG_TAXONOMY", "false")
    
    # Create bhajan
    bhajan = Bhajan(
        title="Test Bhajan 6",
        lyrics="Test lyrics",
        uploader_name="Test User"
    )
    session.add(bhajan)
    session.commit()
    session.refresh(bhajan)
    
    # Dual write should only write to JSON
    dual_write_tags(session, bhajan.id, ["hanuman"], source="manual")
    
    # Verify JSON field written
    session.refresh(bhajan)
    assert bhajan.get_tags() == ["hanuman"]
    
    # Verify taxonomy table NOT written
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT COUNT(*) FROM bhajan_tags WHERE bhajan_id = :bid"
        ), {"bid": bhajan.id})
        count = result.scalar()
    
    assert count == 0, "Taxonomy should not be written when feature flag is false"


def test_nonexistent_tag_name_is_skipped(test_db):
    """Test that invalid tag names are skipped (don't crash)"""
    session, engine = test_db
    
    bhajan = Bhajan(
        title="Test Bhajan 7",
        lyrics="Test lyrics",
        uploader_name="Test User"
    )
    session.add(bhajan)
    session.commit()
    session.refresh(bhajan)
    
    # Try to write with nonexistent tag
    dual_write_tags(session, bhajan.id, ["hanuman", "nonexistent-tag"], source="manual")
    
    # Should only write valid tags
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT tag_id FROM bhajan_tags WHERE bhajan_id = :bid"
        ), {"bid": bhajan.id})
        tag_ids = [row[0] for row in result]
    
    assert tag_ids == [1], f"Should only write valid tags: {tag_ids}"
    
    # JSON should still have both (backward compat)
    session.refresh(bhajan)
    stored_tags = bhajan.get_tags()
    assert set(stored_tags) == {"hanuman", "nonexistent-tag"}, "JSON should keep all tags"


def test_mixed_tags_and_tag_ids(test_db):
    """Test that both strings and integers can be passed"""
    session, engine = test_db
    
    bhajan = Bhajan(
        title="Test Bhajan 8",
        lyrics="Test lyrics",
        uploader_name="Test User"
    )
    session.add(bhajan)
    session.commit()
    session.refresh(bhajan)
    
    # Pass mixed list
    dual_write_tags(session, bhajan.id, ["hanuman", 2], source="manual")  # name + id
    
    # Verify both written correctly
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT tag_id FROM bhajan_tags WHERE bhajan_id = :bid ORDER BY tag_id"
        ), {"bid": bhajan.id})
        tag_ids = [row[0] for row in result]
    
    assert tag_ids == [1, 2], f"Should have both tags: {tag_ids}"
    
    # JSON should have names
    session.refresh(bhajan)
    stored_tags = bhajan.get_tags()
    assert set(stored_tags) == {"hanuman", "rama"}, f"JSON should have names: {stored_tags}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
