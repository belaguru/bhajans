#!/bin/bash
# Run all tests for Belaguru Portal

set -e

cd ~/Projects/belaguru-bhajans

echo "🧪 Running Belaguru Portal Tests"
echo ""

# Activate venv
source venv/bin/activate

# Run unit tests
echo "📝 Running unit tests (pytest)..."
pytest tests/unit/ -v --tb=short

echo ""
echo "🌐 Running E2E tests (Playwright)..."
npx playwright test

echo ""
echo "✅ All tests passed!"
