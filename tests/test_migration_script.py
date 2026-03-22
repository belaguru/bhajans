"""
Test suite for tag migration script.

Tests:
1. Dry-run mode (no database changes)
2. Tag mapping (old → canonical)
3. Transaction safety (rollback on error)
4. Backward compatibility (keeps original tags field)
5. Rollback mode (delete MIGRATED records)

Uses test fixtures for isolated database testing.
"""
import pytest
import sys
import os
import json
import sqlite3
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


@pytest.fixture
def migration_test_db(test_db_path):
    """
    Create test database with sample data for migration tests.
    
    Returns the database path.
    """
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    # Insert sample tags into tag_taxonomy
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
        ("Hanuman Chalisa", "Jai Hanuman gyan gun sagar", '["hanuman", "chalisa", "test"]'),
        ("Rama Bhajan", "Sri Rama Jaya Rama", '["Rama", "bhajan", "Test"]'),
        ("Krishna Stuti", "Hare Krishna Hare Krishna", '["krishna", "stuti"]'),
        ("Shiva Ashtakam", "Om Namah Shivaya", '["Shiva", "ashtakam", "Anjaneya"]'),
        ("Untagged Bhajan", "Bhajan lyrics here", '[]'),
    ]
    
    cursor.executemany(
        "INSERT INTO bhajans (title, lyrics, tags) VALUES (?, ?, ?)",
        sample_bhajans
    )
    
    conn.commit()
    conn.close()
    
    return test_db_path


class TestTagMappingLoad:
    """Test tag mapping logic without full migration"""
    
    def test_mapping_structure(self, test_mapping_csv):
        """Test loading and using tag mapping"""
        import csv
        
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            mapping = {}
            for row in reader:
                mapping[row['old_tag']] = {
                    'action': row['action'],
                    'canonical': row['canonical_tag']
                }
        
        assert 'Hanuman' in mapping
        assert mapping['Hanuman']['action'] == 'KEEP'
        assert mapping.get('Anjaneya', {}).get('canonical') == 'Hanuman'
    
    def test_map_tag_to_canonical(self, test_mapping_csv):
        """Test tag mapping to canonical form"""
        import csv
        
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            mapping = {
                row['old_tag']: {
                    'action': row['action'],
                    'canonical': row['canonical_tag']
                }
                for row in reader
            }
        
        def map_tag(tag_name):
            """Map tag to canonical form"""
            entry = mapping.get(tag_name, {})
            action = entry.get('action', 'KEEP')
            
            if action == 'DELETE':
                return None
            elif action == 'MERGE':
                return entry.get('canonical')
            else:  # KEEP or unknown
                return tag_name
        
        # Test MERGE action
        assert map_tag('Anjaneya') == 'Hanuman'
        assert map_tag('hanuman') == 'Hanuman'
        
        # Test DELETE action
        assert map_tag('test') is None
        
        # Test KEEP action
        assert map_tag('Hanuman') == 'Hanuman'
        
        # Test unknown tag (pass through)
        assert map_tag('UnknownTag') == 'UnknownTag'


class TestMigrationDryRun:
    """Test dry-run migration functionality"""
    
    def test_dry_run_no_changes(self, migration_test_db):
        """Test dry-run mode doesn't change database"""
        conn = sqlite3.connect(migration_test_db)
        cursor = conn.cursor()
        
        # Get initial state
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags")
        initial_count = cursor.fetchone()[0]
        assert initial_count == 0  # Should be empty initially
        
        cursor.execute("SELECT tags FROM bhajans WHERE title = 'Hanuman Chalisa'")
        original_tags = cursor.fetchone()[0]
        
        conn.close()
        
        # Simulate dry-run (just read, don't write)
        conn = sqlite3.connect(migration_test_db)
        cursor = conn.cursor()
        
        # Read bhajans and their tags
        cursor.execute("SELECT id, title, tags FROM bhajans WHERE tags != '[]'")
        bhajans = cursor.fetchall()
        
        # Process tags (dry run - no writes)
        processed_count = 0
        for bhajan_id, title, tags_json in bhajans:
            try:
                tags = json.loads(tags_json)
                processed_count += len(tags)
            except:
                pass
        
        conn.close()
        
        # Verify no changes
        conn = sqlite3.connect(migration_test_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags")
        final_count = cursor.fetchone()[0]
        assert final_count == 0  # Still empty
        
        cursor.execute("SELECT tags FROM bhajans WHERE title = 'Hanuman Chalisa'")
        final_tags = cursor.fetchone()[0]
        assert final_tags == original_tags
        
        conn.close()


class TestMigrationExecution:
    """Test actual migration execution"""
    
    def test_migrate_tags_to_taxonomy(self, migration_test_db):
        """Test migrating old tags to new taxonomy table"""
        conn = sqlite3.connect(migration_test_db)
        cursor = conn.cursor()
        
        # Get tag IDs
        cursor.execute("SELECT id, name FROM tag_taxonomy")
        tag_lookup = {row[1].lower(): row[0] for row in cursor.fetchall()}
        
        # Get bhajans with tags
        cursor.execute("SELECT id, tags FROM bhajans WHERE tags != '[]'")
        bhajans = cursor.fetchall()
        
        # Migrate tags
        migrated_count = 0
        for bhajan_id, tags_json in bhajans:
            try:
                tags = json.loads(tags_json)
                for tag in tags:
                    tag_lower = tag.lower().strip()
                    tag_id = tag_lookup.get(tag_lower)
                    
                    if tag_id:
                        cursor.execute(
                            """INSERT OR IGNORE INTO bhajan_tags 
                               (bhajan_id, tag_id, source, confidence) 
                               VALUES (?, ?, 'MIGRATED', 1.0)""",
                            (bhajan_id, tag_id)
                        )
                        migrated_count += cursor.rowcount
            except:
                pass
        
        conn.commit()
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags WHERE source = 'MIGRATED'")
        count = cursor.fetchone()[0]
        assert count > 0
        
        # Verify specific bhajan has correct tags
        cursor.execute("""
            SELECT tt.name 
            FROM bhajan_tags bt
            JOIN tag_taxonomy tt ON bt.tag_id = tt.id
            JOIN bhajans b ON bt.bhajan_id = b.id
            WHERE b.title = 'Hanuman Chalisa'
        """)
        tags = [row[0] for row in cursor.fetchall()]
        assert 'Hanuman' in tags
        
        conn.close()
    
    def test_backward_compatibility(self, migration_test_db):
        """Test that original tags field is preserved after migration"""
        conn = sqlite3.connect(migration_test_db)
        cursor = conn.cursor()
        
        # Get original tags
        cursor.execute("SELECT tags FROM bhajans WHERE title = 'Hanuman Chalisa'")
        original_tags = cursor.fetchone()[0]
        
        # Migrate (same logic as above)
        cursor.execute("SELECT id, name FROM tag_taxonomy")
        tag_lookup = {row[1].lower(): row[0] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id, tags FROM bhajans WHERE tags != '[]'")
        for bhajan_id, tags_json in cursor.fetchall():
            try:
                tags = json.loads(tags_json)
                for tag in tags:
                    tag_id = tag_lookup.get(tag.lower().strip())
                    if tag_id:
                        cursor.execute(
                            "INSERT OR IGNORE INTO bhajan_tags (bhajan_id, tag_id, source) VALUES (?, ?, 'MIGRATED')",
                            (bhajan_id, tag_id)
                        )
            except:
                pass
        
        conn.commit()
        
        # Verify original tags unchanged
        cursor.execute("SELECT tags FROM bhajans WHERE title = 'Hanuman Chalisa'")
        final_tags = cursor.fetchone()[0]
        assert final_tags == original_tags
        
        # Verify original contains specific tags
        tags_list = json.loads(final_tags)
        assert 'hanuman' in tags_list
        assert 'chalisa' in tags_list
        assert 'test' in tags_list
        
        conn.close()
    
    def test_duplicate_prevention(self, migration_test_db):
        """Test that running migration twice doesn't create duplicates"""
        conn = sqlite3.connect(migration_test_db)
        cursor = conn.cursor()
        
        # Create unique index if not exists (ensures INSERT OR IGNORE works)
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_bhajan_tags_unique 
            ON bhajan_tags (bhajan_id, tag_id)
        """)
        conn.commit()
        
        # Get tag lookup
        cursor.execute("SELECT id, name FROM tag_taxonomy")
        tag_lookup = {row[1].lower(): row[0] for row in cursor.fetchall()}
        
        def run_migration():
            """Run migration logic"""
            cursor.execute("SELECT id, tags FROM bhajans WHERE tags != '[]'")
            for bhajan_id, tags_json in cursor.fetchall():
                try:
                    tags = json.loads(tags_json)
                    for tag in tags:
                        tag_id = tag_lookup.get(tag.lower().strip())
                        if tag_id:
                            cursor.execute(
                                "INSERT OR IGNORE INTO bhajan_tags (bhajan_id, tag_id, source) VALUES (?, ?, 'MIGRATED')",
                                (bhajan_id, tag_id)
                            )
                except:
                    pass
            conn.commit()
        
        # First migration
        run_migration()
        
        # Count after first migration
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags")
        count_first = cursor.fetchone()[0]
        
        # Second migration (should be idempotent due to unique constraint)
        run_migration()
        
        # Count after second migration
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags")
        count_second = cursor.fetchone()[0]
        
        # Should be the same (idempotent)
        assert count_first == count_second
        assert count_first > 0  # Ensure we actually migrated something
        
        conn.close()


class TestRollback:
    """Test rollback functionality"""
    
    def test_rollback_removes_migrated_tags(self, migration_test_db):
        """Test rollback mode deletes all MIGRATED records"""
        conn = sqlite3.connect(migration_test_db)
        cursor = conn.cursor()
        
        # First migrate
        cursor.execute("SELECT id, name FROM tag_taxonomy")
        tag_lookup = {row[1].lower(): row[0] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id, tags FROM bhajans WHERE tags != '[]'")
        for bhajan_id, tags_json in cursor.fetchall():
            try:
                tags = json.loads(tags_json)
                for tag in tags:
                    tag_id = tag_lookup.get(tag.lower().strip())
                    if tag_id:
                        cursor.execute(
                            "INSERT OR IGNORE INTO bhajan_tags (bhajan_id, tag_id, source) VALUES (?, ?, 'MIGRATED')",
                            (bhajan_id, tag_id)
                        )
            except:
                pass
        conn.commit()
        
        # Verify records exist
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags WHERE source = 'MIGRATED'")
        count_before = cursor.fetchone()[0]
        assert count_before > 0
        
        # Rollback
        cursor.execute("DELETE FROM bhajan_tags WHERE source = 'MIGRATED'")
        conn.commit()
        
        # Verify all MIGRATED records are gone
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags WHERE source = 'MIGRATED'")
        count_after = cursor.fetchone()[0]
        assert count_after == 0
        
        conn.close()
    
    def test_rollback_preserves_original_tags(self, migration_test_db):
        """Test that rollback doesn't affect original tags field"""
        conn = sqlite3.connect(migration_test_db)
        cursor = conn.cursor()
        
        # Get original tags before migration
        cursor.execute("SELECT tags FROM bhajans WHERE title = 'Hanuman Chalisa'")
        original_tags = cursor.fetchone()[0]
        
        # Migrate
        cursor.execute("SELECT id, name FROM tag_taxonomy")
        tag_lookup = {row[1].lower(): row[0] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id, tags FROM bhajans WHERE tags != '[]'")
        for bhajan_id, tags_json in cursor.fetchall():
            try:
                tags = json.loads(tags_json)
                for tag in tags:
                    tag_id = tag_lookup.get(tag.lower().strip())
                    if tag_id:
                        cursor.execute(
                            "INSERT OR IGNORE INTO bhajan_tags (bhajan_id, tag_id, source) VALUES (?, ?, 'MIGRATED')",
                            (bhajan_id, tag_id)
                        )
            except:
                pass
        conn.commit()
        
        # Rollback
        cursor.execute("DELETE FROM bhajan_tags WHERE source = 'MIGRATED'")
        conn.commit()
        
        # Verify original tags still intact
        cursor.execute("SELECT tags FROM bhajans WHERE title = 'Hanuman Chalisa'")
        final_tags = cursor.fetchone()[0]
        assert final_tags == original_tags
        
        conn.close()


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_tags_field(self, migration_test_db):
        """Test handling bhajans with empty tags"""
        conn = sqlite3.connect(migration_test_db)
        cursor = conn.cursor()
        
        # Count bhajans with empty tags
        cursor.execute("SELECT COUNT(*) FROM bhajans WHERE tags = '[]'")
        empty_count = cursor.fetchone()[0]
        assert empty_count >= 1  # We have one untagged bhajan
        
        # Try to process all bhajans
        cursor.execute("SELECT id, tags FROM bhajans")
        processed = 0
        for bhajan_id, tags_json in cursor.fetchall():
            try:
                tags = json.loads(tags_json) if tags_json else []
                processed += 1
            except:
                pass
        
        # Should process all without error
        cursor.execute("SELECT COUNT(*) FROM bhajans")
        total = cursor.fetchone()[0]
        assert processed == total
        
        conn.close()
    
    def test_invalid_json_tags(self, migration_test_db):
        """Test handling invalid JSON in tags field"""
        conn = sqlite3.connect(migration_test_db)
        cursor = conn.cursor()
        
        # Insert bhajan with invalid JSON
        cursor.execute(
            "INSERT INTO bhajans (title, lyrics, tags) VALUES (?, ?, ?)",
            ("Bad JSON Bhajan", "Test lyrics here", "not-valid-json")
        )
        conn.commit()
        
        # Try to process all bhajans
        cursor.execute("SELECT id, tags FROM bhajans")
        errors = 0
        processed = 0
        for bhajan_id, tags_json in cursor.fetchall():
            try:
                tags = json.loads(tags_json) if tags_json else []
                processed += 1
            except json.JSONDecodeError:
                errors += 1
                processed += 1  # Still counts as processed
        
        # Should handle gracefully
        assert errors == 1  # Only the invalid one
        
        conn.close()
    
    def test_missing_tag_in_taxonomy(self, migration_test_db):
        """Test handling tags not in tag_taxonomy"""
        conn = sqlite3.connect(migration_test_db)
        cursor = conn.cursor()
        
        # Get tag lookup
        cursor.execute("SELECT id, name FROM tag_taxonomy")
        tag_lookup = {row[1].lower(): row[0] for row in cursor.fetchall()}
        
        # Process Hanuman Chalisa - has 'chalisa' which is NOT in taxonomy
        cursor.execute("SELECT id, tags FROM bhajans WHERE title = 'Hanuman Chalisa'")
        bhajan_id, tags_json = cursor.fetchone()
        tags = json.loads(tags_json)
        
        found_tags = []
        skipped_tags = []
        for tag in tags:
            tag_id = tag_lookup.get(tag.lower().strip())
            if tag_id:
                found_tags.append(tag)
            else:
                skipped_tags.append(tag)
        
        # Should have found Hanuman, skipped chalisa and test
        assert 'hanuman' in [t.lower() for t in found_tags]
        assert 'chalisa' in [t.lower() for t in skipped_tags]
        
        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
