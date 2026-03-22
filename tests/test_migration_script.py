"""
Test suite for tag migration script

Tests:
1. Dry-run mode (no database changes)
2. Tag mapping (old → canonical)
3. Transaction safety (rollback on error)
4. Backward compatibility (keeps original tags field)
5. Rollback mode (delete MIGRATED records)
"""
import pytest
import sys
import os
import json
import sqlite3
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from migrate_tags import (
    load_tag_mapping,
    map_tag_to_canonical,
    migrate_bhajan_tags,
    rollback_migration,
    get_migration_stats
)


# Test database setup
TEST_DB = "./test_migration.db"


@pytest.fixture
def test_db():
    """Create test database with sample data"""
    # Remove existing test db
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    # Create schema
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    
    # Create bhajans table
    cursor.execute("""
        CREATE TABLE bhajans (
            id INTEGER PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            lyrics TEXT NOT NULL,
            tags TEXT DEFAULT '[]'
        )
    """)
    
    # Create tag_taxonomy table
    cursor.execute("""
        CREATE TABLE tag_taxonomy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            parent_id INTEGER,
            category VARCHAR(50) NOT NULL,
            level INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create bhajan_tags table
    cursor.execute("""
        CREATE TABLE bhajan_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bhajan_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            source VARCHAR(50) DEFAULT 'manual',
            confidence REAL DEFAULT 1.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(bhajan_id, tag_id)
        )
    """)
    
    # Insert sample tags into tag_taxonomy (capitalized like production)
    sample_tags = [
        ('Hanuman', None, 'deity', 0),
        ('Rama', None, 'deity', 0),
        ('Krishna', None, 'deity', 0),
        ('Shiva', None, 'deity', 0),
        ('Ganesha', None, 'deity', 0),
    ]
    
    cursor.executemany(
        "INSERT INTO tag_taxonomy (name, parent_id, category, level) VALUES (?, ?, ?, ?)",
        sample_tags
    )
    
    # Insert sample bhajans with old-style tags
    sample_bhajans = [
        (1, "Hanuman Chalisa", "Jai Hanuman...", '["hanuman", "chalisa", "test"]'),
        (2, "Rama Bhajan", "Sri Rama...", '["Rama", "bhajan", "Test"]'),
        (3, "Krishna Stuti", "Krishna Krishna...", '["krishna", "stuti"]'),
        (4, "Shiva Ashtakam", "Om Namah Shivaya...", '["Shiva", "ashtakam", "Anjaneya"]'),
        (5, "Untagged Bhajan", "Bhajan lyrics...", '[]'),
    ]
    
    cursor.executemany(
        "INSERT INTO bhajans (id, title, lyrics, tags) VALUES (?, ?, ?, ?)",
        sample_bhajans
    )
    
    conn.commit()
    conn.close()
    
    yield TEST_DB
    
    # Cleanup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


class TestTagMapping:
    """Test tag mapping logic"""
    
    def test_load_tag_mapping(self):
        """Test loading tag mapping CSV"""
        mapping = load_tag_mapping()
        
        assert isinstance(mapping, dict)
        assert len(mapping) > 0
        
        # Check known mappings
        assert mapping.get('test') == {'action': 'DELETE', 'canonical': 'N/A'}
        assert mapping.get('Anjaneya') == {'action': 'MERGE', 'canonical': 'Hanuman'}
        assert mapping.get('hanuman') == {'action': 'MERGE', 'canonical': 'Hanuman'}
    
    def test_map_tag_to_canonical(self):
        """Test tag mapping to canonical form"""
        mapping = load_tag_mapping()
        
        # Test DELETE action
        assert map_tag_to_canonical('test', mapping) is None
        assert map_tag_to_canonical('Test', mapping) is None
        
        # Test MERGE action
        assert map_tag_to_canonical('Anjaneya', mapping) == 'Hanuman'
        assert map_tag_to_canonical('hanuman', mapping) == 'Hanuman'
        assert map_tag_to_canonical('maruti', mapping) == 'Hanuman'
        
        # Test KEEP action
        assert map_tag_to_canonical('ashtakam', mapping) == 'ashtakam'
        assert map_tag_to_canonical('Chalisa', mapping) == 'Chalisa'
        
        # Test unknown tag (pass through as-is)
        assert map_tag_to_canonical('UnknownTag', mapping) == 'UnknownTag'


class TestMigration:
    """Test migration functionality"""
    
    def test_dry_run_mode(self, test_db):
        """Test dry-run mode (no database changes)"""
        result = migrate_bhajan_tags(
            db_path=test_db,
            dry_run=True,
            verbose=True
        )
        
        # Check results
        assert result['status'] == 'success'
        assert result['dry_run'] is True
        assert result['bhajans_processed'] == 5
        assert result['tags_migrated'] > 0
        assert result['tags_deleted'] > 0  # Should detect 'test' tags
        
        # Verify no actual changes in database
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Check that bhajan_tags is still empty
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags")
        count = cursor.fetchone()[0]
        assert count == 0
        
        # Check that original tags are unchanged
        cursor.execute("SELECT tags FROM bhajans WHERE id = 1")
        tags = json.loads(cursor.fetchone()[0])
        assert 'hanuman' in tags
        assert 'test' in tags
        
        conn.close()
    
    def test_actual_migration(self, test_db):
        """Test actual migration (with database changes)"""
        result = migrate_bhajan_tags(
            db_path=test_db,
            dry_run=False,
            verbose=True
        )
        
        # Check results
        assert result['status'] == 'success'
        assert result['dry_run'] is False
        assert result['bhajans_processed'] == 5
        assert result['tags_migrated'] > 0
        
        # Verify database changes
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Check bhajan_tags table has records
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags WHERE source = 'MIGRATED'")
        count = cursor.fetchone()[0]
        assert count > 0
        
        # Check Hanuman Chalisa (bhajan_id=1) has correct tags
        cursor.execute("""
            SELECT tt.name 
            FROM bhajan_tags bt
            JOIN tag_taxonomy tt ON bt.tag_id = tt.id
            WHERE bt.bhajan_id = 1 AND bt.source = 'MIGRATED'
        """)
        migrated_tags = [row[0] for row in cursor.fetchall()]
        
        # Should have 'Hanuman', but NOT 'test'
        # (Chalisa not in tag_taxonomy for this test)
        assert 'Hanuman' in migrated_tags or any('hanuman' in t.lower() for t in migrated_tags)
        assert 'test' not in migrated_tags
        
        # Check original tags field is preserved
        cursor.execute("SELECT tags FROM bhajans WHERE id = 1")
        tags = json.loads(cursor.fetchone()[0])
        assert 'hanuman' in tags
        assert 'chalisa' in tags
        assert 'test' in tags  # Original preserved
        
        # Check confidence and source
        cursor.execute("SELECT confidence, source FROM bhajan_tags WHERE bhajan_id = 1 LIMIT 1")
        row = cursor.fetchone()
        assert row[0] == 1.0  # confidence
        assert row[1] == 'MIGRATED'  # source
        
        conn.close()
    
    def test_backward_compatibility(self, test_db):
        """Test that original tags field remains intact"""
        # Migrate
        migrate_bhajan_tags(db_path=test_db, dry_run=False, verbose=False)
        
        # Check all bhajans still have original tags
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, tags FROM bhajans")
        rows = cursor.fetchall()
        
        for bhajan_id, tags_json in rows:
            tags = json.loads(tags_json)
            # Original tags should be preserved
            if bhajan_id == 1:
                assert 'hanuman' in tags
                assert 'test' in tags
            elif bhajan_id == 2:
                assert 'Rama' in tags
        
        conn.close()
    
    def test_duplicate_prevention(self, test_db):
        """Test that running migration twice doesn't create duplicates"""
        # First migration
        migrate_bhajan_tags(db_path=test_db, dry_run=False, verbose=False)
        
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Count tags for bhajan 1
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags WHERE bhajan_id = 1")
        count_first = cursor.fetchone()[0]
        
        conn.close()
        
        # Second migration (should be idempotent)
        migrate_bhajan_tags(db_path=test_db, dry_run=False, verbose=False)
        
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Count should be the same
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags WHERE bhajan_id = 1")
        count_second = cursor.fetchone()[0]
        
        assert count_first == count_second
        
        conn.close()


class TestRollback:
    """Test rollback functionality"""
    
    def test_rollback_migration(self, test_db):
        """Test rollback mode (delete all MIGRATED records)"""
        # First, run migration
        migrate_bhajan_tags(db_path=test_db, dry_run=False, verbose=False)
        
        # Verify records exist
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags WHERE source = 'MIGRATED'")
        count_before = cursor.fetchone()[0]
        assert count_before > 0
        conn.close()
        
        # Now rollback
        result = rollback_migration(db_path=test_db, verbose=True)
        
        assert result['status'] == 'success'
        assert result['records_deleted'] == count_before
        
        # Verify all MIGRATED records are gone
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags WHERE source = 'MIGRATED'")
        count_after = cursor.fetchone()[0]
        assert count_after == 0
        conn.close()
    
    def test_rollback_preserves_original_tags(self, test_db):
        """Test that rollback doesn't affect original tags field"""
        # Migrate then rollback
        migrate_bhajan_tags(db_path=test_db, dry_run=False, verbose=False)
        rollback_migration(db_path=test_db, verbose=False)
        
        # Check original tags are still there
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT tags FROM bhajans WHERE id = 1")
        tags = json.loads(cursor.fetchone()[0])
        
        assert 'hanuman' in tags
        assert 'test' in tags
        
        conn.close()


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_tags_field(self, test_db):
        """Test handling bhajans with empty tags"""
        result = migrate_bhajan_tags(db_path=test_db, dry_run=False, verbose=False)
        
        # Should process bhajan with empty tags without error
        assert result['status'] == 'success'
        assert result['bhajans_processed'] == 5  # Including the empty one
    
    def test_invalid_json_tags(self, test_db):
        """Test handling invalid JSON in tags field"""
        # Insert bhajan with invalid JSON
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO bhajans (id, title, lyrics, tags) VALUES (?, ?, ?, ?)",
            (99, "Bad JSON", "Test", "not-valid-json")
        )
        conn.commit()
        conn.close()
        
        # Should handle gracefully
        result = migrate_bhajan_tags(db_path=test_db, dry_run=False, verbose=False)
        assert result['status'] == 'success'
    
    def test_missing_tag_in_taxonomy(self, test_db):
        """Test handling tags not in tag_taxonomy"""
        # 'chalisa' is in bhajan tags but not in tag_taxonomy
        result = migrate_bhajan_tags(db_path=test_db, dry_run=False, verbose=True)
        
        # Should skip unknown tags gracefully
        assert result['status'] == 'success'
        assert result.get('tags_skipped', 0) > 0


class TestStats:
    """Test statistics reporting"""
    
    def test_migration_stats(self, test_db):
        """Test migration statistics"""
        # Run migration
        migrate_bhajan_tags(db_path=test_db, dry_run=False, verbose=False)
        
        # Get stats
        stats = get_migration_stats(db_path=test_db)
        
        assert 'total_bhajans' in stats
        assert 'total_tags_in_bhajan_tags' in stats
        assert 'migrated_tags' in stats
        assert 'bhajans_with_migrated_tags' in stats
        
        assert stats['total_bhajans'] == 5
        assert stats['migrated_tags'] > 0
        assert stats['bhajans_with_migrated_tags'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
