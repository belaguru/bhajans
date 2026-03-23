#!/usr/bin/env python3
"""
Add Day-of-Week Tag Category
Creates day tags with Kannada translations and applies them based on deity associations
"""

import sqlite3
from datetime import datetime

def main():
    conn = sqlite3.connect('data/portal.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("ADDING DAY-OF-WEEK TAG CATEGORY")
    print("=" * 80)
    print()
    
    # Get current max tag ID
    max_id = cursor.execute('SELECT MAX(id) FROM tag_taxonomy').fetchone()[0]
    print(f"Current max tag ID: {max_id}")
    
    # Define day tags (starting from max_id + 1)
    day_tags = [
        {
            'id': max_id + 1,
            'name': 'Monday',
            'name_kn': 'ಸೋಮವಾರ',
            'category': 'day',
            'level': 0,
            'keywords': ['somavara', 'monday', 'ಸೋಮವಾರ']
        },
        {
            'id': max_id + 2,
            'name': 'Tuesday',
            'name_kn': 'ಮಂಗಳವಾರ',
            'category': 'day',
            'level': 0,
            'keywords': ['mangalavara', 'tuesday', 'ಮಂಗಳವಾರ']
        },
        {
            'id': max_id + 3,
            'name': 'Wednesday',
            'name_kn': 'ಬುಧವಾರ',
            'category': 'day',
            'level': 0,
            'keywords': ['budhavara', 'wednesday', 'ಬುಧವಾರ']
        },
        {
            'id': max_id + 4,
            'name': 'Thursday',
            'name_kn': 'ಗುರುವಾರ',
            'category': 'day',
            'level': 0,
            'keywords': ['guruvara', 'thursday', 'ಗುರುವಾರ']
        },
        {
            'id': max_id + 5,
            'name': 'Friday',
            'name_kn': 'ಶುಕ್ರವಾರ',
            'category': 'day',
            'level': 0,
            'keywords': ['shukravara', 'friday', 'ಶುಕ್ರವಾರ']
        },
        {
            'id': max_id + 6,
            'name': 'Saturday',
            'name_kn': 'ಶನಿವಾರ',
            'category': 'day',
            'level': 0,
            'keywords': ['shanivara', 'saturday', 'ಶನಿವಾರ']
        },
        {
            'id': max_id + 7,
            'name': 'Sunday',
            'name_kn': 'ರವಿವಾರ',
            'category': 'day',
            'level': 0,
            'keywords': ['ravivara', 'sunday', 'ರವಿವಾರ']
        }
    ]
    
    # Insert day tags into tag_taxonomy
    print("\nInserting day tags into tag_taxonomy...")
    for tag in day_tags:
        cursor.execute('''
            INSERT INTO tag_taxonomy (id, name, parent_id, category, level, created_at, updated_at)
            VALUES (?, ?, NULL, ?, ?, datetime('now'), datetime('now'))
        ''', (tag['id'], tag['name'], tag['category'], tag['level']))
        print(f"  ✓ Added tag {tag['id']}: {tag['name']} ({tag['name_kn']})")
    
    # Insert Kannada translations
    print("\nAdding Kannada translations...")
    for tag in day_tags:
        cursor.execute('''
            INSERT INTO tag_translations (tag_id, language, translation)
            VALUES (?, 'kn', ?)
        ''', (tag['id'], tag['name_kn']))
        print(f"  ✓ Translation for {tag['name']}: {tag['name_kn']}")
    
    # Commit tag creation
    conn.commit()
    
    # Store day tag IDs for tagging logic
    DAY_TAGS = {
        'Monday': max_id + 1,
        'Tuesday': max_id + 2,
        'Wednesday': max_id + 3,
        'Thursday': max_id + 4,
        'Friday': max_id + 5,
        'Saturday': max_id + 6,
        'Sunday': max_id + 7
    }
    
    # Deity to day mapping
    DEITY_DAY_MAP = {
        2: ['Monday'],                              # Shiva -> Monday
        6: ['Tuesday', 'Saturday'],                 # Hanuman -> Tuesday, Saturday
        5: ['Tuesday'],                              # Ganesha -> Tuesday
        3: ['Wednesday'],                            # Vishnu -> Wednesday
        7: ['Wednesday'],                            # Krishna -> Wednesday
        8: ['Wednesday'],                            # Rama -> Wednesday (Vishnu avatar)
        4: ['Friday'],                               # Devi -> Friday
        146: ['Wednesday'],                          # Narasimha -> Wednesday (Vishnu avatar)
    }
    
    # Type to day mapping (for Gurustuti)
    TYPE_DAY_MAP = {
        13: ['Thursday'],  # Gurustuti -> Thursday
    }
    
    # Occasion to day mapping (for Bindu Madhava)
    OCCASION_DAY_MAP = {
        27: ['Thursday'],  # Bindu Madhava -> Thursday
    }
    
    # Now apply day tags to all bhajans based on existing deity/type/occasion tags
    print("\n" + "=" * 80)
    print("APPLYING DAY TAGS TO BHAJANS")
    print("=" * 80)
    
    # Get all current bhajan tag associations
    bhajan_tags = cursor.execute('''
        SELECT bhajan_id, tag_id 
        FROM bhajan_tags 
        WHERE tag_id NOT IN (?, ?, ?, ?, ?, ?, ?)
    ''', tuple(DAY_TAGS.values())).fetchall()
    
    # Build map of bhajan_id -> set of tag_ids
    bhajan_tag_map = {}
    for bt in bhajan_tags:
        if bt[0] not in bhajan_tag_map:
            bhajan_tag_map[bt[0]] = set()
        bhajan_tag_map[bt[0]].add(bt[1])
    
    # Apply day tags
    day_associations = []
    
    for bhajan_id, tag_ids in bhajan_tag_map.items():
        days_to_add = set()
        
        # Check deity tags
        for tag_id in tag_ids:
            if tag_id in DEITY_DAY_MAP:
                for day in DEITY_DAY_MAP[tag_id]:
                    days_to_add.add(DAY_TAGS[day])
        
        # Check type tags
        for tag_id in tag_ids:
            if tag_id in TYPE_DAY_MAP:
                for day in TYPE_DAY_MAP[tag_id]:
                    days_to_add.add(DAY_TAGS[day])
        
        # Check occasion tags
        for tag_id in tag_ids:
            if tag_id in OCCASION_DAY_MAP:
                for day in OCCASION_DAY_MAP[tag_id]:
                    days_to_add.add(DAY_TAGS[day])
        
        # Add associations
        for day_tag_id in days_to_add:
            day_associations.append((bhajan_id, day_tag_id))
    
    # Insert day tag associations
    print(f"\nInserting {len(day_associations)} day tag associations...")
    for assoc in day_associations:
        cursor.execute('''
            INSERT INTO bhajan_tags (bhajan_id, tag_id, source, confidence)
            VALUES (?, ?, 'AI_ANALYSIS', 0.95)
        ''', assoc)
    
    conn.commit()
    
    # Statistics
    print("\n" + "=" * 80)
    print("DAY TAG STATISTICS")
    print("=" * 80)
    
    day_stats = cursor.execute('''
        SELECT 
            tt.name,
            ttr.translation as name_kn,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / 208, 1) as percentage
        FROM bhajan_tags bt
        JOIN tag_taxonomy tt ON bt.tag_id = tt.id
        LEFT JOIN tag_translations ttr ON tt.id = ttr.tag_id AND ttr.language = 'kn'
        WHERE tt.category = 'day'
        GROUP BY tt.name, ttr.translation
        ORDER BY count DESC
    ''').fetchall()
    
    print(f"\n{'Day':15} | {'Kannada':15} | {'Count':5} | {'%':5}")
    print("-" * 50)
    for stat in day_stats:
        print(f"{stat[0]:15} | {stat[1]:15} | {stat[2]:5} | {stat[3]:5}%")
    
    # Sample tagged bhajans
    print("\n" + "=" * 80)
    print("SAMPLE BHAJANS WITH DAY TAGS (5 examples)")
    print("=" * 80)
    
    samples = cursor.execute('''
        SELECT DISTINCT
            b.id,
            b.title,
            GROUP_CONCAT(
                CASE 
                    WHEN tt.category = 'deity' THEN tt.name
                    ELSE NULL
                END, ', '
            ) as deities,
            GROUP_CONCAT(
                CASE 
                    WHEN tt.category = 'day' THEN tt.name || ' (' || ttr.translation || ')'
                    ELSE NULL
                END, ', '
            ) as days
        FROM bhajans b
        JOIN bhajan_tags bt ON b.id = bt.bhajan_id
        JOIN tag_taxonomy tt ON bt.tag_id = tt.id
        LEFT JOIN tag_translations ttr ON tt.id = ttr.tag_id AND ttr.language = 'kn'
        WHERE b.id IN (1, 2, 3, 50, 100)
        GROUP BY b.id, b.title
        ORDER BY b.id
    ''').fetchall()
    
    for s in samples:
        print(f"\n[{s[0]}] {s[1]}")
        deities = ', '.join([d for d in s[2].split(', ') if d != 'None']) if s[2] else '-'
        days = ', '.join([d for d in s[3].split(', ') if d != 'None']) if s[3] else '-'
        print(f"  Deities: {deities}")
        print(f"  Days: {days}")
    
    # Final summary
    total_associations = cursor.execute('SELECT COUNT(*) FROM bhajan_tags').fetchone()[0]
    bhajans_with_day = cursor.execute('''
        SELECT COUNT(DISTINCT bhajan_id) 
        FROM bhajan_tags bt
        JOIN tag_taxonomy tt ON bt.tag_id = tt.id
        WHERE tt.category = 'day'
    ''').fetchone()[0]
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Day tags created: {len(day_tags)}")
    print(f"Day associations added: {len(day_associations)}")
    print(f"Bhajans with day tags: {bhajans_with_day} / 208")
    print(f"Total tag associations now: {total_associations}")
    print(f"Average tags per bhajan: {total_associations / 208:.1f}")
    
    conn.close()
    
    print("\n✓ Day-of-week tags successfully added!")

if __name__ == '__main__':
    main()
