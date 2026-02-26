# 🧡 Belaguru Bhajan Portal

A community-driven Bhajan portal with a native responsive UI, built with Hanuman Tilak deep orange theme.

## Features

✅ **Community Uploads** - Anyone can upload bhajans  
✅ **Full-Text Search** - Search by title or lyrics  
✅ **Tag Filtering** - Browse by tags  
✅ **Native Responsive Design** - Mobile-first, works on all devices  
✅ **Hanuman Theme** - Deep orange (#FF6B35) Hanuman Tilak colors  
✅ **No Build Tools** - Static HTML/CSS/JS with Tailwind CDN  
✅ **SQLite Database** - Simple, no external dependencies  

## Tech Stack

- **Backend:** FastAPI + Python
- **Frontend:** Vanilla JS + Tailwind CSS (CDN)
- **Database:** SQLite
- **Server:** Uvicorn

## Setup

### 1. Create Virtual Environment

```bash
cd ~/Projects/belaguru-portal
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
python3 -c "from models import init_db; init_db()"
```

### 4. Run Server

```bash
python3 main.py
```

Server runs on: `http://localhost:8000`

## Project Structure

```
belaguru-portal/
├── main.py                 # FastAPI backend
├── models.py              # SQLAlchemy models
├── requirements.txt       # Python dependencies
├── static/
│   ├── index.html        # Main HTML (SPA)
│   ├── app.js            # Frontend logic
│   └── style.css         # Theme & styling
└── README.md
```

## API Endpoints

### Get All Bhajans
```
GET /api/bhajans
GET /api/bhajans?search=Krishna
GET /api/bhajans?tag=Hanuman
```

### Get Single Bhajan
```
GET /api/bhajans/{id}
```

### Create Bhajan
```
POST /api/bhajans
Content-Type: application/x-www-form-urlencoded

title=Hanuman Chalisa
lyrics=Om Shankara...
tags=Hanuman,Sanskrit,Devotional
uploader_name=Kashi
```

### Get All Tags
```
GET /api/tags
```

### Portal Stats
```
GET /api/stats
```

## Color Scheme (Hanuman Tilak Theme)

```
Primary Orange:    #FF6B35
Deep Orange:       #E67E22
Golden Accent:     #FFD700
Saffron:           #FF9933
Background:        #F8F6F1 (Cream)
Dark Text:         #2C2416
```

## Features

### Homepage
- Search bar (real-time search)
- Tag sidebar (filter by tags)
- Bhajan grid (responsive, mobile-first)
- Each card shows: title, uploader, preview, tags

### Upload Page
- Title input
- Lyrics textarea (12 rows, expandable)
- Tags input (comma-separated)
- Optional uploader name
- Form validation
- Community upload disclaimer

### Bhajan Detail
- Full lyrics with formatting
- All tags
- Uploader name and date
- Copy to clipboard button
- Mobile-friendly reading

## Responsive Design

- **Mobile (< 640px):** Single column, full width
- **Tablet (640px - 1024px):** Grid adjusts
- **Desktop (> 1024px):** Sidebar + 3-column grid

All designed mobile-first, scales up beautifully.

## Database

SQLite database stores:
- `bhajans` table with: id, title, lyrics, tags (JSON), uploader_name, created_at, updated_at

## Usage Tips

1. **Search:** Type in search bar, results update in real-time
2. **Filter:** Click tags in sidebar to filter
3. **Upload:** Click "+ Upload" button, fill form
4. **Read:** Click any bhajan to see full lyrics
5. **Copy:** Use "Copy" button to copy lyrics to clipboard

## Future Enhancements

- User accounts & authentication
- Bhajan ratings/likes
- Comments on bhajans
- Download as PDF
- Audio playback
- Multi-language support

## Support

For issues or questions, check the code comments or reach out!

---

**Built with ❤️ for Belaguru Bhajans**
