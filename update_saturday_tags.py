#!/usr/bin/env python3
"""
Update Saturday Day Tag Associations
Add Saturday tag to all Vishnu/Krishna/Rama/Narasimha bhajans (along with existing Wednesday)
"""

import sqlite3

def main():
    conn = sqlite3.connect('data/portal.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("UPDATING SATURDAY DAY TAG ASSOCIATIONS")
    print("=" * 80)
    print()
    
    # Saturday tag ID
    SATURDAY_TAG = 152
    WEDNESDAY_TAG = 149
    
    # Vishnu family deity IDs
    VISHNU_DEITIES = {
        3: 'Vishnu',
        7: 'Krishna',
        8: 'Rama',
        146: 'Narasimha'
    }
    
    print("Updated mapping:")
    print("  Monday (147): Shiva")
    print("  Tuesday (148): Hanuman, Ganesha")
    print("  Wednesday (149): Krishna")
    print("  Thursday (150): Guru/Bindu Madhava")
    print("  Friday (151): Devi, Lakshmi")
    print("  Saturday (152): Vishnu, Govinda, Hanuman, Rama, Krishna, Narasimha")
    print("  Sunday (153): Surya")
    print()
    
    # Find all bhajans with Vishnu-family deity tags
    vishnu_bhajans = cursor.execute('''
        SELECT DISTINCT bt.bhajan_id, b.title, tt.id, tt.name
        FROM bhajan_tags bt
        JOIN bhajans b ON bt.bhajan_id = b.id
        JOIN tag_taxonomy tt ON bt.tag_id = tt.id
        WHERE bt.tag_id IN (3, 7, 8, 146)
        ORDER BY bt.bhajan_id
    ''').fetchall()
    
    # Group by bhajan_id
    bhajan_deities = {}
    for row in vishnu_bhajans:
        bhajan_id = row[0]
        if bhajan_id not in bhajan_deities:
            bhajan_deities[bhajan_id] = {
                'title': row[1],
                'deities': []
            }
        bhajan_deities[bhajan_id]['deities'].append(row[3])
    
    print(f"Found {len(bhajan_deities)} bhajans with Vishnu-family deities")
    print()
    
    # Check which ones already have Saturday tag
    saturday_existing = cursor.execute('''
        SELECT COUNT(DISTINCT bhajan_id)
        FROM bhajan_tags
        WHERE tag_id = ?
    ''', (SATURDAY_TAG,)).fetchone()[0]
    
    print(f"Bhajans currently with Saturday tag: {saturday_existing}")
    print()
    
    # Add Saturday tag to all Vishnu-family bhajans that don't have it
    new_associations = 0
    
    print("Adding Saturday tags to Vishnu-family bhajans...")
    for bhajan_id, info in bhajan_deities.items():
        # Check if already has Saturday tag
        has_saturday = cursor.execute('''
            SELECT COUNT(*)
            FROM bhajan_tags
            WHERE bhajan_id = ? AND tag_id = ?
        ''', (bhajan_id, SATURDAY_TAG)).fetchone()[0]
        
        if not has_saturday:
            cursor.execute('''
                INSERT INTO bhajan_tags (bhajan_id, tag_id, source, confidence)
                VALUES (?, ?, 'AI_ANALYSIS', 0.95)
            ''', (bhajan_id, SATURDAY_TAG))
            new_associations += 1
    
    conn.commit()
    
    print(f"  ✓ Added {new_associations} new Saturday associations")
    print()
    
    # Updated statistics
    print("=" * 80)
    print("UPDATED DAY TAG STATISTICS")
    print("=" * 80)
    print()
    
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
    
    print(f"{'Day':15} | {'Kannada':15} | {'Count':5} | {'%':5}")
    print("-" * 50)
    for stat in day_stats:
        print(f"{stat[0]:15} | {stat[1]:15} | {stat[2]:5} | {stat[3]:5}%")
    
    # Sample bhajans with both Wednesday and Saturday
    print()
    print("=" * 80)
    print("SAMPLE BHAJANS WITH BOTH WEDNESDAY AND SATURDAY")
    print("=" * 80)
    print()
    
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
        WHERE b.id IN (
            SELECT DISTINCT bhajan_id
            FROM bhajan_tags
            WHERE tag_id IN (?, ?)
            GROUP BY bhajan_id
            HAVING COUNT(DISTINCT tag_id) = 2
        )
        GROUP BY b.id, b.title
        ORDER BY b.id
        LIMIT 10
    ''', (WEDNESDAY_TAG, SATURDAY_TAG)).fetchall()
    
    for s in samples:
        deities = ', '.join([d for d in s[2].split(', ') if d != 'None']) if s[2] else '-'
        days = ', '.join([d for d in s[3].split(', ') if d != 'None']) if s[3] else '-'
        print(f"[{s[0]}] {s[1]}")
        print(f"  Deities: {deities}")
        print(f"  Days: {days}")
        print()
    
    # Final summary
    total_associations = cursor.execute('SELECT COUNT(*) FROM bhajan_tags').fetchone()[0]
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"New Saturday associations added: {new_associations}")
    print(f"Total associations now: {total_associations}")
    print(f"Average tags per bhajan: {total_associations / 208:.1f}")
    
    conn.close()
    
    print()
    print("✓ Saturday tags updated successfully!")

if __name__ == '__main__':
    main()
