#!/bin/bash

# Belaguru Portal - Startup Script

cd ~/Projects/belaguru-portal

echo "🧡 Starting Belaguru Bhajan Portal..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Initialize database
echo "📊 Initializing database..."
python3 -c "from models import init_db; init_db()" 2>/dev/null

# Start server
echo ""
echo "✅ Server starting on http://localhost:8000"
echo "🌐 Open in browser: http://localhost:8000"
echo "📱 Works on mobile, tablet, and desktop"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 main.py
