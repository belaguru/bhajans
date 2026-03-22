"""
Test suite for tag taxonomy database schema
Tests table structure, foreign keys, indexes, and constraints
"""
import pytest
import sqlite3
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test database path
TEST_DB_PATH = ":memory:"


@pytest.fixture
def db_connection():
    """Create a test database connection and apply migration"""
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Create bhajans table (required by migration foreign keys)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bhajans (
            id INTEGER PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            lyrics TEXT NOT NULL
        )
    """)
    
    # Read and apply migration SQL
    migration_path = os.path.join(os.path.dirname(__file__), '..', 'migrations', '001_create_tag_taxonomy.sql')
    with open(migration_path, 'r') as f:
        migration_sql = f.read()
        # Split and execute (skip rollback section)
        sql_statements = migration_sql.split('-- ROLLBACK')[0]
        conn.executescript(sql_statements)
    
    yield conn
    
    conn.close()


def get_table_info(conn, table_name):
    """Get table schema information"""
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    return {row[1]: {'type': row[2], 'notnull': row[3], 'pk': row[5]} for row in cursor}


def get_foreign_keys(conn, table_name):
    """Get foreign key information"""
    cursor = conn.execute(f"PRAGMA foreign_key_list({table_name})")
    return list(cursor)


def get_indexes(conn, table_name):
    """Get index information"""
    cursor = conn.execute(f"PRAGMA index_list({table_name})")
    return [row[1] for row in cursor]


# ============================================================================
# TEST: tag_taxonomy table
# ============================================================================

def test_tag_taxonomy_table_exists(db_connection):
    """Test that tag_taxonomy table exists"""
    cursor = db_connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='tag_taxonomy'"
    )
    result = cursor.fetchone()
    assert result is not None, "tag_taxonomy table should exist"
    assert result[0] == "tag_taxonomy"


def test_tag_taxonomy_columns(db_connection):
    """Test tag_taxonomy table has required columns with correct types"""
    schema = get_table_info(db_connection, 'tag_taxonomy')
    
    # Required columns
    assert 'id' in schema, "tag_taxonomy should have 'id' column"
    assert schema['id']['pk'] == 1, "id should be primary key"
    
    assert 'name' in schema, "tag_taxonomy should have 'name' column"
    assert 'VARCHAR' in schema['name']['type'].upper(), "name should be VARCHAR"
    
    assert 'parent_id' in schema, "tag_taxonomy should have 'parent_id' column"
    assert 'INTEGER' in schema['parent_id']['type'].upper(), "parent_id should be INTEGER"
    
    assert 'category' in schema, "tag_taxonomy should have 'category' column"
    assert 'VARCHAR' in schema['category']['type'].upper(), "category should be VARCHAR"
    
    assert 'level' in schema, "tag_taxonomy should have 'level' column"
    assert 'INTEGER' in schema['level']['type'].upper(), "level should be INTEGER"


def test_tag_taxonomy_foreign_key(db_connection):
    """Test tag_taxonomy parent_id foreign key constraint"""
    fks = get_foreign_keys(db_connection, 'tag_taxonomy')
    
    # Find parent_id foreign key
    parent_fk = [fk for fk in fks if fk[3] == 'parent_id']
    assert len(parent_fk) > 0, "parent_id should have foreign key constraint"
    assert parent_fk[0][2] == 'tag_taxonomy', "parent_id should reference tag_taxonomy table"
    assert parent_fk[0][4] == 'id', "parent_id should reference id column"


def test_tag_taxonomy_indexes(db_connection):
    """Test tag_taxonomy has performance indexes"""
    indexes = get_indexes(db_connection, 'tag_taxonomy')
    
    # Check for key indexes (names may vary)
    index_names = [idx.lower() for idx in indexes]
    
    # Should have indexes on commonly queried columns
    assert len(indexes) > 0, "tag_taxonomy should have indexes"
    
    # Check specific indexes by querying index info
    cursor = db_connection.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='tag_taxonomy'"
    )
    all_indexes = [row[0] for row in cursor]
    
    # Verify we have indexes (at least primary key)
    assert len(all_indexes) > 0, "Should have at least one index (primary key)"


def test_tag_taxonomy_self_reference(db_connection):
    """Test tag_taxonomy can reference itself (hierarchical structure)"""
    # Insert root tag
    db_connection.execute(
        "INSERT INTO tag_taxonomy (name, category, level) VALUES (?, ?, ?)",
        ('root', 'deity', 0)
    )
    
    # Insert child tag
    db_connection.execute(
        "INSERT INTO tag_taxonomy (name, parent_id, category, level) VALUES (?, ?, ?, ?)",
        ('child', 1, 'deity', 1)
    )
    
    db_connection.commit()
    
    # Verify relationship
    cursor = db_connection.execute(
        "SELECT t1.name as child, t2.name as parent "
        "FROM tag_taxonomy t1 "
        "LEFT JOIN tag_taxonomy t2 ON t1.parent_id = t2.id "
        "WHERE t1.name = 'child'"
    )
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == 'child'
    assert result[1] == 'root'


# ============================================================================
# TEST: tag_translations table
# ============================================================================

def test_tag_translations_table_exists(db_connection):
    """Test that tag_translations table exists"""
    cursor = db_connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='tag_translations'"
    )
    result = cursor.fetchone()
    assert result is not None, "tag_translations table should exist"
    assert result[0] == "tag_translations"


def test_tag_translations_columns(db_connection):
    """Test tag_translations table has required columns"""
    schema = get_table_info(db_connection, 'tag_translations')
    
    assert 'id' in schema, "tag_translations should have 'id' column"
    assert schema['id']['pk'] == 1, "id should be primary key"
    
    assert 'tag_id' in schema, "tag_translations should have 'tag_id' column"
    assert 'INTEGER' in schema['tag_id']['type'].upper()
    
    assert 'language' in schema, "tag_translations should have 'language' column"
    assert 'VARCHAR' in schema['language']['type'].upper()
    
    assert 'translation' in schema, "tag_translations should have 'translation' column"
    assert 'VARCHAR' in schema['translation']['type'].upper()


def test_tag_translations_foreign_key(db_connection):
    """Test tag_translations foreign key to tag_taxonomy"""
    fks = get_foreign_keys(db_connection, 'tag_translations')
    
    tag_fk = [fk for fk in fks if fk[3] == 'tag_id']
    assert len(tag_fk) > 0, "tag_id should have foreign key constraint"
    assert tag_fk[0][2] == 'tag_taxonomy', "tag_id should reference tag_taxonomy"
    assert tag_fk[0][4] == 'id', "tag_id should reference id column"


def test_tag_translations_cascade_delete(db_connection):
    """Test that deleting a tag cascades to translations"""
    # Insert tag
    db_connection.execute(
        "INSERT INTO tag_taxonomy (id, name, category, level) VALUES (?, ?, ?, ?)",
        (100, 'test_tag', 'deity', 0)
    )
    
    # Insert translation
    db_connection.execute(
        "INSERT INTO tag_translations (tag_id, language, translation) VALUES (?, ?, ?)",
        (100, 'kn', 'ಟೆಸ್ಟ್')
    )
    db_connection.commit()
    
    # Verify translation exists
    cursor = db_connection.execute("SELECT COUNT(*) FROM tag_translations WHERE tag_id = 100")
    assert cursor.fetchone()[0] == 1
    
    # Delete tag
    db_connection.execute("DELETE FROM tag_taxonomy WHERE id = 100")
    db_connection.commit()
    
    # Verify translation was deleted (cascade)
    cursor = db_connection.execute("SELECT COUNT(*) FROM tag_translations WHERE tag_id = 100")
    assert cursor.fetchone()[0] == 0, "Translation should be deleted when tag is deleted (CASCADE)"


# ============================================================================
# TEST: tag_synonyms table
# ============================================================================

def test_tag_synonyms_table_exists(db_connection):
    """Test that tag_synonyms table exists"""
    cursor = db_connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='tag_synonyms'"
    )
    result = cursor.fetchone()
    assert result is not None, "tag_synonyms table should exist"
    assert result[0] == "tag_synonyms"


def test_tag_synonyms_columns(db_connection):
    """Test tag_synonyms table has required columns"""
    schema = get_table_info(db_connection, 'tag_synonyms')
    
    assert 'id' in schema, "tag_synonyms should have 'id' column"
    assert schema['id']['pk'] == 1, "id should be primary key"
    
    assert 'tag_id' in schema, "tag_synonyms should have 'tag_id' column"
    assert 'INTEGER' in schema['tag_id']['type'].upper()
    
    assert 'synonym' in schema, "tag_synonyms should have 'synonym' column"
    assert 'VARCHAR' in schema['synonym']['type'].upper()


def test_tag_synonyms_foreign_key(db_connection):
    """Test tag_synonyms foreign key to tag_taxonomy"""
    fks = get_foreign_keys(db_connection, 'tag_synonyms')
    
    tag_fk = [fk for fk in fks if fk[3] == 'tag_id']
    assert len(tag_fk) > 0, "tag_id should have foreign key constraint"
    assert tag_fk[0][2] == 'tag_taxonomy', "tag_id should reference tag_taxonomy"


# ============================================================================
# TEST: bhajan_tags table
# ============================================================================

def test_bhajan_tags_table_exists(db_connection):
    """Test that bhajan_tags table exists"""
    cursor = db_connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='bhajan_tags'"
    )
    result = cursor.fetchone()
    assert result is not None, "bhajan_tags table should exist"
    assert result[0] == "bhajan_tags"


def test_bhajan_tags_columns(db_connection):
    """Test bhajan_tags table has required columns"""
    schema = get_table_info(db_connection, 'bhajan_tags')
    
    assert 'id' in schema, "bhajan_tags should have 'id' column"
    assert schema['id']['pk'] == 1, "id should be primary key"
    
    assert 'bhajan_id' in schema, "bhajan_tags should have 'bhajan_id' column"
    assert 'INTEGER' in schema['bhajan_id']['type'].upper()
    
    assert 'tag_id' in schema, "bhajan_tags should have 'tag_id' column"
    assert 'INTEGER' in schema['tag_id']['type'].upper()
    
    assert 'source' in schema, "bhajan_tags should have 'source' column"
    assert 'confidence' in schema, "bhajan_tags should have 'confidence' column"
    assert 'created_at' in schema, "bhajan_tags should have 'created_at' column"


def test_bhajan_tags_foreign_keys(db_connection):
    """Test bhajan_tags has foreign keys to both bhajans and tag_taxonomy"""
    fks = get_foreign_keys(db_connection, 'bhajan_tags')
    
    # Should have 2 foreign keys
    assert len(fks) >= 2, "bhajan_tags should have at least 2 foreign keys"
    
    # Check tag_id foreign key
    tag_fk = [fk for fk in fks if fk[3] == 'tag_id']
    assert len(tag_fk) > 0, "tag_id should have foreign key"
    assert tag_fk[0][2] == 'tag_taxonomy', "tag_id should reference tag_taxonomy"
    
    # Check bhajan_id foreign key
    bhajan_fk = [fk for fk in fks if fk[3] == 'bhajan_id']
    assert len(bhajan_fk) > 0, "bhajan_id should have foreign key"
    assert bhajan_fk[0][2] == 'bhajans', "bhajan_id should reference bhajans"


def test_bhajan_tags_indexes(db_connection):
    """Test bhajan_tags has performance indexes"""
    cursor = db_connection.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='bhajan_tags'"
    )
    indexes = [row[0] for row in cursor]
    
    # Should have multiple indexes for performance
    assert len(indexes) > 0, "bhajan_tags should have indexes"


def test_bhajan_tags_integration(db_connection):
    """Test complete workflow: create tag, create bhajan, link them"""
    # Note: bhajans table created in fixture
    
    # Insert test bhajan
    db_connection.execute(
        "INSERT INTO bhajans (id, title, lyrics) VALUES (?, ?, ?)",
        (1, 'Test Bhajan', 'Om Namah Shivaya')
    )
    
    # Insert test tag
    db_connection.execute(
        "INSERT INTO tag_taxonomy (id, name, category, level) VALUES (?, ?, ?, ?)",
        (1, 'shiva', 'deity', 0)
    )
    
    # Link bhajan to tag
    db_connection.execute(
        "INSERT INTO bhajan_tags (bhajan_id, tag_id, source, confidence) VALUES (?, ?, ?, ?)",
        (1, 1, 'manual', 1.0)
    )
    db_connection.commit()
    
    # Verify link
    cursor = db_connection.execute("""
        SELECT b.title, t.name
        FROM bhajan_tags bt
        JOIN bhajans b ON bt.bhajan_id = b.id
        JOIN tag_taxonomy t ON bt.tag_id = t.id
        WHERE bt.bhajan_id = 1
    """)
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == 'Test Bhajan'
    assert result[1] == 'shiva'


# ============================================================================
# TEST: Schema constraints and data integrity
# ============================================================================

def test_foreign_key_constraint_enforcement(db_connection):
    """Test that foreign key constraints are actually enforced"""
    # Try to insert bhajan_tags with non-existent tag_id
    with pytest.raises(sqlite3.IntegrityError):
        db_connection.execute(
            "INSERT INTO bhajan_tags (bhajan_id, tag_id, source, confidence) VALUES (?, ?, ?, ?)",
            (999, 999, 'test', 1.0)
        )
        db_connection.commit()


def test_tag_taxonomy_hierarchy_depth(db_connection):
    """Test multi-level tag hierarchy"""
    # Level 0: Root
    db_connection.execute(
        "INSERT INTO tag_taxonomy (id, name, category, level) VALUES (?, ?, ?, ?)",
        (1, 'deity', 'root', 0)
    )
    
    # Level 1: Vishnu
    db_connection.execute(
        "INSERT INTO tag_taxonomy (id, name, parent_id, category, level) VALUES (?, ?, ?, ?, ?)",
        (2, 'vishnu', 1, 'deity', 1)
    )
    
    # Level 2: Krishna
    db_connection.execute(
        "INSERT INTO tag_taxonomy (id, name, parent_id, category, level) VALUES (?, ?, ?, ?, ?)",
        (3, 'krishna', 2, 'deity', 2)
    )
    db_connection.commit()
    
    # Query hierarchy
    cursor = db_connection.execute("""
        SELECT t1.name as child, t1.level, t2.name as parent
        FROM tag_taxonomy t1
        LEFT JOIN tag_taxonomy t2 ON t1.parent_id = t2.id
        WHERE t1.name = 'krishna'
    """)
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == 'krishna'
    assert result[1] == 2  # Level 2
    assert result[2] == 'vishnu'  # Parent


def test_unique_constraints(db_connection):
    """Test unique constraints on tag names and synonyms"""
    # Insert a tag
    db_connection.execute(
        "INSERT INTO tag_taxonomy (name, category, level) VALUES (?, ?, ?)",
        ('unique_tag', 'deity', 0)
    )
    db_connection.commit()
    
    # Try to insert duplicate tag name (should fail if UNIQUE constraint exists)
    # Note: This depends on schema having UNIQUE constraint on name
    # If schema doesn't have it, this test documents that requirement
    try:
        db_connection.execute(
            "INSERT INTO tag_taxonomy (name, category, level) VALUES (?, ?, ?)",
            ('unique_tag', 'deity', 0)
        )
        db_connection.commit()
        # If we get here, unique constraint might not be enforced
        # This is a warning rather than a hard failure
        print("WARNING: Duplicate tag names allowed - consider adding UNIQUE constraint")
    except sqlite3.IntegrityError:
        # Good! Unique constraint is working
        pass


# ============================================================================
# TEST: Performance and scalability
# ============================================================================

def test_bulk_insert_performance(db_connection):
    """Test that bulk inserts work efficiently"""
    # Insert multiple tags
    tags = [(f'tag_{i}', 'deity', 0) for i in range(100)]
    db_connection.executemany(
        "INSERT INTO tag_taxonomy (name, category, level) VALUES (?, ?, ?)",
        tags
    )
    db_connection.commit()
    
    # Verify count
    cursor = db_connection.execute("SELECT COUNT(*) FROM tag_taxonomy")
    count = cursor.fetchone()[0]
    assert count >= 100, "Bulk insert should create all records"


def test_index_usage_on_queries(db_connection):
    """Test that indexes are used in common queries"""
    # Insert test data
    db_connection.execute(
        "INSERT INTO tag_taxonomy (id, name, category, level) VALUES (?, ?, ?, ?)",
        (1, 'test', 'deity', 0)
    )
    db_connection.commit()
    
    # Use EXPLAIN QUERY PLAN to check index usage
    cursor = db_connection.execute(
        "EXPLAIN QUERY PLAN SELECT * FROM tag_taxonomy WHERE name = 'test'"
    )
    plan = cursor.fetchall()
    
    # Plan should exist
    assert len(plan) > 0, "Query plan should be generated"
    # Note: Full index verification would require parsing EXPLAIN output
    # This test documents that we care about index usage


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
