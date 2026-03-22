#!/usr/bin/env python3
"""Run auto-tagger on all untagged bhajans"""
import sqlite3
import json
import sys
sys.path.insert(0, '.')
from scripts.auto_tag import auto_tag

def main():
    conn = sqlite3.connect('data/portal.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get untagged bhajans
    cursor.execute("""
        SELECT id, title, lyrics, tags 
        FROM bhajans 
        WHERE tags IS NULL OR tags = '' OR tags = '[]'
    """)
    untagged = cursor.fetchall()
    print(f"Found {len(untagged)} untagged bhajans\n")
    
    dry_run = '--dry-run' in sys.argv
    updated = 0
    
    for bhajan in untagged:
        # auto_tag returns {tag: confidence, ...}
        result = auto_tag({"title": bhajan['title'], "lyrics": bhajan['lyrics']})
        
        if result:
            # Get tags with confidence > 0.5
            tag_names = [tag for tag, conf in result.items() if conf >= 0.5]
            
            if tag_names:
                print(f"[{bhajan['id']}] {bhajan['title'][:50]}...")
                print(f"    Tags: {tag_names}")
                print(f"    Confidences: {dict((k, f'{v:.0%}') for k, v in result.items())}")
                
                updated += 1
                if not dry_run:
                    cursor.execute(
                        "UPDATE bhajans SET tags = ? WHERE id = ?",
                        (json.dumps(tag_names), bhajan['id'])
                    )
                print()
    
    if not dry_run:
        conn.commit()
        print(f"\n✅ Updated {updated} bhajans with auto-generated tags")
    else:
        print(f"\n[DRY RUN] Would update {updated} bhajans")
    
    conn.close()

if __name__ == "__main__":
    main()
