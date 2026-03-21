# Testing Guide

**Automated testing with Playwright + pytest + Auto-Fix Agent**

## Overview

```
Push to GitHub
    ↓
GitHub Actions runs tests
    ├─ Unit tests (pytest)
    └─ E2E tests (Playwright)
    ↓
Tests pass? → Deploy to GCP
Tests fail? → Fix Agent creates PR
```

## Running Tests Locally

### Unit Tests (Python/FastAPI)
```bash
cd ~/Projects/belaguru-portal-staging
source venv/bin/activate
pytest tests/unit/ -v
```

### E2E Tests (Playwright)
```bash
cd ~/Projects/belaguru-portal-staging
npm run test:e2e
```

### All Tests
```bash
npm test
```

## Test Structure

### Unit Tests (`tests/unit/`)
- `test_database.py` - Database operations (SQLAlchemy)
- `test_api.py` - FastAPI endpoints

### E2E Tests (`tests/e2e/`)
- `test_homepage.spec.js` - Homepage loads, navigation
- `test_search.spec.js` - Bhajan search functionality
- `test_audio_player.spec.js` - Audio player controls

## CI/CD Pipeline

**Trigger:** Push to `main` or `master` branch

**Steps:**
1. **Setup** - Install Python 3.11, Node.js, PostgreSQL, Redis
2. **Unit Tests** - Run pytest on backend code
3. **E2E Tests** - Run Playwright on full app
4. **Fix Agent** (if tests fail)
   - Analyzes failures
   - Generates fixes
   - Creates PR for review
5. **Deploy** (if tests pass)
   - SSH to GCP
   - Pull latest code
   - Restart services
6. **Health Check** - Verify production is up
7. **Notify** - Send Telegram message with status

## Auto-Fix Agent

**How it works:**

1. GitHub Actions detects test failure
2. Spawns OpenClaw subagent (Claude Sonnet)
3. Subagent analyzes:
   - Error message
   - Stack trace
   - Test code
   - Application code
4. Generates fix:
   - Identifies root cause
   - Proposes code changes
   - Creates git branch
5. Creates PR for human review
6. Comments on original PR with link

**Example:**
```
Test failed: "Homepage loads successfully"
Error: Timeout waiting for element

Fix Agent:
1. Analyzes: Selector changed
2. Proposes: Update selector in test
3. Creates: PR #123 "Fix: Update homepage test selector"
4. Comments: "🤖 Auto-fix available in PR #123"
```

## GitHub Secrets Required

Set these in GitHub repo settings (Settings → Secrets and variables → Actions):

- `GCP_SSH_KEY` - SSH private key for GCP deployment
- `GCP_HOST` - GCP server IP (34.93.110.163)
- `TELEGRAM_BOT_TOKEN` - Bot token for notifications
- `TELEGRAM_CHAT_ID` - Your Telegram user ID
- `OPENCLAW_TOKEN` - OpenClaw API token (for Fix Agent)
- `GITHUB_TOKEN` - Auto-provided by GitHub

## Writing New Tests

### E2E Test Template
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    await page.goto('/');
    
    // Your test logic
    await expect(page.locator('...')).toBeVisible();
  });
});
```

### Unit Test Template
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_feature():
    response = client.get("/api/endpoint")
    assert response.status_code == 200
```

## Debugging Failed Tests

**Locally:**
```bash
# Run in headed mode (see browser)
npx playwright test --headed

# Run specific test
npx playwright test tests/e2e/test_homepage.spec.js

# Debug mode (step through)
npx playwright test --debug
```

**On CI:**
1. Check GitHub Actions logs
2. Download test videos (artifacts)
3. Download Playwright report (artifacts)
4. Review Fix Agent PR

## Test Coverage Goals

**Target:** 80% code coverage

**Critical paths to test:**
- [ ] Homepage loads
- [ ] Search works
- [ ] Audio playback
- [ ] Database queries
- [ ] API endpoints
- [ ] Error handling
- [ ] Mobile responsive

## Performance Benchmarks

**E2E tests should complete in:**
- Locally: <2 minutes
- CI: <5 minutes

**Unit tests should complete in:**
- Locally: <10 seconds
- CI: <30 seconds

## Maintenance

**Weekly:**
- Review Fix Agent PRs
- Update test selectors if UI changed
- Add tests for new features

**Monthly:**
- Update Playwright version
- Update pytest dependencies
- Review flaky tests (re-runs >2)

## Troubleshooting

**Test fails locally but passes in CI:**
- Check timing (add waits)
- Check data (seed test database)
- Check environment variables

**Test is flaky (passes sometimes):**
- Add explicit waits (`waitForLoadState`)
- Use `toBeVisible({ timeout: 10000 })` 
- Check for race conditions

**Fix Agent creates wrong fix:**
- Review the PR
- Close if incorrect
- Fix manually
- Update test to be clearer

## Cost Analysis

**CI/CD:**
- GitHub Actions: FREE (2000 min/month for private repos)
- Test runs: ~5 min per push
- Monthly cost: $0

**Fix Agent:**
- OpenClaw API: ~$0.05 per failure analysis
- Average: 1-2 failures per week
- Monthly cost: ~$0.20-0.40

**Total monthly cost: <$0.50**

## Success Metrics

**Week 1:**
- ✅ 10 tests passing
- ✅ CI/CD pipeline working
- ⏸️ Fix Agent tested (no failures yet)

**Month 1:**
- 🎯 20 tests total
- 🎯 90% pass rate
- 🎯 1-2 Fix Agent PRs reviewed

**Month 3:**
- 🎯 50 tests total
- 🎯 95% pass rate
- 🎯 <5% regression rate
