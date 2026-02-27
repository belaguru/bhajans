#!/usr/bin/env python3
"""
Database Migration Script for Belaguru Bhajan Portal
Run this on fresh deployments or when schema changes
"""
import sqlite3
import sys
from datetime import datetime

def migrate_database(db_path):
    """Migrate database schema"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking database schema...")
        
        # Get current columns
        cursor.execute("PRAGMA table_info(bhajans)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        print(f"✓ Found {len(columns)} columns")
        
        # Add missing columns
        migrations = {
            "tags": "TEXT",
            "uploader_name": "TEXT",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
            "deleted_at": "DATETIME"
        }
        
        for col_name, col_type in migrations.items():
            if col_name not in columns:
                print(f"➕ Adding column: {col_name} ({col_type})")
                cursor.execute(f"ALTER TABLE bhajans ADD COLUMN {col_name} {col_type}")
        
        # Migrate data from old columns to new
        print("\n📊 Migrating data...")
        
        # Migrate tags: manual_tags → tags
        if "manual_tags" in columns and "tags" in columns:
            cursor.execute("""
                UPDATE bhajans 
                SET tags = COALESCE(manual_tags, '')
                WHERE tags = '' OR tags IS NULL
            """)
            print("✓ Migrated manual_tags → tags")
        
        # Set uploader_name if empty
        cursor.execute("""
            UPDATE bhajans 
            SET uploader_name = 'Unknown'
            WHERE uploader_name = '' OR uploader_name IS NULL
        """)
        print("✓ Set default uploader_name")
        
        # Set timestamps if empty
        cursor.execute("""
            UPDATE bhajans 
            SET created_at = DATETIME('now')
            WHERE created_at IS NULL
        """)
        print("✓ Set created_at timestamps")
        
        cursor.execute("""
            UPDATE bhajans 
            SET updated_at = DATETIME('now')
            WHERE updated_at IS NULL
        """)
        print("✓ Set updated_at timestamps")
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM bhajans")
        bhajan_count = cursor.fetchone()[0]
        print(f"\n✅ Total Bhajans in database: {bhajan_count}")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Migration complete!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "./data/portal.db"
    print(f"Migrating database: {db_path}\n")
    success = migrate_database(db_path)
    sys.exit(0 if success else 1)
