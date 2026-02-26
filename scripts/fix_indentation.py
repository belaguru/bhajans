#!/usr/bin/env python3

"""
Fix indentation in existing bhajans
Trims leading whitespace from each line
"""

import sys
sys.path.insert(0, '/home/kreddy/Projects/belaguru-portal')

from models import Bhajan, SessionLocal

def fix_indentation():
    """Clean up indentation in all existing bhajans"""
    db = SessionLocal()
    
    try:
        bhajans = db.query(Bhajan).all()
        
        if not bhajans:
            print("✅ No bhajans to fix")
            return
        
        fixed_count = 0
        
        for bhajan in bhajans:
            # Clean lyrics: trim leading whitespace from each line
            cleaned_lyrics = "\n".join(line.lstrip() for line in bhajan.lyrics.split("\n"))
            
            if cleaned_lyrics != bhajan.lyrics:
                bhajan.lyrics = cleaned_lyrics
                fixed_count += 1
        
        if fixed_count > 0:
            db.commit()
            print(f"✅ Fixed indentation in {fixed_count}/{len(bhajans)} bhajans")
        else:
            print(f"✅ All {len(bhajans)} bhajans already clean")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_indentation()
