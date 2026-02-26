# 🧡 Belaguru Bhajan Portal - LAUNCH GUIDE

## 🚀 Portal is LIVE!

**Server Status:** ✅ Running on `http://localhost:8000`  
**Database:** ✅ Initialized  
**Community Ready:** ✅ Accept uploads  

---

## What We Built

A **community-driven bhajan portal** with:

- 🔍 **Real-time search** (title + lyrics)
- 🏷️ **Tag filtering** (browse by theme)
- 📱 **Native responsive UI** (mobile-first)
- 🧡 **Hanuman Tilak theme** (deep orange #FF6B35)
- ⚡ **Zero build tools** (static + CDN)
- 🔓 **Community uploads** (anyone can contribute)

---

## How to Use

### 1. Access Portal
Open in browser: **http://localhost:8000**

### 2. User Experience

**Homepage:**
- Search bar at top
- Tag sidebar on left (click to filter)
- Bhajan cards in grid
- Shows: title, uploader, preview, tags

**Upload Bhajan:**
- Click "+ Upload" button
- Fill: title, lyrics, tags (optional), name (optional)
- Submit
- Bhajan appears immediately

**View Bhajan:**
- Click any bhajan card
- See full lyrics
- Click "Copy" to copy to clipboard
- Click "Back" to return

### 3. Share Portal URL
Give community this link: `http://localhost:8000`

---

## Features

### Search
```
🔍 Type in search bar
→ Real-time filtering by title/lyrics
→ Results update instantly
```

### Tags
```
📑 Click any tag in sidebar
→ Filters to bhajans with that tag
→ Click again to clear filter
```

### Upload
```
+ Upload button
→ Form with 4 fields
→ Title (required)
→ Lyrics (required)
→ Tags (optional, comma-separated)
→ Your name (optional)
→ Auto-validates on submit
```

### Copy
```
📋 Click "Copy" button
→ Full lyrics copied to clipboard
→ Works on mobile + desktop
```

---

## Design

### Colors (Hanuman Tilak Theme)
- 🧡 **Primary:** Deep Orange (#FF6B35)
- 🟠 **Dark:** Dark Orange (#E67E22)
- 🟡 **Accent:** Golden (#FFD700)
- 🟠 **Secondary:** Saffron (#FF9933)
- ⚪ **Background:** Cream (#F8F6F1)

### Responsive
- **Mobile:** Full-width, single column
- **Tablet:** 2-column grid
- **Desktop:** 3-column grid + sidebar
- All scales beautifully

---

## API Reference

### Get All Bhajans
```bash
curl http://localhost:8000/api/bhajans
```

### Search
```bash
curl "http://localhost:8000/api/bhajans?search=krishna"
```

### Filter by Tag
```bash
curl "http://localhost:8000/api/bhajans?tag=Hanuman"
```

### Get Single Bhajan
```bash
curl http://localhost:8000/api/bhajans/1
```

### Create Bhajan
```bash
curl -X POST http://localhost:8000/api/bhajans \
  -d "title=Hanuman Chalisa" \
  -d "lyrics=Om Shankara..." \
  -d "tags=Hanuman,Sanskrit" \
  -d "uploader_name=Kashi"
```

### Get All Tags
```bash
curl http://localhost:8000/api/tags
```

### Stats
```bash
curl http://localhost:8000/api/stats
```

---

## Database

**Location:** `/home/kreddy/.belaguru/portal.db`

**Table: bhajans**
```
- id (int, primary key)
- title (string, indexed)
- lyrics (text)
- tags (JSON array)
- uploader_name (string)
- created_at (datetime, indexed)
- updated_at (datetime)
```

---

## Deployment

### Local (Development)
```bash
cd ~/Projects/belaguru-portal
bash start.sh
# Opens on http://localhost:8000
```

### Production (Future)
Deploy to:
- **AWS:** EC2 + RDS
- **Heroku:** Git push
- **DigitalOcean:** App Platform
- **Self-hosted:** Any Linux + Python

---

## Maintenance

### Monitor
```bash
tail -f ~/.belaguru/portal.log
```

### Restart
```bash
pkill -f "python.*main.py"
cd ~/Projects/belaguru-portal && bash start.sh
```

### Backup Database
```bash
cp ~/.belaguru/portal.db ~/.belaguru/portal.db.backup
```

---

## Future Enhancements

1. **User Accounts**
   - Register/login
   - Track uploads
   - Favorites list

2. **Ratings & Comments**
   - Star ratings
   - Comments section
   - Community engagement

3. **Media**
   - Audio playback
   - PDF download
   - Share links

4. **Admin Dashboard**
   - Flag inappropriate content
   - Merge duplicate bhajans
   - Analytics

5. **Multi-language**
   - Kannada UI
   - Tamil, Telugu, Marathi support

---

## Troubleshooting

### Portal Not Loading
```bash
# Check if server is running
ps aux | grep "python.*main.py"

# Restart
cd ~/Projects/belaguru-portal && bash start.sh
```

### Database Issues
```bash
# Check database exists
ls -la ~/.belaguru/portal.db

# Reinitialize if needed
cd ~/Projects/belaguru-portal && source venv/bin/activate
python3 -c "from models import init_db; init_db()"
```

### Slow Search
```bash
# Database is SQLite, suitable for <10k bhajans
# For large scale, migrate to PostgreSQL
```

---

## Community Guidelines

✅ **Do:**
- Upload authentic bhajans
- Use meaningful tags
- Include full lyrics
- Credit original composers when known

❌ **Don't:**
- Spam or duplicate entries
- Upload incomplete lyrics
- Add false attribution

---

## Contact & Support

For issues or questions, reach out!

---

## Credits

**Built with ❤️ for Belaguru Matt Devotees**

- **Portal:** Belaguru Bhajan Portal v1.0
- **Theme:** Hanuman Tilak (Deep Orange)
- **Tech:** FastAPI + SQLite + Vanilla JS
- **Design:** Mobile-first responsive

---

**Welcome to the community! 🙏🧡**
