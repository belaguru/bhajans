#!/usr/bin/env python3
"""
Tag Migration Script - Migrate JSON tags to bhajan_tags table

Usage:
    python scripts/migrate_tags.py --dry-run          # Preview changes
    python scripts/migrate_tags.py --verbose          # Run with detailed logging
    python scripts/migrate_tags.py --rollback         # Delete all MIGRATED records
    python scripts/migrate_tags.py                    # Run actual migration

Features:
- Reads each bhajan's tags JSON field
- Maps old tags → canonical tags using data/tag-migration-mapping.csv
- Inserts into bhajan_tags table with source='MIGRATED', confidence=1.0
- Keeps original tags field intact (backward compatibility)
- Progress bar for bulk operations
- Transaction safety (rollback on error)
- Summary report at end

Author: Belaguru Bot
Date: 2026-03-22
"""

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Progress bar support
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("⚠️  Install tqdm for progress bars: pip install tqdm")


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_DB = "./data/portal.db"
MAPPING_CSV = "./data/tag-migration-mapping.csv"


# ============================================================================
# Tag Mapping Functions
# ============================================================================

def load_tag_mapping(csv_path: str = MAPPING_CSV) -> Dict[str, Dict[str, str]]:
    """
    Load tag mapping from CSV
    
    Returns:
        Dict mapping old_tag → {action: str, canonical: str}
        Example: {'test': {'action': 'DELETE', 'canonical': 'N/A'}}
    """
    mapping = {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                old_tag = row['old_tag'].strip()
                canonical = row['canonical_tag'].strip()
                action = row['action'].strip()
                
                mapping[old_tag] = {
                    'action': action,
                    'canonical': canonical
                }
        
        print(f"✓ Loaded {len(mapping)} tag mappings from {csv_path}")
        return mapping
    
    except FileNotFoundError:
        print(f"❌ Mapping file not found: {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading mapping: {e}")
        sys.exit(1)


def map_tag_to_canonical(tag: str, mapping: Dict[str, Dict[str, str]]) -> Optional[str]:
    """
    Map a tag to its canonical form
    
    Args:
        tag: Original tag
        mapping: Tag mapping dictionary
    
    Returns:
        Canonical tag or None if should be deleted
    """
    # Exact match in mapping
    if tag in mapping:
        action = mapping[tag]['action']
        canonical = mapping[tag]['canonical']
        
        if action == 'DELETE':
            return None
        elif action in ('KEEP', 'MERGE'):
            # Return canonical tag as-is (preserves case from mapping)
            return canonical
    
    # No mapping found - pass through as-is
    return tag


# ============================================================================
# Database Functions
# ============================================================================

def get_tag_id(cursor: sqlite3.Cursor, tag_name: str) -> Optional[int]:
    """
    Get tag ID from tag_taxonomy table (case-insensitive)
    
    Returns:
        tag_id or None if not found
    """
    # Try exact match first
    cursor.execute(
        "SELECT id FROM tag_taxonomy WHERE name = ?",
        (tag_name,)
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    
    # Try case-insensitive match
    cursor.execute(
        "SELECT id FROM tag_taxonomy WHERE LOWER(name) = LOWER(?)",
        (tag_name,)
    )
    row = cursor.fetchone()
    return row[0] if row else None


def insert_bhajan_tag(
    cursor: sqlite3.Cursor,
    bhajan_id: int,
    tag_id: int,
    source: str = 'MIGRATED',
    confidence: float = 1.0
) -> bool:
    """
    Insert tag assignment into bhajan_tags table
    
    Returns:
        True if inserted, False if duplicate (already exists)
    """
    try:
        cursor.execute("""
            INSERT INTO bhajan_tags (bhajan_id, tag_id, source, confidence)
            VALUES (?, ?, ?, ?)
        """, (bhajan_id, tag_id, source, confidence))
        return True
    except sqlite3.IntegrityError:
        # Duplicate - already exists
        return False


# ============================================================================
# Migration Functions
# ============================================================================

def migrate_bhajan_tags(
    db_path: str = DEFAULT_DB,
    dry_run: bool = False,
    verbose: bool = False
) -> Dict:
    """
    Migrate tags from bhajans.tags JSON field to bhajan_tags table
    
    Args:
        db_path: Path to SQLite database
        dry_run: If True, only show what would happen (no changes)
        verbose: If True, show detailed logging
    
    Returns:
        Dict with migration results
    """
    # Load mapping
    mapping = load_tag_mapping()
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Stats
    stats = {
        'status': 'success',
        'dry_run': dry_run,
        'bhajans_processed': 0,
        'tags_migrated': 0,
        'tags_deleted': 0,
        'tags_skipped': 0,
        'tags_duplicates': 0,
        'errors': []
    }
    
    try:
        # Get all bhajans (check if deleted_at column exists)
        cursor.execute("PRAGMA table_info(bhajans)")
        columns = [row[1] for row in cursor.fetchall()]
        has_deleted_at = 'deleted_at' in columns
        
        if has_deleted_at:
            cursor.execute("SELECT id, title, tags FROM bhajans WHERE deleted_at IS NULL")
        else:
            cursor.execute("SELECT id, title, tags FROM bhajans")
        
        bhajans = cursor.fetchall()
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Migrating tags for {len(bhajans)} bhajans...")
        
        # Progress bar
        iterator = tqdm(bhajans, desc="Processing") if TQDM_AVAILABLE else bhajans
        
        for bhajan_id, title, tags_json in iterator:
            stats['bhajans_processed'] += 1
            
            # Parse tags JSON
            try:
                if tags_json:
                    tags = json.loads(tags_json)
                else:
                    tags = []
            except json.JSONDecodeError:
                if verbose:
                    print(f"⚠️  Invalid JSON for bhajan {bhajan_id}: {title}")
                stats['errors'].append(f"Invalid JSON for bhajan {bhajan_id}")
                continue
            
            if verbose:
                print(f"\n📖 Bhajan #{bhajan_id}: {title}")
                print(f"   Original tags: {tags}")
            
            # Process each tag
            for old_tag in tags:
                # Map to canonical
                canonical_tag = map_tag_to_canonical(old_tag, mapping)
                
                if canonical_tag is None:
                    # DELETE action
                    stats['tags_deleted'] += 1
                    if verbose:
                        print(f"   ❌ DELETE: {old_tag}")
                    continue
                
                # Get tag ID from taxonomy
                tag_id = get_tag_id(cursor, canonical_tag)
                
                if tag_id is None:
                    # Tag not in taxonomy - skip
                    stats['tags_skipped'] += 1
                    if verbose:
                        print(f"   ⏭️  SKIP: {old_tag} → {canonical_tag} (not in taxonomy)")
                    continue
                
                # Insert into bhajan_tags (if not dry run)
                if not dry_run:
                    inserted = insert_bhajan_tag(cursor, bhajan_id, tag_id)
                    if inserted:
                        stats['tags_migrated'] += 1
                        if verbose:
                            print(f"   ✓ MIGRATED: {old_tag} → {canonical_tag}")
                    else:
                        stats['tags_duplicates'] += 1
                        if verbose:
                            print(f"   ⚠️  DUPLICATE: {old_tag} → {canonical_tag}")
                else:
                    # Dry run - just count
                    stats['tags_migrated'] += 1
                    if verbose:
                        print(f"   ✓ WOULD MIGRATE: {old_tag} → {canonical_tag}")
        
        # Commit transaction (unless dry run)
        if not dry_run:
            conn.commit()
            print("\n✓ Transaction committed")
        else:
            print("\n[DRY RUN] No changes made to database")
    
    except Exception as e:
        conn.rollback()
        stats['status'] = 'error'
        stats['errors'].append(str(e))
        print(f"\n❌ Error during migration: {e}")
        print("   Transaction rolled back")
    
    finally:
        conn.close()
    
    # Print summary
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    print(f"Status:            {stats['status'].upper()}")
    print(f"Mode:              {'DRY RUN' if dry_run else 'ACTUAL MIGRATION'}")
    print(f"Bhajans processed: {stats['bhajans_processed']}")
    print(f"Tags migrated:     {stats['tags_migrated']}")
    print(f"Tags deleted:      {stats['tags_deleted']}")
    print(f"Tags skipped:      {stats['tags_skipped']}")
    print(f"Tags duplicates:   {stats['tags_duplicates']}")
    
    if stats['errors']:
        print(f"\nErrors ({len(stats['errors'])}):")
        for error in stats['errors'][:5]:
            print(f"  - {error}")
        if len(stats['errors']) > 5:
            print(f"  ... and {len(stats['errors']) - 5} more")
    
    print("="*60)
    
    return stats


def rollback_migration(
    db_path: str = DEFAULT_DB,
    verbose: bool = False
) -> Dict:
    """
    Rollback migration by deleting all MIGRATED records
    
    Args:
        db_path: Path to SQLite database
        verbose: If True, show detailed logging
    
    Returns:
        Dict with rollback results
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = {
        'status': 'success',
        'records_deleted': 0,
        'errors': []
    }
    
    try:
        # Count records to delete
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags WHERE source = 'MIGRATED'")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("ℹ️  No MIGRATED records found to rollback")
            return stats
        
        print(f"\n🔄 Rolling back {count} MIGRATED records...")
        
        # Delete all MIGRATED records
        cursor.execute("DELETE FROM bhajan_tags WHERE source = 'MIGRATED'")
        stats['records_deleted'] = cursor.rowcount
        
        conn.commit()
        
        print(f"✓ Deleted {stats['records_deleted']} records")
        print("✓ Rollback complete")
    
    except Exception as e:
        conn.rollback()
        stats['status'] = 'error'
        stats['errors'].append(str(e))
        print(f"❌ Error during rollback: {e}")
    
    finally:
        conn.close()
    
    return stats


def get_migration_stats(db_path: str = DEFAULT_DB) -> Dict:
    """
    Get statistics about migrated tags
    
    Returns:
        Dict with statistics
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = {}
    
    try:
        # Total bhajans (check if deleted_at column exists)
        cursor.execute("PRAGMA table_info(bhajans)")
        columns = [row[1] for row in cursor.fetchall()]
        has_deleted_at = 'deleted_at' in columns
        
        if has_deleted_at:
            cursor.execute("SELECT COUNT(*) FROM bhajans WHERE deleted_at IS NULL")
        else:
            cursor.execute("SELECT COUNT(*) FROM bhajans")
        
        stats['total_bhajans'] = cursor.fetchone()[0]
        
        # Total tags in bhajan_tags
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags")
        stats['total_tags_in_bhajan_tags'] = cursor.fetchone()[0]
        
        # MIGRATED tags
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags WHERE source = 'MIGRATED'")
        stats['migrated_tags'] = cursor.fetchone()[0]
        
        # Bhajans with MIGRATED tags
        cursor.execute("""
            SELECT COUNT(DISTINCT bhajan_id) 
            FROM bhajan_tags 
            WHERE source = 'MIGRATED'
        """)
        stats['bhajans_with_migrated_tags'] = cursor.fetchone()[0]
    
    finally:
        conn.close()
    
    return stats


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Migrate tags from bhajans.tags JSON to bhajan_tags table"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying database'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed logging'
    )
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Delete all MIGRATED records'
    )
    parser.add_argument(
        '--db',
        default=DEFAULT_DB,
        help=f'Path to database (default: {DEFAULT_DB})'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show migration statistics'
    )
    
    args = parser.parse_args()
    
    # Show stats
    if args.stats:
        stats = get_migration_stats(args.db)
        print("\n" + "="*60)
        print("MIGRATION STATISTICS")
        print("="*60)
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print("="*60)
        return
    
    # Rollback
    if args.rollback:
        confirm = input("\n⚠️  This will DELETE all MIGRATED records. Continue? [y/N] ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return
        
        rollback_migration(args.db, args.verbose)
        return
    
    # Migration
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made")
    
    migrate_bhajan_tags(
        db_path=args.db,
        dry_run=args.dry_run,
        verbose=args.verbose
    )


if __name__ == '__main__':
    main()
