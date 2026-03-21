# Automated Testing Setup

**Pre-commit hooks, pre-push checks, and nightly test runs**

---

## ✅ Installation Complete

All automated testing is configured and ready.

### **1. Pre-Commit Hook** ⚡
**Installed:** `.git/hooks/pre-commit`  
**Runs:** Before every `git commit`  
**Tests:** Unit tests only (fast ~2 seconds)  
**Action:** Blocks commit if tests fail

### **2. Pre-Push Hook** 🚀
**Installed:** `.git/hooks/pre-push`  
**Runs:** Before every `git push`  
**Tests:** Full suite (unit + E2E, ~25 seconds)  
**Action:** Blocks push if tests fail

### **3. Nightly Tests** 🌙
**Script:** `run-nightly-tests.sh`  
**Schedule:** Every day at 2:00 AM  
**Tests:** Full suite + coverage report  
**Reports:** Saved to `test-reports/`

---

## Installation

### Install Nightly Cron Job

```bash
cd ~/Projects/belaguru-bhajans
./install-nightly-tests.sh
```

**Or manually:**
```bash
crontab -e
# Add this line:
0 2 * * * $HOME/Projects/belaguru-bhajans/run-nightly-tests.sh >> $HOME/Projects/belaguru-bhajans/test-reports/cron.log 2>&1
```

---

## How It Works

### Pre-Commit (Every Commit)

```bash
git add .
git commit -m "message"

# Automatic:
# 🧪 Running tests before commit...
# 📝 Running unit tests...
# ✅ All unit tests passed!
# ✅ Commit allowed!
```

**If tests fail:**
```
❌ Unit tests failed! Commit blocked.
Fix the tests before committing.
```

### Pre-Push (Every Push)

```bash
git push origin main

# Automatic:
# 🚀 Running full test suite before push...
# 📝 Running unit tests...
# ✅ Unit tests passed!
# 🌐 Running E2E tests...
# ✅ All tests passed!
# ✅ Push allowed!
```

**If tests fail:**
```
❌ E2E tests failed! Push blocked.
Run 'npm run test:e2e:headed' to debug.
```

### Nightly Run (2:00 AM Daily)

**Automatically:**
1. Pulls latest code from GitHub
2. Updates dependencies
3. Restarts staging server
4. Runs unit tests with coverage
5. Runs E2E tests
6. Generates reports
7. (Optional) Sends Telegram notification

**Report example:**
```
🌙 Nightly Test Run - 2026-03-21-020000
================================================

📥 Pulling latest code...
📦 Updating dependencies...
🔄 Restarting staging server...
📝 Running unit tests with coverage...
🌐 Running E2E tests...

================================================
📊 Test Summary
================================================
✅ Unit Tests: PASSED
✅ E2E Tests: PASSED

📁 Full report: test-reports/nightly-2026-03-21-020000.txt
📊 Coverage report: htmlcov/index.html

🎯 Nightly test run complete!
```

---

## View Reports

### Nightly Reports
```bash
ls -lt ~/Projects/belaguru-bhajans/test-reports/
cat ~/Projects/belaguru-bhajans/test-reports/nightly-*.txt
```

### Coverage Report
```bash
open ~/Projects/belaguru-bhajans/htmlcov/index.html
```

### Cron Log
```bash
tail -f ~/Projects/belaguru-bhajans/test-reports/cron.log
```

---

## Configuration

### Change Nightly Schedule

**Edit crontab:**
```bash
crontab -e
```

**Examples:**
```cron
# Every day at 2:00 AM (current)
0 2 * * * /path/to/run-nightly-tests.sh

# Every day at midnight
0 0 * * * /path/to/run-nightly-tests.sh

# Twice daily (2 AM and 2 PM)
0 2,14 * * * /path/to/run-nightly-tests.sh

# Only weekdays at 3 AM
0 3 * * 1-5 /path/to/run-nightly-tests.sh
```

### Skip Hooks Temporarily

**Skip pre-commit:**
```bash
git commit --no-verify -m "message"
```

**Skip pre-push:**
```bash
git push --no-verify origin main
```

⚠️ **Use sparingly** - hooks are safety guardrails!

### Disable Hooks

**Temporarily (rename):**
```bash
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
mv .git/hooks/pre-push .git/hooks/pre-push.disabled
```

**Re-enable:**
```bash
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
mv .git/hooks/pre-push.disabled .git/hooks/pre-push
```

**Permanently (delete):**
```bash
rm .git/hooks/pre-commit
rm .git/hooks/pre-push
```

---

## Telegram Notifications (Optional)

**Enable notifications in `run-nightly-tests.sh`:**

1. Create Telegram bot (talk to @BotFather)
2. Get bot token
3. Get your chat ID
4. Edit `run-nightly-tests.sh`:

```bash
# Uncomment and configure:
curl -s -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
  -d chat_id=<YOUR_CHAT_ID> \
  -d text="$MESSAGE" > /dev/null
```

**Test notification:**
```bash
~/Projects/belaguru-bhajans/run-nightly-tests.sh
```

---

## Troubleshooting

### Pre-commit hook not running

**Check if executable:**
```bash
ls -la .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Nightly tests not running

**Check crontab:**
```bash
crontab -l
```

**Check cron log:**
```bash
tail -f ~/Projects/belaguru-bhajans/test-reports/cron.log
```

**Test manually:**
```bash
~/Projects/belaguru-bhajans/run-nightly-tests.sh
```

### Tests fail in cron but pass manually

**Issue:** Environment variables (PATH, venv)

**Fix in `run-nightly-tests.sh`:**
```bash
# Add at top:
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
source $HOME/.zshrc  # or .bashrc
```

---

## Files

```
.git/hooks/pre-commit          # Pre-commit hook
.git/hooks/pre-push             # Pre-push hook
run-nightly-tests.sh            # Nightly test runner
install-nightly-tests.sh        # Cron installer
test-reports/                   # Test reports directory
  nightly-*.txt                 # Daily reports
  cron.log                      # Cron execution log
```

---

## Best Practices

### ✅ DO
- Let hooks run (they catch bugs early)
- Review nightly reports weekly
- Fix failing tests immediately
- Add tests when adding features

### ❌ DON'T
- Skip hooks frequently (--no-verify)
- Ignore failing nightly tests
- Commit broken code
- Disable safety checks

---

## Summary

**Automated testing ensures:**
- ✅ No broken code committed
- ✅ No broken code pushed to GitHub
- ✅ Daily health checks (even if you're not working)
- ✅ Coverage reports generated automatically
- ✅ Issues caught before production

**Philosophy:** Tests should run automatically, not manually. If you have to remember to run tests, you'll forget.

---

**Created:** 2026-03-21 18:08 IST  
**Maintained by:** Kashi Viswanatha
