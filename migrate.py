"""
Database migration script - Safe schema updates
Usage: python migrate.py
"""

import sqlite3
import os

# Ensure data directory exists
os.makedirs("./data", exist_ok=True)
DB_PATH = "./data/portal.db"

def migrate():
    """Run all pending migrations"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if deleted_at column exists
        cursor.execute("PRAGMA table_info(bhajans)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "deleted_at" not in columns:
            print("Adding deleted_at column to bhajans...")
            cursor.execute("""
                ALTER TABLE bhajans 
                ADD COLUMN deleted_at DATETIME DEFAULT NULL
            """)
            conn.commit()
            print("✅ Migration successful - deleted_at column added")
        else:
            print("✅ Schema already up-to-date")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
