#!/usr/bin/env python3
"""
Migration: Add mp3_file column to bhajans table
"""
import sqlite3
import os

DB_PATH = "./data/portal.db"

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)

def main():
    print("🔧 Migration: Adding mp3_file column to bhajans table")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        if check_column_exists(cursor, "bhajans", "mp3_file"):
            print("✓ Column mp3_file already exists, skipping migration")
            return True
        
        # Add the column
        print("  Adding mp3_file column...")
        cursor.execute("ALTER TABLE bhajans ADD COLUMN mp3_file TEXT")
        conn.commit()
        
        print("✓ Migration successful!")
        
        # Verify column was added
        if check_column_exists(cursor, "bhajans", "mp3_file"):
            print("✓ Column verified in schema")
            return True
        else:
            print("❌ Column verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
