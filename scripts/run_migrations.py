#!/usr/bin/env python3
"""
Migration Runner with Version Tracking

Safely runs SQL migrations with:
- Version tracking in migration_history table
- Checksum verification to detect modified migrations
- Dry-run mode to preview changes
- Backup creation before running
- Rollback support
- Transaction per migration (atomic)

Usage:
    python scripts/run_migrations.py                    # Run pending migrations
    python scripts/run_migrations.py --dry-run          # Show what would run
    python scripts/run_migrations.py --status           # Show migration status
    python scripts/run_migrations.py --rollback 001_*.sql  # Rollback a migration
    python scripts/run_migrations.py --backup           # Create backup before running
"""

import os
import sys
import sqlite3
import hashlib
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class MigrationRunner:
    """Handles database migrations with version tracking"""
    
    def __init__(self, db_path: str, migrations_dir: str = "migrations"):
        """
        Initialize migration runner
        
        Args:
            db_path: Path to SQLite database
            migrations_dir: Directory containing migration files
        """
        self.db_path = db_path
        self.migrations_dir = migrations_dir
        self._ensure_migration_history_table()
    
    def _ensure_migration_history_table(self):
        """Create migration_history table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename VARCHAR(255) NOT NULL UNIQUE,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                checksum VARCHAR(64)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_applied_migrations(self) -> List[Dict]:
        """Get list of applied migrations"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT filename, applied_at, checksum
            FROM migration_history
            ORDER BY filename
        """)
        
        migrations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return migrations
    
    def is_migration_applied(self, filename: str) -> bool:
        """Check if a migration has been applied"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM migration_history WHERE filename = ?",
            (filename,)
        )
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def record_migration(self, filename: str, checksum: str):
        """Record a migration as applied"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO migration_history (filename, checksum)
            VALUES (?, ?)
        """, (filename, checksum))
        
        conn.commit()
        conn.close()
    
    def remove_migration_record(self, filename: str):
        """Remove a migration record (for rollback)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM migration_history WHERE filename = ?",
            (filename,)
        )
        
        conn.commit()
        conn.close()
    
    def verify_checksum(self, filename: str, current_checksum: str) -> bool:
        """Verify that a migration hasn't been modified since it was applied"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT checksum FROM migration_history WHERE filename = ?",
            (filename,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return True  # Not applied yet, so checksum is valid
        
        stored_checksum = result[0]
        return stored_checksum == current_checksum
    
    def run_migrations(self, dry_run: bool = False) -> Dict:
        """
        Run pending migrations
        
        Args:
            dry_run: If True, only show what would be run
        
        Returns:
            Dictionary with results
        """
        migration_files = get_migration_files(self.migrations_dir)
        
        if not migration_files:
            return {
                'success': True,
                'message': 'No migration files found',
                'applied': [],
                'skipped': []
            }
        
        applied = []
        skipped = []
        errors = []
        
        if dry_run:
            would_apply = []
            for filename in migration_files:
                if not self.is_migration_applied(filename):
                    would_apply.append(filename)
                else:
                    skipped.append(filename)
            
            return {
                'dry_run': True,
                'would_apply': would_apply,
                'skipped': skipped
            }
        
        # Run migrations
        for filename in migration_files:
            migration_path = os.path.join(self.migrations_dir, filename)
            
            # Skip if already applied
            if self.is_migration_applied(filename):
                skipped.append(filename)
                continue
            
            # Calculate checksum
            checksum = calculate_checksum(migration_path)
            
            # Parse migration
            try:
                forward_sql, _ = parse_migration_file(migration_path)
            except Exception as e:
                errors.append({
                    'filename': filename,
                    'error': f'Failed to parse migration: {str(e)}'
                })
                break
            
            # Run migration in transaction
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute("BEGIN TRANSACTION")
                
                # Execute the migration
                conn.executescript(forward_sql)
                
                conn.commit()
                conn.close()
                
                # Record success
                self.record_migration(filename, checksum)
                applied.append(filename)
                
            except Exception as e:
                errors.append({
                    'filename': filename,
                    'error': str(e)
                })
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass
                break
        
        success = len(errors) == 0
        
        result = {
            'success': success,
            'applied': applied,
            'skipped': skipped
        }
        
        if errors:
            result['error'] = errors[0]['error']
            result['failed_migration'] = errors[0]['filename']
        
        return result
    
    def get_status(self) -> Dict:
        """Get migration status (applied vs pending)"""
        migration_files = get_migration_files(self.migrations_dir)
        applied_migrations = self.get_applied_migrations()
        applied_filenames = {m['filename'] for m in applied_migrations}
        
        pending = []
        applied = []
        modified = []
        
        for filename in migration_files:
            migration_path = os.path.join(self.migrations_dir, filename)
            current_checksum = calculate_checksum(migration_path)
            
            if filename in applied_filenames:
                applied.append({
                    'filename': filename,
                    'applied_at': next(
                        m['applied_at'] for m in applied_migrations 
                        if m['filename'] == filename
                    )
                })
                
                # Check if modified
                if not self.verify_checksum(filename, current_checksum):
                    modified.append(filename)
            else:
                pending.append(filename)
        
        return {
            'pending': pending,
            'applied': applied,
            'modified': modified
        }
    
    def rollback_migration(self, filename: str) -> Dict:
        """
        Rollback a migration
        
        Args:
            filename: Name of migration file to rollback
        
        Returns:
            Dictionary with results
        """
        migration_path = os.path.join(self.migrations_dir, filename)
        
        if not os.path.exists(migration_path):
            return {
                'success': False,
                'error': f'Migration file not found: {filename}'
            }
        
        if not self.is_migration_applied(filename):
            return {
                'success': False,
                'error': f'Migration not applied: {filename}'
            }
        
        # Parse rollback section
        try:
            _, rollback_sql = parse_migration_file(migration_path)
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to parse rollback section: {str(e)}'
            }
        
        if not rollback_sql.strip():
            return {
                'success': False,
                'error': 'No rollback section found in migration'
            }
        
        # Run rollback in transaction
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("BEGIN TRANSACTION")
            
            # Execute rollback
            conn.executescript(rollback_sql)
            
            conn.commit()
            conn.close()
            
            # Remove migration record
            self.remove_migration_record(filename)
            
            return {
                'success': True,
                'message': f'Successfully rolled back {filename}'
            }
            
        except Exception as e:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            
            return {
                'success': False,
                'error': f'Rollback failed: {str(e)}'
            }
    
    def backup_database(self) -> str:
        """
        Create a backup of the database
        
        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(os.path.dirname(self.db_path), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        db_name = os.path.basename(self.db_path)
        backup_path = os.path.join(
            backup_dir,
            f"{db_name}.backup_{timestamp}.db"
        )
        
        shutil.copy2(self.db_path, backup_path)
        
        return backup_path


# Helper Functions

def calculate_checksum(file_path: str) -> str:
    """Calculate SHA256 checksum of a file"""
    sha256 = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    
    return sha256.hexdigest()


def parse_migration_file(file_path: str) -> Tuple[str, str]:
    """
    Parse migration file into forward and rollback sections
    
    Returns:
        Tuple of (forward_sql, rollback_sql)
    """
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split on ROLLBACK SECTION marker
    parts = content.split('-- ROLLBACK SECTION')
    
    forward_sql = parts[0].strip()
    rollback_sql = ''
    
    if len(parts) > 1:
        # Extract rollback SQL (uncomment the lines)
        rollback_lines = []
        for line in parts[1].split('\n'):
            line = line.strip()
            if line.startswith('-- ') and not line.startswith('-- ='):
                # Uncomment the line
                rollback_lines.append(line[3:])
        
        rollback_sql = '\n'.join(rollback_lines).strip()
    
    return forward_sql, rollback_sql


def get_migration_files(migrations_dir: str) -> List[str]:
    """
    Get sorted list of migration files
    
    Returns:
        List of migration filenames in order
    """
    if not os.path.exists(migrations_dir):
        return []
    
    files = [
        f for f in os.listdir(migrations_dir)
        if f.endswith('.sql')
    ]
    
    return sorted(files)


def print_status(status: Dict):
    """Pretty print migration status"""
    print("\n📊 Migration Status")
    print("=" * 60)
    
    if status['applied']:
        print(f"\n✅ Applied Migrations ({len(status['applied'])}):")
        for migration in status['applied']:
            print(f"  • {migration['filename']}")
            print(f"    Applied: {migration['applied_at']}")
    
    if status['pending']:
        print(f"\n⏳ Pending Migrations ({len(status['pending'])}):")
        for filename in status['pending']:
            print(f"  • {filename}")
    
    if status['modified']:
        print(f"\n⚠️  Modified Migrations ({len(status['modified'])}):")
        print("    (These migrations have changed since they were applied)")
        for filename in status['modified']:
            print(f"  • {filename}")
    
    if not status['applied'] and not status['pending']:
        print("\n✨ No migrations found")
    
    print("=" * 60)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Run database migrations with version tracking'
    )
    
    parser.add_argument(
        '--db',
        default='./data/portal.db',
        help='Path to database (default: ./data/portal.db)'
    )
    
    parser.add_argument(
        '--migrations-dir',
        default='migrations',
        help='Path to migrations directory (default: migrations)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be run without executing'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show migration status'
    )
    
    parser.add_argument(
        '--rollback',
        metavar='FILENAME',
        help='Rollback a specific migration'
    )
    
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create database backup before running'
    )
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = MigrationRunner(args.db, args.migrations_dir)
    
    # Handle --status
    if args.status:
        status = runner.get_status()
        print_status(status)
        return
    
    # Handle --rollback
    if args.rollback:
        print(f"\n🔄 Rolling back migration: {args.rollback}")
        result = runner.rollback_migration(args.rollback)
        
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        return
    
    # Handle --backup
    if args.backup:
        print("\n💾 Creating database backup...")
        backup_path = runner.backup_database()
        print(f"✅ Backup created: {backup_path}")
    
    # Run migrations
    if args.dry_run:
        print("\n🔍 Dry Run - No changes will be made")
        print("=" * 60)
    else:
        print("\n🚀 Running Migrations")
        print("=" * 60)
    
    result = runner.run_migrations(dry_run=args.dry_run)
    
    if args.dry_run:
        if result['would_apply']:
            print(f"\nWould apply {len(result['would_apply'])} migrations:")
            for filename in result['would_apply']:
                print(f"  • {filename}")
        else:
            print("\n✨ No pending migrations")
        
        if result['skipped']:
            print(f"\nWould skip {len(result['skipped'])} already applied:")
            for filename in result['skipped']:
                print(f"  • {filename}")
    else:
        if result['success']:
            if result['applied']:
                print(f"\n✅ Successfully applied {len(result['applied'])} migrations:")
                for filename in result['applied']:
                    print(f"  • {filename}")
            else:
                print("\n✨ No pending migrations")
            
            if result['skipped']:
                print(f"\n⏭️  Skipped {len(result['skipped'])} already applied")
        else:
            print(f"\n❌ Migration failed!")
            print(f"   File: {result['failed_migration']}")
            print(f"   Error: {result['error']}")
            sys.exit(1)
    
    print("=" * 60)


if __name__ == '__main__':
    main()
