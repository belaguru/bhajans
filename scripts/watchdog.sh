#!/bin/bash

# Belaguru Portal - Auto-Restart Watchdog
# Monitors server and auto-restarts if it crashes

PROJECT_DIR="/home/kreddy/Projects/belaguru-portal"
LOG_FILE="/home/kreddy/.belaguru/watchdog.log"
CHECK_INTERVAL=30
RESTART_DELAY=5

{
    echo "[$(date)] =========================================="
    echo "[$(date)] Starting watchdog (PID: $$)"
    echo "[$(date)] Check interval: $CHECK_INTERVAL seconds"
    echo "[$(date)] =========================================="
} >> "$LOG_FILE"

while true; do
    # Check if process exists
    if ! pgrep -f "python3 main.py" > /dev/null 2>&1; then
        echo "[$(date)] ⚠️  Server process not found! Restarting..." >> "$LOG_FILE"
        
        pkill -9 -f "python.*main.py" 2>/dev/null || true
        sleep $RESTART_DELAY
        fuser -k 8000/tcp 2>/dev/null || true
        sleep 2
        
        echo "[$(date)] Starting server..." >> "$LOG_FILE"
        cd "$PROJECT_DIR"
        source venv/bin/activate >> "$LOG_FILE" 2>&1
        nohup python3 main.py >> /home/kreddy/.belaguru/portal.log 2>&1 &
        RESTART_PID=$!
        
        sleep 5
        
        if ps -p $RESTART_PID > /dev/null 2>&1; then
            echo "[$(date)] ✅ Server started (PID: $RESTART_PID)" >> "$LOG_FILE"
        else
            echo "[$(date)] ❌ Failed to start server" >> "$LOG_FILE"
            cat /home/kreddy/.belaguru/portal.log | tail -20 >> "$LOG_FILE"
        fi
    else
        # Check health endpoint
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "[$(date)] ✓ Server healthy" >> "$LOG_FILE"
        else
            echo "[$(date)] ⚠️  Health check failed! Restarting..." >> "$LOG_FILE"
            pkill -9 -f "python3 main.py"
            sleep 2
        fi
    fi
    
    sleep $CHECK_INTERVAL
done
