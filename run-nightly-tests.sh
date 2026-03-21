#!/bin/bash
# Nightly test runner - Comprehensive test suite with reporting

set -e

REPO_DIR="$HOME/Projects/belaguru-bhajans"
REPORT_DIR="$REPO_DIR/test-reports"
TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)
REPORT_FILE="$REPORT_DIR/nightly-$TIMESTAMP.txt"

# Create report directory
mkdir -p "$REPORT_DIR"

echo "🌙 Nightly Test Run - $TIMESTAMP" | tee "$REPORT_FILE"
echo "================================================" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

cd "$REPO_DIR"

# Pull latest code
echo "📥 Pulling latest code..." | tee -a "$REPORT_FILE"
git pull origin main >> "$REPORT_FILE" 2>&1

# Activate venv
source venv/bin/activate

# Update dependencies
echo "" | tee -a "$REPORT_FILE"
echo "📦 Updating dependencies..." | tee -a "$REPORT_FILE"
pip install -q -U pytest pytest-cov httpx >> "$REPORT_FILE" 2>&1
npm install >> "$REPORT_FILE" 2>&1

# Restart staging server
echo "" | tee -a "$REPORT_FILE"
echo "🔄 Restarting staging server..." | tee -a "$REPORT_FILE"
pkill -f "uvicorn.*8001" || true
nohup uvicorn main:app --host 0.0.0.0 --port 8001 --reload > staging.log 2>&1 &
sleep 5

# Run unit tests with coverage
echo "" | tee -a "$REPORT_FILE"
echo "📝 Running unit tests with coverage..." | tee -a "$REPORT_FILE"
pytest tests/unit/ -v --cov=. --cov-report=term --cov-report=html >> "$REPORT_FILE" 2>&1
UNIT_EXIT=$?

# Run E2E tests
echo "" | tee -a "$REPORT_FILE"
echo "🌐 Running E2E tests..." | tee -a "$REPORT_FILE"
npx playwright test >> "$REPORT_FILE" 2>&1
E2E_EXIT=$?

# Generate summary
echo "" | tee -a "$REPORT_FILE"
echo "================================================" | tee -a "$REPORT_FILE"
echo "📊 Test Summary" | tee -a "$REPORT_FILE"
echo "================================================" | tee -a "$REPORT_FILE"

if [ $UNIT_EXIT -eq 0 ]; then
    echo "✅ Unit Tests: PASSED" | tee -a "$REPORT_FILE"
else
    echo "❌ Unit Tests: FAILED (exit code: $UNIT_EXIT)" | tee -a "$REPORT_FILE"
fi

if [ $E2E_EXIT -eq 0 ]; then
    echo "✅ E2E Tests: PASSED" | tee -a "$REPORT_FILE"
else
    echo "❌ E2E Tests: FAILED (exit code: $E2E_EXIT)" | tee -a "$REPORT_FILE"
fi

echo "" | tee -a "$REPORT_FILE"
echo "📁 Full report: $REPORT_FILE" | tee -a "$REPORT_FILE"
echo "📊 Coverage report: $REPO_DIR/htmlcov/index.html" | tee -a "$REPORT_FILE"

# Send Telegram notification
if [ $UNIT_EXIT -ne 0 ] || [ $E2E_EXIT -ne 0 ]; then
    STATUS="❌ FAILED"
    EXIT_CODE=1
else
    STATUS="✅ PASSED"
    EXIT_CODE=0
fi

# Telegram notification (optional - configure with your bot)
MESSAGE="🌙 Nightly Tests $STATUS

Timestamp: $TIMESTAMP
Unit Tests: $([ $UNIT_EXIT -eq 0 ] && echo "✅" || echo "❌")
E2E Tests: $([ $E2E_EXIT -eq 0 ] && echo "✅" || echo "❌")

Report: test-reports/nightly-$TIMESTAMP.txt"

# Uncomment to send Telegram notification
# curl -s -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
#   -d chat_id=<YOUR_CHAT_ID> \
#   -d text="$MESSAGE" > /dev/null

echo "" | tee -a "$REPORT_FILE"
echo "🎯 Nightly test run complete!" | tee -a "$REPORT_FILE"

exit $EXIT_CODE
