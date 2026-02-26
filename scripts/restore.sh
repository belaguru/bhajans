#!/bin/bash

# Belaguru Portal - Database Restore Script
# Usage: ./restore.sh [backup_timestamp]
# Example: ./restore.sh 20260226_090000

set -e

DB_PATH="/home/kreddy/.belaguru/portal.db"
BACKUP_DIR="/home/kreddy/.belaguru/backups"

if [ -z "$1" ]; then
    echo "Available backups:"
    ls -lh "$BACKUP_DIR" | awk 'NR>1 {print $9, "(" $5 ")"}'
    echo ""
    echo "Usage: ./restore.sh [backup_timestamp]"
    echo "Example: ./restore.sh 20260226_090000"
    exit 1
fi

BACKUP_FILE="$BACKUP_DIR/portal_$1.db"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "[ERROR] Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "[WARNING] About to restore database from: $BACKUP_FILE"
echo "[WARNING] Current database will be backed up first"
read -p "Continue? (yes/no): " -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Backup current database
if [ -f "$DB_PATH" ]; then
    CURRENT_BACKUP="$BACKUP_DIR/portal_before_restore_$(date +%Y%m%d_%H%M%S).db"
    cp "$DB_PATH" "$CURRENT_BACKUP"
    echo "[OK] Current database backed up: $CURRENT_BACKUP"
fi

# Stop the server
echo "[OK] Stopping server..."
pkill -f "python.*main.py" || true
sleep 2

# Restore from backup
cp "$BACKUP_FILE" "$DB_PATH"
echo "[OK] Database restored from: $BACKUP_FILE"

# Verify
if [ -f "$DB_PATH" ]; then
    SIZE=$(du -h "$DB_PATH" | cut -f1)
    echo "[OK] Restore successful - Size: $SIZE"
    
    # Log
    LOG_FILE="/home/kreddy/.belaguru/backup.log"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Restore completed from: $BACKUP_FILE" >> "$LOG_FILE"
else
    echo "[ERROR] Restore failed"
    exit 1
fi

# Restart server
echo "[OK] Restarting server..."
cd /home/kreddy/Projects/belaguru-portal && source venv/bin/activate && nohup python3 main.py > /home/kreddy/.belaguru/portal.log 2>&1 & 
sleep 3
echo "[OK] Server restarted"
echo "[OK] Restore complete!"

exit 0
