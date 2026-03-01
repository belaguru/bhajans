"""
Belaguru Bhajan Portal - FastAPI Backend
"""
import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from pydantic import BaseModel
from typing import List, Optional
from models import Bhajan, init_db, get_db

# Configure comprehensive logging
LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{LOG_DIR}/portal_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("🧡 BELAGURU BHAJAN PORTAL STARTING")
logger.info("=" * 60)

# Initialize FastAPI
app = FastAPI(title="Belaguru Bhajan Portal")

logger.info("FastAPI app initialized")

# Get absolute path to static directory
STATIC_DIR = os.path.abspath("static")
logger.info(f"Static directory: {STATIC_DIR}")
logger.info(f"Static directory exists: {os.path.exists(STATIC_DIR)}")


# Global exception handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    raise HTTPException(status_code=500, detail=str(exc))


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    logger.warning(f"HTTP Exception {exc.status_code}: {exc.detail}")
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


logger.info("Exception handlers registered")

# Ensure directories exist
os.makedirs("./data", exist_ok=True)
os.makedirs("./static", exist_ok=True)

logger.info("Directories verified")

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
    
    # Run schema migration
    import sqlite3
    db_path = "./data/portal.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current columns
        cursor.execute("PRAGMA table_info(bhajans)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        # Add missing columns
        migrations = {
            "tags": "TEXT",
            "uploader_name": "TEXT",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
            "deleted_at": "DATETIME"
        }
        
        for col_name, col_type in migrations.items():
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE bhajans ADD COLUMN {col_name} {col_type}")
                logger.info(f"Added column: {col_name}")
        
        # Migrate data
        if "manual_tags" in columns and "tags" in columns:
            cursor.execute("UPDATE bhajans SET tags = COALESCE(manual_tags, '') WHERE tags = '' OR tags IS NULL")
        
        cursor.execute("UPDATE bhajans SET uploader_name = 'Unknown' WHERE uploader_name = '' OR uploader_name IS NULL")
        cursor.execute("UPDATE bhajans SET created_at = DATETIME('now') WHERE created_at IS NULL")
        cursor.execute("UPDATE bhajans SET updated_at = DATETIME('now') WHERE updated_at IS NULL")
        
        conn.commit()
        conn.close()
        logger.info("Database schema migration completed")
    except Exception as e:
        logger.warning(f"Schema migration skipped (might already be migrated): {e}")
        
except Exception as e:
    logger.error(f"Database initialization failed: {e}", exc_info=True)
    raise


# Pydantic models for API
class BhajanCreate(BaseModel):
    title: str
    lyrics: str
    tags: List[str] = []
    uploader_name: str = "Anonymous"


class BhajanResponse(BaseModel):
    id: int
    title: str
    lyrics: str
    tags: List[str]
    uploader_name: str
    youtube_url: Optional[str] = None
    created_at: str
    updated_at: str


# API Endpoints

@app.get("/api/bhajans", response_model=List[BhajanResponse])
def get_bhajans(
    search: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all bhajans with optional search/filter (excludes deleted)"""
    try:
        logger.info(f"GET /api/bhajans - search={search}, tag={tag}")
        
        query = db.query(Bhajan).filter(Bhajan.deleted_at == None)
        
        if search:
            search = f"%{search}%"
            query = query.filter(
                or_(
                    Bhajan.title.ilike(search),
                    Bhajan.lyrics.ilike(search)
                )
            )
        
        if tag:
            query = query.filter(Bhajan.tags.contains(f'"{tag}"'))
        
        query = query.order_by(desc(Bhajan.created_at))
        
        bhajans = query.all()
        logger.info(f"Returning {len(bhajans)} bhajans")
        return [b.to_dict() for b in bhajans]
    
    except Exception as e:
        logger.error(f"Error in get_bhajans: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bhajans/{bhajan_id}", response_model=BhajanResponse)
def get_bhajan(bhajan_id: int, db: Session = Depends(get_db)):
    """Get single bhajan by ID (excludes deleted)"""
    bhajan = db.query(Bhajan).filter(
        Bhajan.id == bhajan_id,
        Bhajan.deleted_at == None
    ).first()
    
    if not bhajan:
        raise HTTPException(status_code=404, detail="Bhajan not found")
    
    return bhajan.to_dict()


@app.post("/api/bhajans", response_model=BhajanResponse)
def create_bhajan(
    title: str = Form(...),
    lyrics: str = Form(...),
    tags: str = Form(""),
    uploader_name: str = Form("Anonymous"),
    youtube_url: str = Form(None),
    db: Session = Depends(get_db)
):
    """Create new bhajan"""
    try:
        logger.info(f"POST /api/bhajans - title={title[:50]}, uploader={uploader_name}, tags={tags}")
        
        # Parse tags
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        logger.info(f"Parsed {len(tag_list)} tags: {tag_list}")
        
        # Validate input
        if not title or len(title) < 3:
            logger.warning(f"Invalid title: {title}")
            raise HTTPException(status_code=400, detail="Title must be at least 3 characters")
        
        if not lyrics or len(lyrics) < 20:
            logger.warning(f"Invalid lyrics length: {len(lyrics)}")
            raise HTTPException(status_code=400, detail="Lyrics must be at least 20 characters")
        
        # Clean lyrics
        cleaned_lyrics = "\n".join(line.lstrip() for line in lyrics.split("\n"))
        logger.info(f"Cleaned lyrics: {len(cleaned_lyrics)} chars")
        
        # Create bhajan
        bhajan = Bhajan(
            title=title,
            lyrics=cleaned_lyrics,
            uploader_name=uploader_name,
            youtube_url=youtube_url.strip() if youtube_url else None
        )
        bhajan.set_tags(tag_list)
        
        logger.info(f"Creating bhajan in database...")
        db.add(bhajan)
        db.commit()
        db.refresh(bhajan)
        
        logger.info(f"✅ Bhajan created with ID {bhajan.id}")
        return bhajan.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_bhajan: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/bhajans/{bhajan_id}", response_model=BhajanResponse)
def update_bhajan(
    bhajan_id: int,
    title: Optional[str] = Form(None),
    lyrics: Optional[str] = Form(None),
    tags: str = Form(""),
    uploader_name: Optional[str] = Form(None),
    youtube_url: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Update bhajan (title, lyrics, tags, uploader_name)"""
    bhajan = db.query(Bhajan).filter(
        Bhajan.id == bhajan_id,
        Bhajan.deleted_at == None
    ).first()

    if not bhajan:
        raise HTTPException(status_code=404, detail="Bhajan not found")

    # Update title if provided
    if title and len(title) >= 3:
        bhajan.title = title

    # Update lyrics if provided
    if lyrics and len(lyrics) >= 20:
        cleaned_lyrics = "\n".join(line.lstrip() for line in lyrics.split("\n"))
        bhajan.lyrics = cleaned_lyrics

    # Update tags
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    bhajan.set_tags(tag_list)

    # Update uploader name if provided
    if uploader_name:
        bhajan.uploader_name = uploader_name

    # Update YouTube URL if provided
    if youtube_url is not None:
        bhajan.youtube_url = youtube_url.strip() if youtube_url else None

    bhajan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(bhajan)

    return bhajan.to_dict()


@app.delete("/api/bhajans/{bhajan_id}")
def delete_bhajan(bhajan_id: int, db: Session = Depends(get_db)):
    """Soft delete bhajan (marks as deleted, doesn't remove)"""
    bhajan = db.query(Bhajan).filter(
        Bhajan.id == bhajan_id,
        Bhajan.deleted_at == None
    ).first()
    
    if not bhajan:
        raise HTTPException(status_code=404, detail="Bhajan not found")
    
    # Soft delete: just set deleted_at timestamp
    from datetime import datetime
    bhajan.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return {"status": "deleted", "id": bhajan_id}


@app.get("/api/tags")
def get_all_tags(db: Session = Depends(get_db)):
    """Get all unique tags"""
    import json
    
    bhajans = db.query(Bhajan).all()
    tags_set = set()
    
    for bhajan in bhajans:
        tags = bhajan.get_tags()
        tags_set.update(tags)
    
    return sorted(list(tags_set))


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get portal statistics"""
    try:
        logger.info("GET /api/stats")
        total_bhajans = db.query(Bhajan).filter(Bhajan.deleted_at == None).count()
        logger.info(f"Stats: {total_bhajans} bhajans")
        
        return {
            "total_bhajans": total_bhajans,
            "status": "online",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in get_stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    try:
        logger.debug("Health check")
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Serve static files
@app.get("/", response_class=FileResponse)
def serve_index():
    """Serve index.html"""
    index_path = os.path.join(STATIC_DIR, "index.html")
    logger.info(f"[ROOT REQUEST] Serving index from: {index_path}")
    logger.info(f"[ROOT REQUEST] File exists: {os.path.exists(index_path)}")
    if not os.path.exists(index_path):
        logger.error(f"[ROOT REQUEST] FILE NOT FOUND: {index_path}")
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)


@app.get("/{path:path}")
def serve_static(path: str):
    """Serve static files"""
    file_path = os.path.join(STATIC_DIR, path)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Return index.html for SPA routing
    logger.info(f"Path not found: {file_path}, serving index.html instead")
    index_path = os.path.join(STATIC_DIR, "index.html")
    return FileResponse(index_path, media_type="text/html")


if __name__ == "__main__":
    import uvicorn
    import signal
    import sys
    
    logger.info("=" * 60)
    logger.info("Server starting on http://0.0.0.0:8000")
    logger.info("Public IP: http://34.93.110.163:8000")
    logger.info("Auto-restart: ENABLED")
    logger.info("=" * 60)
    
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Starting uvicorn server on port {port}...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            server_header=False,
            lifespan="on",
        )
    except Exception as e:
        logger.error(f"Server crashed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")
