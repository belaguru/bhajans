# E2E Testing Guide

## Run Modes

### 1. Headless (Default - Fast)
```bash
npm run test:e2e
# or
npx playwright test
```
Tests run in background, no visible browser.

---

### 2. Headed (See Browser)
```bash
npm run test:e2e:headed
# or
npx playwright test --headed
```
Browser window opens, you can watch tests run.

---

### 3. Slow Motion (Watch Each Step)
```bash
npx playwright test --headed --slow-mo=1000
```
1000ms = 1 second delay between actions. Adjust as needed:
- `--slow-mo=500` - Half second
- `--slow-mo=2000` - 2 seconds

---

### 4. Debug Mode (Interactive)
```bash
npm run test:e2e:debug
# or
npx playwright test --debug
```
Opens Playwright Inspector:
- Pause/resume tests
- Step through actions
- Inspect elements
- See console logs

---

### 5. UI Mode (Best for Development)
```bash
npm run test:e2e:ui
# or
npx playwright test --ui
```
Opens interactive UI:
- Run tests individually
- See live browser
- Time travel through test steps
- View traces

---

## Run Specific Tests

### Single File
```bash
npx playwright test tests/e2e/test_homepage.spec.js --headed
```

### Single Test
```bash
npx playwright test -g "Homepage loads successfully" --headed
```

### By Tag/Describe Block
```bash
npx playwright test tests/e2e/test_youtube_playback.spec.js --headed
```

---

## Useful Flags

### See Output
```bash
npx playwright test --headed --reporter=list
```

### Keep Browser Open on Failure
```bash
npx playwright test --headed --retries=0
```

### Run in Parallel
```bash
npx playwright test --headed --workers=3
```

### Generate HTML Report
```bash
npx playwright test
npx playwright show-report
```

---

## Configuration

**Permanent headless toggle:**

Edit `playwright.config.js`:
```js
use: {
  headless: false,  // true = headless, false = headed
  slowMo: 500,      // ms delay between actions
}
```

**Environment-based:**
```js
use: {
  headless: process.env.HEADLESS !== 'false',
}
```

Then run:
```bash
HEADLESS=false npm run test:e2e
```

---

## Debugging Tips

### 1. Use Codegen (Record Tests)
```bash
npx playwright codegen http://localhost:8001
```
Records your actions as test code!

### 2. Take Screenshots
```bash
npx playwright test --headed --screenshot=on
```

### 3. Record Video
```bash
npx playwright test --headed --video=on
```

### 4. Slow Down Specific Test
In your test file:
```js
test.use({ slowMo: 2000 });

test('my slow test', async ({ page }) => {
  // This test runs with 2s delay
});
```

### 5. Pause Test
In your test:
```js
await page.pause();
```
Test pauses, opens inspector.

---

## Current Test Suite

**Total:** 31 E2E tests

**Files:**
- `test_homepage.spec.js` - 3 tests
- `test_search.spec.js` - 3 tests
- `test_audio_player.spec.js` - 2 tests
- `test_frontend_comprehensive.spec.js` - 14 tests
- `test_youtube_playback.spec.js` - 9 tests

**Run time:**
- Headless: ~23 seconds
- Headed: ~30 seconds
- Debug mode: As fast as you click

---

## Quick Commands Summary

```bash
# Watch tests run
npm run test:e2e:headed

# Step through tests
npm run test:e2e:debug

# Interactive UI
npm run test:e2e:ui

# Slow motion
npx playwright test --headed --slow-mo=1000

# Single test
npx playwright test -g "test name" --headed

# Keep browser open
npx playwright test --headed --debug

# Generate report
npx playwright show-report
```

---

**Pro Tip:** Use `npm run test:e2e:ui` for development - it's the best experience!
