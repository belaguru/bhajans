#!/bin/bash
# Start Belaguru Staging (Git Repo)

set -e

cd ~/Projects/belaguru-bhajans

echo "🚀 Starting Belaguru Staging from Git Repo"

# Install/update dependencies
echo "Checking dependencies..."
source venv/bin/activate
pip install -q fastapi uvicorn sqlalchemy python-multipart

# Start PostgreSQL if needed
if ! pgrep -x postgres > /dev/null; then
    echo "Starting PostgreSQL..."
    brew services start postgresql@15
    sleep 2
fi

# Start Redis if needed
if ! pgrep -x redis-server > /dev/null; then
    echo "Starting Redis..."
    brew services start redis
    sleep 1
fi

# Stop old backend if running
if pgrep -f "uvicorn.*8001" > /dev/null; then
    echo "Stopping old backend..."
    pkill -f "uvicorn.*8001"
    sleep 2
fi

# Start staging backend
echo "Starting backend on port 8001..."
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8001 --reload > staging.log 2>&1 &

sleep 3

# Check health
if curl -sf http://localhost:8001/health > /dev/null; then
    echo "✅ Backend healthy"
else
    echo "❌ Backend failed to start"
    tail -20 staging.log
    exit 1
fi

echo ""
echo "✅ Staging server running!"
echo ""
echo "📂 Git Repo: ~/Projects/belaguru-bhajans"
echo "🌍 URL: https://qa.bhajans.s365.in"
echo "📝 Logs: tail -f ~/Projects/belaguru-bhajans/staging.log"
echo ""
echo "To update code:"
echo "  cd ~/Projects/belaguru-bhajans"
echo "  git pull origin main"
echo "  sudo brew services restart nginx"
