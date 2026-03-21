# Quick Reference - Belaguru Staging

## 🚀 Start Server
```bash
~/Projects/belaguru-bhajans/start-staging.sh
```

## 🧪 Run Tests
```bash
~/Projects/belaguru-bhajans/run-tests.sh
```

## 🔄 Update Code
```bash
cd ~/Projects/belaguru-bhajans
git pull origin main
sudo brew services restart nginx
```

## 🌍 URLs
- Production: https://bhajans.s365.in
- Staging: https://qa.bhajans.s365.in
- Local: http://localhost:8001

## 📝 Logs
```bash
tail -f ~/Projects/belaguru-bhajans/staging.log
tail -f /usr/local/var/log/nginx/belaguru-staging-error.log
```

## 🐛 Troubleshoot
```bash
# Check backend
curl http://localhost:8001/health

# Restart backend
pkill -f uvicorn && ./start-staging.sh

# Restart nginx
sudo brew services restart nginx
```

## 📊 Test Status
- Total: 89 tests (76 passing, 93%)
- Coverage: 63%
- Run: `npm test`

## 📚 Full Docs
- `STAGING-SETUP.md` - Complete guide
- `TEST-REPORT.md` - Test results
- `FEATURE-COVERAGE.md` - Coverage analysis
