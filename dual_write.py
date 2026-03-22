"""
Dual-Write Strategy for Tags

When bhajans are created/updated, write tags to BOTH:
1. Old JSON field (bhajans.tags column) - for backward compatibility
2. New bhajan_tags table - for hierarchical taxonomy

Feature flag: USE_TAG_TAXONOMY environment variable
- When "true": Write to both systems
- When "false": Only write to JSON field (old behavior)
"""
import os
import json
from typing import List, Union
from sqlalchemy.orm import Session
from sqlalchemy import text

def _use_tag_taxonomy() -> bool:
    """Check feature flag - allows dynamic testing"""
    return os.environ.get("USE_TAG_TAXONOMY", "true").lower() == "true"

# Convenience global (but always call function for tests)
USE_TAG_TAXONOMY = _use_tag_taxonomy()


def get_tag_id_by_name(session: Session, tag_name: str) -> int | None:
    """
    Look up tag_id from tag_taxonomy by name.
    
    Args:
        session: Database session
        tag_name: Tag name (e.g., 'hanuman', 'bhajan')
    
    Returns:
        tag_id if found, None otherwise
    """
    result = session.execute(
        text("SELECT id FROM tag_taxonomy WHERE name = :name"),
        {"name": tag_name.lower().strip()}
    )
    row = result.first()
    return row[0] if row else None


def get_tag_name_by_id(session: Session, tag_id: int) -> str | None:
    """
    Look up tag name from tag_taxonomy by id.
    
    Args:
        session: Database session
        tag_id: Tag ID
    
    Returns:
        tag name if found, None otherwise
    """
    result = session.execute(
        text("SELECT name FROM tag_taxonomy WHERE id = :id"),
        {"id": tag_id}
    )
    row = result.first()
    return row[0] if row else None


def dual_write_tags(
    session: Session,
    bhajan_id: int,
    tags: List[Union[str, int]],
    source: str = "manual",
    confidence: float = 1.0
):
    """
    Write tags to BOTH old JSON field AND new bhajan_tags table.
    
    This ensures backward compatibility during migration period.
    
    Args:
        session: Database session
        bhajan_id: Bhajan ID
        tags: List of tag names (strings) OR tag_ids (integers)
        source: Tag source ('manual', 'ai', 'migration', 'auto')
        confidence: Confidence score for AI-assigned tags (0.0-1.0)
    
    Logic:
        1. Clear existing bhajan_tags entries (for updates)
        2. For each tag:
           - If string: look up tag_id, insert into bhajan_tags
           - If int: insert into bhajan_tags, convert to name for JSON
        3. Save all tag names to bhajans.tags JSON field
    """
    from models import Bhajan
    
    # Get bhajan instance
    bhajan = session.query(Bhajan).filter(Bhajan.id == bhajan_id).first()
    if not bhajan:
        raise ValueError(f"Bhajan {bhajan_id} not found")
    
    # Separate strings and integers
    tag_names = []
    tag_ids = []
    
    for tag in tags:
        if isinstance(tag, str):
            tag_name = tag.lower().strip()
            tag_names.append(tag_name)
            
            # Look up tag_id if taxonomy enabled
            if _use_tag_taxonomy():
                tag_id = get_tag_id_by_name(session, tag_name)
                if tag_id:
                    tag_ids.append(tag_id)
        
        elif isinstance(tag, int):
            tag_ids.append(tag)
            
            # Convert to name for JSON
            tag_name = get_tag_name_by_id(session, tag)
            if tag_name:
                tag_names.append(tag_name)
    
    # Write to old JSON field (always, for backward compat)
    bhajan.set_tags(tag_names)
    
    # Write to new taxonomy table (if feature enabled)
    if _use_tag_taxonomy() and tag_ids:
        # Clear existing tags for this bhajan (for updates)
        session.execute(
            text("DELETE FROM bhajan_tags WHERE bhajan_id = :bid"),
            {"bid": bhajan_id}
        )
        
        # Insert new tags
        for tag_id in tag_ids:
            session.execute(
                text("""
                    INSERT OR IGNORE INTO bhajan_tags 
                    (bhajan_id, tag_id, source, confidence)
                    VALUES (:bhajan_id, :tag_id, :source, :confidence)
                """),
                {
                    "bhajan_id": bhajan_id,
                    "tag_id": tag_id,
                    "source": source,
                    "confidence": confidence
                }
            )
    
    session.commit()


def read_bhajan_tags(session: Session, bhajan_id: int) -> List[str]:
    """
    Read tags for a bhajan.
    
    Preference order:
    1. If bhajan_tags table has entries → return those (convert to names)
    2. Otherwise fallback to JSON field
    
    Args:
        session: Database session
        bhajan_id: Bhajan ID
    
    Returns:
        List of tag names
    """
    from models import Bhajan
    
    # Try reading from taxonomy table first
    if _use_tag_taxonomy():
        result = session.execute(
            text("""
                SELECT t.name 
                FROM bhajan_tags bt
                JOIN tag_taxonomy t ON bt.tag_id = t.id
                WHERE bt.bhajan_id = :bid
                ORDER BY t.name
            """),
            {"bid": bhajan_id}
        )
        tags = [row[0] for row in result]
        
        if tags:
            return tags
    
    # Fallback to JSON field
    bhajan = session.query(Bhajan).filter(Bhajan.id == bhajan_id).first()
    if bhajan:
        return bhajan.get_tags()
    
    return []


def get_bhajan_with_unified_tags(session: Session, bhajan_id: int) -> dict | None:
    """
    Get bhajan with tags from preferred source.
    
    Returns bhajan dict with unified tags field.
    
    Args:
        session: Database session
        bhajan_id: Bhajan ID
    
    Returns:
        Bhajan dict with tags, or None if not found
    """
    from models import Bhajan
    
    bhajan = session.query(Bhajan).filter(Bhajan.id == bhajan_id).first()
    if not bhajan:
        return None
    
    # Get unified tags
    tags = read_bhajan_tags(session, bhajan_id)
    
    # Convert to dict and override tags
    bhajan_dict = bhajan.to_dict()
    bhajan_dict["tags"] = tags
    
    return bhajan_dict
