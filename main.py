"""
Belaguru Bhajan Portal - FastAPI Backend
"""
import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Global exception handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {"error": str(exc)}, 500


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    logger.warning(f"HTTP Exception {exc.status_code}: {exc.detail}")
    return {"error": exc.detail}, exc.status_code


logger.info("Exception handlers registered")

# Ensure directories exist
os.makedirs("./data", exist_ok=True)
os.makedirs("./static", exist_ok=True)

logger.info("Directories verified")

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
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
            uploader_name=uploader_name
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
    db: Session = Depends(get_db)
):
    """Update bhajan (tags and title)"""
    bhajan = db.query(Bhajan).filter(
        Bhajan.id == bhajan_id,
        Bhajan.deleted_at == None
    ).first()
    
    if not bhajan:
        raise HTTPException(status_code=404, detail="Bhajan not found")
    
    # Update title if provided
    if title and len(title) >= 3:
        bhajan.title = title
    
    # Update tags
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        bhajan.set_tags(tag_list)
    
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
        return {"status": "unhealthy", "error": str(e)}, 500


# Serve static files
@app.get("/")
def serve_index():
    """Serve index.html"""
    return FileResponse("static/index.html")


@app.get("/{path:path}")
def serve_static(path: str):
    """Serve static files"""
    file_path = f"static/{path}"
    
    if os.path.exists(file_path):
        return FileResponse(file_path)
    
    # Return index.html for SPA routing
    return FileResponse("static/index.html")


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
        logger.info("Starting uvicorn server...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 8000)),
            log_level="info",  # More verbose for debugging
            access_log=True,
            server_header=False,
        )
    except Exception as e:
        logger.error(f"Server crashed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")
