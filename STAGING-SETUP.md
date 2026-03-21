# Belaguru Portal - Staging Environment

**Git Repo:** `git@github.com:belaguru/bhajans.git`  
**Branch:** main  
**Directory:** `~/Projects/belaguru-bhajans`

---

## 🌍 Live URLs

**Production:**
```
https://bhajans.s365.in
```

**Staging (QA):**
```
https://qa.bhajans.s365.in
```

---

## 🚀 Quick Start

### Start Staging Server
```bash
~/Projects/belaguru-bhajans/start-staging.sh
```

### Run Tests
```bash
~/Projects/belaguru-bhajans/run-tests.sh
```

### Update Code
```bash
cd ~/Projects/belaguru-bhajans
git pull origin main
sudo brew services restart nginx
```

---

## 📂 Directory Structure

```
~/Projects/belaguru-bhajans/
├── main.py              # FastAPI backend
├── models.py            # Database models
├── static/              # Frontend (HTML, CSS, JS)
├── data/                # SQLite database
├── tests/               # Test suite
│   ├── unit/           # pytest unit tests
│   └── e2e/            # Playwright E2E tests
├── .github/            # GitHub Actions CI/CD
├── venv/               # Python virtual environment
├── start-staging.sh    # Startup script
└── run-tests.sh        # Test runner
```

---

## 🧪 Testing

### Run All Tests
```bash
npm test
# or
./run-tests.sh
```

### Run Unit Tests Only
```bash
npm run test:unit
# or
source venv/bin/activate && pytest tests/unit/
```

### Run E2E Tests Only
```bash
npm run test:e2e
# or
npx playwright test
```

### Code Coverage
```bash
source venv/bin/activate
pytest tests/unit/ --cov=. --cov-report=html
open htmlcov/index.html
```

---

## 📊 Test Results

**Current Status:**
- Total Tests: 89 (58 unit + 31 E2E)
- Passing: 76 (93%)
- Code Coverage: 63%

**Documentation:**
- `TEST-REPORT.md` - Comprehensive test report
- `FEATURE-COVERAGE.md` - Feature coverage analysis
- `TESTING.md` - Testing guide

---

## 🔧 Configuration

### nginx
```
Config: /usr/local/etc/nginx/servers/belaguru-staging.conf
Logs: /usr/local/var/log/nginx/belaguru-staging-*.log
```

### Backend
```
Port: 8001
Host: 0.0.0.0
Reload: auto (--reload flag)
Logs: ~/Projects/belaguru-bhajans/staging.log
```

### Database
```
Type: SQLite
Location: ~/Projects/belaguru-bhajans/data/portal.db
Records: 197 bhajans, 56 tags
```

---

## 🔄 Deployment Workflow

### 1. Development
```bash
# Make changes
git add .
git commit -m "Description"
git push origin main
```

### 2. Staging (QA)
```bash
# Pull latest
cd ~/Projects/belaguru-bhajans
git pull origin main

# Restart services
sudo brew services restart nginx
pkill -f uvicorn
./start-staging.sh
```

### 3. Testing
```bash
# Run tests
./run-tests.sh

# Or manual
npm test
```

### 4. Production
```bash
# SSH to GCP
ssh kreddy@34.93.110.163

# Pull latest
cd ~/Projects/belaguru-portal
git pull origin main

# Restart
docker-compose restart
```

---

## 🐛 Troubleshooting

### Backend not starting
```bash
# Check logs
tail -50 ~/Projects/belaguru-bhajans/staging.log

# Check if port is in use
lsof -i :8001

# Restart
pkill -f uvicorn
./start-staging.sh
```

### nginx errors
```bash
# Test config
sudo nginx -t

# Check logs
tail -f /usr/local/var/log/nginx/belaguru-staging-error.log

# Restart
sudo brew services restart nginx
```

### 502 Bad Gateway
```bash
# Backend not responding
curl http://localhost:8001/health

# Restart backend
pkill -f uvicorn && ./start-staging.sh
```

### Permission denied (static files)
```bash
# Fix permissions
chmod -R o+rX ~/Projects/belaguru-bhajans/static
chmod o+x ~
chmod o+x ~/Projects
chmod o+x ~/Projects/belaguru-bhajans
```

---

## 📦 Dependencies

### Python (Backend)
```bash
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy python-multipart pytest pytest-cov httpx
```

### Node.js (Frontend Tests)
```bash
npm install
```

### System
```bash
brew install nginx postgresql@15 redis
brew install certbot  # For SSL
```

---

## 🔒 SSL Certificate

**Certificate:**
```
Location: /etc/letsencrypt/live/qa.bhajans.s365.in/
Expiry: 90 days
Auto-renew: Yes (via certbot)
```

**Manual renewal:**
```bash
sudo certbot renew
sudo brew services restart nginx
```

---

## 📝 Common Commands

**Start everything:**
```bash
./start-staging.sh
```

**Stop backend:**
```bash
pkill -f "uvicorn.*8001"
```

**View logs:**
```bash
tail -f ~/Projects/belaguru-bhajans/staging.log
tail -f /usr/local/var/log/nginx/belaguru-staging-access.log
```

**Check status:**
```bash
ps aux | grep uvicorn
ps aux | grep nginx
curl http://localhost:8001/health
curl https://qa.bhajans.s365.in/health
```

**Update from production:**
```bash
cd ~/Projects/belaguru-bhajans
scp kreddy@34.93.110.163:~/Projects/belaguru-portal/data/portal.db data/
```

---

## 📚 Documentation

- `TEST-REPORT.md` - Test coverage report
- `FEATURE-COVERAGE.md` - Feature analysis
- `TESTING.md` - Testing guide
- `TEST-COVERAGE.md` - Coverage metrics
- `README.md` - Project overview

---

**Created:** 2026-03-21  
**Last Updated:** 2026-03-21  
**Maintainer:** Kashi Viswanatha
