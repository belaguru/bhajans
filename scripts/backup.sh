#!/bin/bash

# Belaguru Portal - Automated Backup Script
# Backs up database daily with 7-day retention

set -e

DB_PATH="/home/kreddy/.belaguru/portal.db"
BACKUP_DIR="/home/kreddy/.belaguru/backups"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/portal_$TIMESTAMP.db"

# Create backup directory if needed
mkdir -p "$BACKUP_DIR"

# Only backup if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "[ERROR] Database not found at $DB_PATH"
    exit 1
fi

# Create backup
cp "$DB_PATH" "$BACKUP_FILE"
echo "[OK] $(date) - Backup created: $BACKUP_FILE"

# Verify backup
if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "[OK] Backup verified - Size: $SIZE"
else
    echo "[ERROR] Backup verification failed"
    exit 1
fi

# Cleanup old backups (keep only 7 days)
echo "[OK] Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "portal_*.db" -type f -mtime +$RETENTION_DAYS -delete

# Show current backups
echo "[OK] Current backups:"
ls -lh "$BACKUP_DIR" | tail -10

# Log to file
LOG_FILE="/home/kreddy/.belaguru/backup.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup successful: $BACKUP_FILE (Size: $SIZE)" >> "$LOG_FILE"

exit 0
