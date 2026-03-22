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
from dual_write import dual_write_tags, read_bhajan_tags, get_bhajan_with_unified_tags

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


class TagCreate(BaseModel):
    name: str
    category: str
    parent_id: Optional[int] = None
    translations: dict = {}
    synonyms: List[str] = []


class TagUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    parent_id: Optional[int] = None
    translations: Optional[dict] = None
    synonyms: Optional[List[str]] = None


# API Endpoints

@app.get("/api/bhajans", response_model=List[BhajanResponse])
def get_bhajans(
    search: Optional[str] = None,
    tag: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """Get all bhajans with optional search/filter (excludes deleted)
    
    Enhanced tag filtering:
    - Supports multiple tags (AND logic)
    - Resolves synonyms to canonical tags
    - Includes hierarchical search (child tags)
    
    Args:
        search: Search in title/lyrics
        tag: Tag name(s) to filter by (can be repeated: ?tag=Hanuman&tag=Stotra)
    """
    import sqlite3
    import json as json_lib
    
    try:
        logger.info(f"GET /api/bhajans - search={search}, tag={tag}")
        
        # If tag filtering requested, use taxonomy search
        if tag:
            conn = sqlite3.connect("./data/portal.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Resolve tag names to IDs (with synonym resolution and hierarchy)
            def resolve_tag_name(tag_name):
                """Resolve tag name to canonical tag ID (handles synonyms)"""
                # Try direct match
                cursor.execute("SELECT id FROM tag_taxonomy WHERE name = ?", (tag_name,))
                row = cursor.fetchone()
                if row:
                    return row["id"]
                
                # Try synonym match
                cursor.execute("SELECT tag_id FROM tag_synonyms WHERE synonym = ?", (tag_name,))
                row = cursor.fetchone()
                if row:
                    return row["tag_id"]
                
                return None
            
            def get_descendant_ids(tid):
                """Get all descendant tag IDs recursively"""
                descendants = [tid]
                cursor.execute("SELECT id FROM tag_taxonomy WHERE parent_id = ?", (tid,))
                children = cursor.fetchall()
                for child in children:
                    descendants.extend(get_descendant_ids(child["id"]))
                return descendants
            
            # Resolve all tag names to tag ID sets (including descendants)
            tag_id_sets = []
            for tag_name in tag:
                tag_id = resolve_tag_name(tag_name)
                if tag_id:
                    tag_id_sets.append(set(get_descendant_ids(tag_id)))
            
            if not tag_id_sets:
                # No valid tags found
                conn.close()
                return []
            
            # Find bhajans that match ALL tag sets (AND logic)
            # First tag set
            placeholders = ",".join("?" * len(tag_id_sets[0]))
            query = f"""
                SELECT DISTINCT bhajan_id FROM bhajan_tags
                WHERE tag_id IN ({placeholders})
            """
            cursor.execute(query, list(tag_id_sets[0]))
            matching_bhajan_ids = {row["bhajan_id"] for row in cursor.fetchall()}
            
            # Intersect with other tag sets
            for tag_id_set in tag_id_sets[1:]:
                placeholders = ",".join("?" * len(tag_id_set))
                query = f"""
                    SELECT DISTINCT bhajan_id FROM bhajan_tags
                    WHERE tag_id IN ({placeholders})
                """
                cursor.execute(query, list(tag_id_set))
                matching_bhajan_ids &= {row["bhajan_id"] for row in cursor.fetchall()}
            
            if not matching_bhajan_ids:
                conn.close()
                return []
            
            # Get bhajan details
            placeholders = ",".join("?" * len(matching_bhajan_ids))
            query_sql = f"""
                SELECT id, title, lyrics, tags, uploader_name, youtube_url, created_at, updated_at
                FROM bhajans
                WHERE id IN ({placeholders})
                  AND deleted_at IS NULL
            """
            
            params = list(matching_bhajan_ids)
            
            if search:
                search_pattern = f"%{search}%"
                query_sql += " AND (title LIKE ? OR lyrics LIKE ?)"
                params.extend([search_pattern, search_pattern])
            
            query_sql += " ORDER BY created_at DESC"
            
            cursor.execute(query_sql, params)
            
            bhajans = []
            for row in cursor.fetchall():
                bhajans.append({
                    "id": row["id"],
                    "title": row["title"],
                    "lyrics": row["lyrics"],
                    "tags": json_lib.loads(row["tags"]) if row["tags"] else [],
                    "uploader_name": row["uploader_name"],
                    "youtube_url": row["youtube_url"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            
            conn.close()
            logger.info(f"Returning {len(bhajans)} bhajans")
            return bhajans
        
        # No tag filter - use ORM query
        query = db.query(Bhajan).filter(Bhajan.deleted_at == None)
        
        if search:
            search = f"%{search}%"
            query = query.filter(
                or_(
                    Bhajan.title.ilike(search),
                    Bhajan.lyrics.ilike(search)
                )
            )
        
        query = query.order_by(desc(Bhajan.created_at))
        
        bhajans = query.all()
        logger.info(f"Returning {len(bhajans)} bhajans")
        
        # Return with unified tags (prefers taxonomy)
        return [get_bhajan_with_unified_tags(db, b.id) for b in bhajans]
    
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
    
    # Return with unified tags (prefers taxonomy)
    return get_bhajan_with_unified_tags(db, bhajan_id)


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
        
        logger.info(f"Creating bhajan in database...")
        db.add(bhajan)
        db.commit()
        db.refresh(bhajan)
        
        # Dual-write tags (to both JSON field and taxonomy table)
        logger.info(f"Writing {len(tag_list)} tags using dual-write strategy...")
        dual_write_tags(db, bhajan.id, tag_list, source="manual")
        
        logger.info(f"✅ Bhajan created with ID {bhajan.id}")
        
        # Return with unified tags
        return get_bhajan_with_unified_tags(db, bhajan.id)
    
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

    # Update tags using dual-write strategy
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    if tag_list:
        dual_write_tags(db, bhajan.id, tag_list, source="manual")

    # Update uploader name if provided
    if uploader_name:
        bhajan.uploader_name = uploader_name

    # Update YouTube URL if provided
    if youtube_url is not None:
        bhajan.youtube_url = youtube_url.strip() if youtube_url else None

    bhajan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(bhajan)

    # Return with unified tags
    return get_bhajan_with_unified_tags(db, bhajan.id)


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
def get_all_tags(
    category: Optional[str] = None,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all canonical tags with optional filters
    
    Args:
        category: Filter by category (deity, type, composer, etc.)
        parent_id: Get only children of specified parent tag
    
    Returns:
        List of tags with structure: [{id, name, category, level, parent_id, translations}]
    """
    import sqlite3
    
    conn = sqlite3.connect("./data/portal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query with filters
    query = "SELECT id, name, category, level, parent_id FROM tag_taxonomy WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    if parent_id is not None:
        query += " AND parent_id = ?"
        params.append(parent_id)
    
    query += " ORDER BY level, category, name"
    
    cursor.execute(query, params)
    tags = []
    
    for row in cursor.fetchall():
        tag_id = row["id"]
        
        # Get translations for this tag
        cursor.execute(
            "SELECT language, translation FROM tag_translations WHERE tag_id = ?",
            (tag_id,)
        )
        translations = {t["language"]: t["translation"] for t in cursor.fetchall()}
        
        tags.append({
            "id": tag_id,
            "name": row["name"],
            "category": row["category"],
            "level": row["level"],
            "parent_id": row["parent_id"],
            "translations": translations
        })
    
    conn.close()
    return tags


@app.get("/api/tags/tree")
def get_tags_tree(db: Session = Depends(get_db)):
    """Get hierarchical tag tree structure
    
    Returns nested JSON like:
    {
        "Deity": {
            "id": 1,
            "category": "root",
            "children": {
                "Vishnu": {
                    "id": 3,
                    "category": "deity",
                    "children": {
                        "Krishna": {...},
                        "Rama": {...}
                    }
                }
            }
        }
    }
    """
    import sqlite3
    
    conn = sqlite3.connect("./data/portal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all tags
    cursor.execute("SELECT id, name, category, level, parent_id FROM tag_taxonomy ORDER BY level, name")
    all_tags = cursor.fetchall()
    
    # Build tree structure
    tree = {}
    tag_lookup = {}
    
    for tag in all_tags:
        # Get translations for this tag
        cursor.execute(
            "SELECT language, translation FROM tag_translations WHERE tag_id = ?",
            (tag["id"],)
        )
        translations_rows = cursor.fetchall()
        translations = {t["language"]: t["translation"] for t in translations_rows}
        
        tag_dict = {
            "id": tag["id"],
            "category": tag["category"],
            "translations": translations,
            "children": {}
        }
        tag_lookup[tag["id"]] = tag_dict
        
        if tag["parent_id"] is None:
            # Root level
            tree[tag["name"]] = tag_dict
        else:
            # Child - add to parent's children
            parent = tag_lookup.get(tag["parent_id"])
            if parent:
                parent["children"][tag["name"]] = tag_dict
    
    conn.close()
    return tree


@app.get("/api/tags/{tag_id}")
def get_tag_details(tag_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific tag
    
    Returns:
        {
            id, name, category, level, parent_id,
            translations: {language: translation},
            synonyms: [list],
            children: [list of child tags],
            parent: {parent tag details}
        }
    """
    import sqlite3
    
    conn = sqlite3.connect("./data/portal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get tag
    cursor.execute("SELECT * FROM tag_taxonomy WHERE id = ?", (tag_id,))
    tag_row = cursor.fetchone()
    
    if not tag_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Get translations
    cursor.execute("SELECT language, translation FROM tag_translations WHERE tag_id = ?", (tag_id,))
    translations = {t["language"]: t["translation"] for t in cursor.fetchall()}
    
    # Get synonyms
    cursor.execute("SELECT synonym FROM tag_synonyms WHERE tag_id = ?", (tag_id,))
    synonyms = [s["synonym"] for s in cursor.fetchall()]
    
    # Get children
    cursor.execute("SELECT id, name FROM tag_taxonomy WHERE parent_id = ?", (tag_id,))
    children = [{"id": c["id"], "name": c["name"]} for c in cursor.fetchall()]
    
    # Get parent
    parent = None
    if tag_row["parent_id"]:
        cursor.execute("SELECT id, name FROM tag_taxonomy WHERE id = ?", (tag_row["parent_id"],))
        parent_row = cursor.fetchone()
        if parent_row:
            parent = {"id": parent_row["id"], "name": parent_row["name"]}
    
    result = {
        "id": tag_row["id"],
        "name": tag_row["name"],
        "category": tag_row["category"],
        "level": tag_row["level"],
        "parent_id": tag_row["parent_id"],
        "translations": translations,
        "synonyms": synonyms,
        "children": children,
        "parent": parent
    }
    
    conn.close()
    return result


@app.get("/api/tags/{tag_id}/bhajans")
def get_bhajans_by_tag_id(
    tag_id: int,
    page: int = 1,
    per_page: int = 50,
    db: Session = Depends(get_db)
):
    """Get bhajans tagged with specified tag (includes hierarchical search)
    
    Includes bhajans tagged with this tag AND all descendant tags
    
    Args:
        tag_id: Tag ID
        page: Page number (default 1)
        per_page: Results per page (default 50)
    """
    import sqlite3
    
    conn = sqlite3.connect("./data/portal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all descendant tag IDs (recursive)
    def get_descendant_ids(tid):
        descendants = [tid]
        cursor.execute("SELECT id FROM tag_taxonomy WHERE parent_id = ?", (tid,))
        children = cursor.fetchall()
        for child in children:
            descendants.extend(get_descendant_ids(child["id"]))
        return descendants
    
    tag_ids = get_descendant_ids(tag_id)
    
    # Get bhajans with any of these tags
    placeholders = ",".join("?" * len(tag_ids))
    
    offset = (page - 1) * per_page if page > 0 else 0
    
    query = f"""
        SELECT DISTINCT b.id, b.title, b.lyrics, b.tags, b.uploader_name, 
               b.youtube_url, b.created_at, b.updated_at
        FROM bhajans b
        JOIN bhajan_tags bt ON b.id = bt.bhajan_id
        WHERE bt.tag_id IN ({placeholders})
          AND b.deleted_at IS NULL
        ORDER BY b.created_at DESC
        LIMIT ? OFFSET ?
    """
    
    cursor.execute(query, tag_ids + [per_page, offset])
    bhajans = []
    
    for row in cursor.fetchall():
        bhajans.append({
            "id": row["id"],
            "title": row["title"],
            "lyrics": row["lyrics"],
            "tags": json.loads(row["tags"]) if row["tags"] else [],
            "uploader_name": row["uploader_name"],
            "youtube_url": row["youtube_url"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        })
    
    conn.close()
    return bhajans


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


@app.get("/api/search")
def enhanced_search(q: str, db: Session = Depends(get_db)):
    """Enhanced search across bhajans, tags, translations, and synonyms
    
    Searches in:
    - Bhajan titles
    - Bhajan lyrics
    - Tag names
    - Tag translations (all languages)
    - Tag synonyms
    
    Returns matching bhajans with relevance indication
    
    Args:
        q: Search query
    """
    import sqlite3
    import json as json_lib
    
    if not q or len(q.strip()) < 2:
        return []
    
    query = q.strip()
    
    conn = sqlite3.connect("./data/portal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Track bhajan IDs with match source for relevance
    bhajan_matches = {}  # {bhajan_id: relevance_score}
    
    # 1. Search in bhajan titles (highest relevance = 100)
    search_pattern = f"%{query}%"
    cursor.execute("""
        SELECT id FROM bhajans
        WHERE title LIKE ? AND deleted_at IS NULL
    """, (search_pattern,))
    
    for row in cursor.fetchall():
        bhajan_matches[row["id"]] = max(bhajan_matches.get(row["id"], 0), 100)
    
    # 2. Search in bhajan lyrics (relevance = 80)
    cursor.execute("""
        SELECT id FROM bhajans
        WHERE lyrics LIKE ? AND deleted_at IS NULL
    """, (search_pattern,))
    
    for row in cursor.fetchall():
        bhajan_matches[row["id"]] = max(bhajan_matches.get(row["id"], 0), 80)
    
    # 3. Search in tag names (relevance = 90)
    cursor.execute("""
        SELECT id FROM tag_taxonomy
        WHERE name LIKE ?
    """, (search_pattern,))
    
    tag_ids = [row["id"] for row in cursor.fetchall()]
    
    if tag_ids:
        # Get bhajans with these tags
        placeholders = ",".join("?" * len(tag_ids))
        cursor.execute(f"""
            SELECT DISTINCT bhajan_id FROM bhajan_tags
            WHERE tag_id IN ({placeholders})
        """, tag_ids)
        
        for row in cursor.fetchall():
            bhajan_matches[row["bhajan_id"]] = max(bhajan_matches.get(row["bhajan_id"], 0), 90)
    
    # 4. Search in tag translations (relevance = 85)
    cursor.execute("""
        SELECT tag_id FROM tag_translations
        WHERE translation LIKE ?
    """, (search_pattern,))
    
    tag_ids_trans = [row["tag_id"] for row in cursor.fetchall()]
    
    if tag_ids_trans:
        placeholders = ",".join("?" * len(tag_ids_trans))
        cursor.execute(f"""
            SELECT DISTINCT bhajan_id FROM bhajan_tags
            WHERE tag_id IN ({placeholders})
        """, tag_ids_trans)
        
        for row in cursor.fetchall():
            bhajan_matches[row["bhajan_id"]] = max(bhajan_matches.get(row["bhajan_id"], 0), 85)
    
    # 5. Search in tag synonyms (relevance = 75)
    cursor.execute("""
        SELECT tag_id FROM tag_synonyms
        WHERE synonym LIKE ?
    """, (search_pattern,))
    
    tag_ids_syn = [row["tag_id"] for row in cursor.fetchall()]
    
    if tag_ids_syn:
        placeholders = ",".join("?" * len(tag_ids_syn))
        cursor.execute(f"""
            SELECT DISTINCT bhajan_id FROM bhajan_tags
            WHERE tag_id IN ({placeholders})
        """, tag_ids_syn)
        
        for row in cursor.fetchall():
            bhajan_matches[row["bhajan_id"]] = max(bhajan_matches.get(row["bhajan_id"], 0), 75)
    
    if not bhajan_matches:
        conn.close()
        return []
    
    # Get full bhajan details, sorted by relevance
    sorted_bhajan_ids = sorted(bhajan_matches.keys(), key=lambda x: bhajan_matches[x], reverse=True)
    
    placeholders = ",".join("?" * len(sorted_bhajan_ids))
    cursor.execute(f"""
        SELECT id, title, lyrics, tags, uploader_name, youtube_url, created_at, updated_at
        FROM bhajans
        WHERE id IN ({placeholders})
          AND deleted_at IS NULL
    """, sorted_bhajan_ids)
    
    bhajans = []
    rows_dict = {row["id"]: row for row in cursor.fetchall()}
    
    # Return in relevance order
    for bhajan_id in sorted_bhajan_ids:
        if bhajan_id in rows_dict:
            row = rows_dict[bhajan_id]
            bhajans.append({
                "id": row["id"],
                "title": row["title"],
                "lyrics": row["lyrics"],
                "tags": json_lib.loads(row["tags"]) if row["tags"] else [],
                "uploader_name": row["uploader_name"],
                "youtube_url": row["youtube_url"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "relevance": bhajan_matches[bhajan_id]
            })
    
    conn.close()
    return bhajans


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


@app.post("/api/tags")
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag in the taxonomy"""
    import sqlite3
    
    conn = sqlite3.connect("./data/portal.db")
    cursor = conn.cursor()
    
    try:
        # Check if tag name already exists
        cursor.execute("SELECT id FROM tag_taxonomy WHERE name = ?", (tag.name,))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail=f"Tag '{tag.name}' already exists")
        
        # Determine level based on parent
        level = 0
        if tag.parent_id:
            cursor.execute("SELECT level FROM tag_taxonomy WHERE id = ?", (tag.parent_id,))
            parent_row = cursor.fetchone()
            if not parent_row:
                conn.close()
                raise HTTPException(status_code=404, detail="Parent tag not found")
            level = parent_row[0] + 1
        
        # Insert tag
        cursor.execute(
            """INSERT INTO tag_taxonomy (name, category, parent_id, level, created_at, updated_at)
               VALUES (?, ?, ?, ?, DATETIME('now'), DATETIME('now'))""",
            (tag.name, tag.category, tag.parent_id, level)
        )
        tag_id = cursor.lastrowid
        
        # Insert translations
        for lang, translation in tag.translations.items():
            cursor.execute(
                "INSERT INTO tag_translations (tag_id, language, translation) VALUES (?, ?, ?)",
                (tag_id, lang, translation)
            )
        
        # Insert synonyms
        for synonym in tag.synonyms:
            cursor.execute(
                "INSERT INTO tag_synonyms (tag_id, synonym) VALUES (?, ?)",
                (tag_id, synonym)
            )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created tag: {tag.name} (id={tag_id})")
        return {"id": tag_id, "name": tag.name, "message": "Tag created successfully"}
        
    except HTTPException:
        conn.close()
        raise
    except Exception as e:
        conn.rollback()
        conn.close()
        logger.error(f"Error creating tag: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/tags/{tag_id}")
def update_tag(tag_id: int, tag: TagUpdate, db: Session = Depends(get_db)):
    """Update an existing tag"""
    import sqlite3
    
    conn = sqlite3.connect("./data/portal.db")
    cursor = conn.cursor()
    
    try:
        # Check if tag exists
        cursor.execute("SELECT * FROM tag_taxonomy WHERE id = ?", (tag_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Tag not found")
        
        # Update basic fields
        updates = []
        params = []
        
        if tag.name:
            updates.append("name = ?")
            params.append(tag.name)
        
        if tag.category:
            updates.append("category = ?")
            params.append(tag.category)
        
        if tag.parent_id is not None:
            # Recalculate level
            if tag.parent_id:
                cursor.execute("SELECT level FROM tag_taxonomy WHERE id = ?", (tag.parent_id,))
                parent_row = cursor.fetchone()
                if not parent_row:
                    conn.close()
                    raise HTTPException(status_code=404, detail="Parent tag not found")
                new_level = parent_row[0] + 1
            else:
                new_level = 0
            
            updates.append("parent_id = ?")
            params.append(tag.parent_id)
            updates.append("level = ?")
            params.append(new_level)
        
        if updates:
            updates.append("updated_at = DATETIME('now')")
            params.append(tag_id)
            cursor.execute(
                f"UPDATE tag_taxonomy SET {', '.join(updates)} WHERE id = ?",
                params
            )
        
        # Update translations (replace all)
        if tag.translations is not None:
            cursor.execute("DELETE FROM tag_translations WHERE tag_id = ?", (tag_id,))
            for lang, translation in tag.translations.items():
                cursor.execute(
                    "INSERT INTO tag_translations (tag_id, language, translation) VALUES (?, ?, ?)",
                    (tag_id, lang, translation)
                )
        
        # Update synonyms (replace all)
        if tag.synonyms is not None:
            cursor.execute("DELETE FROM tag_synonyms WHERE tag_id = ?", (tag_id,))
            for synonym in tag.synonyms:
                cursor.execute(
                    "INSERT INTO tag_synonyms (tag_id, synonym) VALUES (?, ?)",
                    (tag_id, synonym)
                )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Updated tag id={tag_id}")
        return {"message": "Tag updated successfully"}
        
    except HTTPException:
        conn.close()
        raise
    except Exception as e:
        conn.rollback()
        conn.close()
        logger.error(f"Error updating tag: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/tags/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Delete a tag (only if not used by any bhajans)"""
    import sqlite3
    
    conn = sqlite3.connect("./data/portal.db")
    cursor = conn.cursor()
    
    try:
        # Check if tag exists
        cursor.execute("SELECT name FROM tag_taxonomy WHERE id = ?", (tag_id,))
        tag_row = cursor.fetchone()
        if not tag_row:
            conn.close()
            raise HTTPException(status_code=404, detail="Tag not found")
        
        tag_name = tag_row[0]
        
        # Check if tag is used by any bhajans
        cursor.execute("SELECT COUNT(*) FROM bhajan_tags WHERE tag_id = ?", (tag_id,))
        usage_count = cursor.fetchone()[0]
        
        if usage_count > 0:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete tag '{tag_name}' - it is used by {usage_count} bhajan(s)"
            )
        
        # Check if tag has children
        cursor.execute("SELECT COUNT(*) FROM tag_taxonomy WHERE parent_id = ?", (tag_id,))
        children_count = cursor.fetchone()[0]
        
        if children_count > 0:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete tag '{tag_name}' - it has {children_count} child tag(s)"
            )
        
        # Delete tag (translations and synonyms cascade automatically)
        cursor.execute("DELETE FROM tag_taxonomy WHERE id = ?", (tag_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted tag: {tag_name} (id={tag_id})")
        return {"message": f"Tag '{tag_name}' deleted successfully"}
        
    except HTTPException:
        conn.close()
        raise
    except Exception as e:
        conn.rollback()
        conn.close()
        logger.error(f"Error deleting tag: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


app.mount("/static", StaticFiles(directory="static"), name="static")


# Admin routes
@app.get("/admin/tags", response_class=FileResponse)
def serve_admin_tags():
    """Serve admin tag management page"""
    template_path = os.path.join("templates", "admin_tags.html")
    logger.info(f"[ADMIN TAGS] Serving from: {template_path}")
    if not os.path.exists(template_path):
        logger.error(f"[ADMIN TAGS] FILE NOT FOUND: {template_path}")
        raise HTTPException(status_code=404, detail="Admin page not found")
    return FileResponse(template_path)


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


@app.get("/api/tags/counts")
def get_tag_counts(db: Session = Depends(get_db)):
    """Get all tags with their usage counts"""
    try:
        bhajans = db.query(Bhajan).all()
        tag_counts = {}
        
        for bhajan in bhajans:
            if bhajan.tags:
                # Parse tags - handle both JSON array strings and comma-separated
                import json
                try:
                    # Try parsing as JSON first
                    tags_list = json.loads(bhajan.tags) if bhajan.tags.startswith('[') else bhajan.tags.split(',')
                except:
                    tags_list = bhajan.tags.split(',')
                
                for tag in tags_list:
                    tag = str(tag).strip().strip('"').strip("'")  # Clean quotes and whitespace
                    if tag and tag not in ['[', ']', '']:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Return sorted by count descending
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"tag": tag, "count": count} for tag, count in sorted_tags]
    
    except Exception as e:
        logger.error(f"Error getting tag counts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
