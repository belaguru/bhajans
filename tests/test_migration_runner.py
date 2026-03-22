"""
Tests for migration runner
"""
import os
import sqlite3
import tempfile
import shutil
import hashlib
from pathlib import Path
import pytest
import sys

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scripts.run_migrations import (
    MigrationRunner,
    calculate_checksum,
    parse_migration_file,
    get_migration_files
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def temp_migrations_dir():
    """Create a temporary migrations directory with test migrations"""
    temp_dir = tempfile.mkdtemp()
    
    # Create test migration 1
    migration1 = """-- Test Migration 1
CREATE TABLE test_table1 (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100)
);

-- ROLLBACK SECTION
-- DROP TABLE IF EXISTS test_table1;
"""
    Path(temp_dir, "001_test_migration.sql").write_text(migration1)
    
    # Create test migration 2
    migration2 = """-- Test Migration 2
CREATE TABLE test_table2 (
    id INTEGER PRIMARY KEY,
    value TEXT
);

-- ROLLBACK SECTION
-- DROP TABLE IF EXISTS test_table2;
"""
    Path(temp_dir, "002_another_migration.sql").write_text(migration2)
    
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestMigrationRunner:
    """Test MigrationRunner class"""
    
    def test_init_creates_migration_history(self, temp_db):
        """Test that initializing creates migration_history table"""
        runner = MigrationRunner(temp_db, migrations_dir="migrations")
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='migration_history'"
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'migration_history'
    
    def test_get_applied_migrations_empty(self, temp_db):
        """Test getting applied migrations when none exist"""
        runner = MigrationRunner(temp_db, migrations_dir="migrations")
        applied = runner.get_applied_migrations()
        
        assert applied == []
    
    def test_record_migration(self, temp_db):
        """Test recording a migration"""
        runner = MigrationRunner(temp_db, migrations_dir="migrations")
        
        filename = "001_test.sql"
        checksum = "abc123"
        
        runner.record_migration(filename, checksum)
        
        applied = runner.get_applied_migrations()
        assert len(applied) == 1
        assert applied[0]['filename'] == filename
        assert applied[0]['checksum'] == checksum
    
    def test_is_migration_applied(self, temp_db):
        """Test checking if migration is applied"""
        runner = MigrationRunner(temp_db, migrations_dir="migrations")
        
        filename = "001_test.sql"
        checksum = "abc123"
        
        # Not applied yet
        assert not runner.is_migration_applied(filename)
        
        # Apply it
        runner.record_migration(filename, checksum)
        
        # Now it should be applied
        assert runner.is_migration_applied(filename)
    
    def test_verify_checksum(self, temp_db):
        """Test checksum verification"""
        runner = MigrationRunner(temp_db, migrations_dir="migrations")
        
        filename = "001_test.sql"
        original_checksum = "abc123"
        
        runner.record_migration(filename, original_checksum)
        
        # Same checksum should verify
        assert runner.verify_checksum(filename, original_checksum)
        
        # Different checksum should fail
        assert not runner.verify_checksum(filename, "different123")
    
    def test_run_migrations_dry_run(self, temp_db, temp_migrations_dir):
        """Test dry run mode"""
        runner = MigrationRunner(temp_db, migrations_dir=temp_migrations_dir)
        
        result = runner.run_migrations(dry_run=True)
        
        # Dry run should show pending migrations but not apply them
        assert result['dry_run'] is True
        assert len(result['would_apply']) == 2
        assert '001_test_migration.sql' in result['would_apply']
        assert '002_another_migration.sql' in result['would_apply']
        
        # Verify nothing was actually applied
        applied = runner.get_applied_migrations()
        assert len(applied) == 0
    
    def test_run_migrations_applies_pending(self, temp_db, temp_migrations_dir):
        """Test running pending migrations"""
        runner = MigrationRunner(temp_db, migrations_dir=temp_migrations_dir)
        
        result = runner.run_migrations()
        
        assert result['success'] is True
        assert len(result['applied']) == 2
        
        # Verify they were recorded
        applied = runner.get_applied_migrations()
        assert len(applied) == 2
        
        # Verify tables were created
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'test_table1' in tables
        assert 'test_table2' in tables
    
    def test_run_migrations_skips_applied(self, temp_db, temp_migrations_dir):
        """Test that already applied migrations are skipped"""
        runner = MigrationRunner(temp_db, migrations_dir=temp_migrations_dir)
        
        # Apply migrations first time
        result1 = runner.run_migrations()
        assert len(result1['applied']) == 2
        
        # Apply again
        result2 = runner.run_migrations()
        assert len(result2['applied']) == 0
        assert len(result2['skipped']) == 2
    
    def test_get_status(self, temp_db, temp_migrations_dir):
        """Test getting migration status"""
        runner = MigrationRunner(temp_db, migrations_dir=temp_migrations_dir)
        
        # Before applying
        status = runner.get_status()
        assert len(status['pending']) == 2
        assert len(status['applied']) == 0
        
        # Apply first migration manually
        migration_file = os.path.join(temp_migrations_dir, "001_test_migration.sql")
        with open(migration_file) as f:
            sql = f.read()
        
        conn = sqlite3.connect(temp_db)
        conn.executescript(sql)
        conn.close()
        
        checksum = calculate_checksum(migration_file)
        runner.record_migration("001_test_migration.sql", checksum)
        
        # Check status again
        status = runner.get_status()
        assert len(status['pending']) == 1
        assert len(status['applied']) == 1
        assert status['applied'][0]['filename'] == '001_test_migration.sql'
    
    def test_rollback_migration(self, temp_db, temp_migrations_dir):
        """Test rolling back a migration"""
        runner = MigrationRunner(temp_db, migrations_dir=temp_migrations_dir)
        
        # Apply migrations
        runner.run_migrations()
        
        # Verify table exists
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table1'")
        assert cursor.fetchone() is not None
        conn.close()
        
        # Rollback first migration
        result = runner.rollback_migration("001_test_migration.sql")
        
        assert result['success'] is True
        
        # Verify table is gone
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table1'")
        assert cursor.fetchone() is None
        conn.close()
        
        # Verify migration record is removed
        applied = runner.get_applied_migrations()
        filenames = [m['filename'] for m in applied]
        assert '001_test_migration.sql' not in filenames
    
    def test_backup_database(self, temp_db):
        """Test database backup creation"""
        runner = MigrationRunner(temp_db, migrations_dir="migrations")
        
        # Create some data
        conn = sqlite3.connect(temp_db)
        conn.execute("CREATE TABLE test_data (id INTEGER, value TEXT)")
        conn.execute("INSERT INTO test_data VALUES (1, 'test')")
        conn.commit()
        conn.close()
        
        # Create backup
        backup_path = runner.backup_database()
        
        assert os.path.exists(backup_path)
        assert backup_path.endswith('.db')
        
        # Verify backup has the data
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM test_data WHERE id=1")
        result = cursor.fetchone()
        conn.close()
        
        assert result[0] == 'test'
        
        # Cleanup
        os.unlink(backup_path)


class TestHelperFunctions:
    """Test helper functions"""
    
    def test_calculate_checksum(self, temp_migrations_dir):
        """Test calculating file checksum"""
        migration_file = os.path.join(temp_migrations_dir, "001_test_migration.sql")
        
        checksum1 = calculate_checksum(migration_file)
        checksum2 = calculate_checksum(migration_file)
        
        # Same file should produce same checksum
        assert checksum1 == checksum2
        assert len(checksum1) == 64  # SHA256 produces 64 hex chars
    
    def test_parse_migration_file(self, temp_migrations_dir):
        """Test parsing migration file"""
        migration_file = os.path.join(temp_migrations_dir, "001_test_migration.sql")
        
        forward, rollback = parse_migration_file(migration_file)
        
        assert 'CREATE TABLE test_table1' in forward
        assert 'DROP TABLE IF EXISTS test_table1' in rollback
        assert 'ROLLBACK SECTION' not in forward
        assert 'ROLLBACK SECTION' not in rollback
    
    def test_get_migration_files(self, temp_migrations_dir):
        """Test getting sorted migration files"""
        files = get_migration_files(temp_migrations_dir)
        
        assert len(files) == 2
        assert files[0] == '001_test_migration.sql'
        assert files[1] == '002_another_migration.sql'
    
    def test_get_migration_files_filters_non_sql(self, temp_migrations_dir):
        """Test that non-SQL files are filtered out"""
        # Create a non-SQL file
        Path(temp_migrations_dir, "README.md").write_text("# Migrations")
        
        files = get_migration_files(temp_migrations_dir)
        
        # Should only get SQL files
        assert len(files) == 2
        assert all(f.endswith('.sql') for f in files)


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_migration_sql(self, temp_db, temp_migrations_dir):
        """Test handling invalid SQL in migration"""
        # Create migration with invalid SQL
        invalid_migration = """-- Invalid Migration
CREATE INVALID SYNTAX HERE;
"""
        Path(temp_migrations_dir, "003_invalid.sql").write_text(invalid_migration)
        
        runner = MigrationRunner(temp_db, migrations_dir=temp_migrations_dir)
        
        result = runner.run_migrations()
        
        assert result['success'] is False
        assert 'error' in result
        # First two should have applied, third should have failed
        assert len(result.get('applied', [])) == 2
    
    def test_modified_migration_detected(self, temp_db, temp_migrations_dir):
        """Test that modified migrations are detected"""
        runner = MigrationRunner(temp_db, migrations_dir=temp_migrations_dir)
        
        # Apply migrations
        runner.run_migrations()
        
        # Modify a migration file
        migration_file = os.path.join(temp_migrations_dir, "001_test_migration.sql")
        with open(migration_file, 'a') as f:
            f.write("\n-- Modified\n")
        
        # Check status
        status = runner.get_status()
        
        # Should detect the modified migration
        assert len(status.get('modified', [])) > 0
    
    def test_rollback_nonexistent_migration(self, temp_db):
        """Test rolling back a migration that doesn't exist"""
        runner = MigrationRunner(temp_db, migrations_dir="migrations")
        
        result = runner.rollback_migration("999_nonexistent.sql")
        
        assert result['success'] is False
        assert 'not found' in result['error'].lower()
