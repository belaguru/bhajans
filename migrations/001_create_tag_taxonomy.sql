-- ============================================================================
-- Belaguru Bhajans Tag Taxonomy Schema - Migration 001
-- ============================================================================
-- 
-- Creates hierarchical, multilingual tag system with:
-- - tag_taxonomy: Master tag list with parent-child relationships
-- - tag_translations: Multilingual support (English, Kannada, Hindi, etc.)
-- - tag_synonyms: Search aliases (Anjaneya → Hanuman)
-- - bhajan_tags: Many-to-many bhajan-tag assignments
--
-- Foreign keys enforce referential integrity
-- Indexes optimize common queries
-- ============================================================================

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. TAG TAXONOMY (Master tag list with hierarchy)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tag_taxonomy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,          -- Canonical name (lowercase, no spaces)
    parent_id INTEGER,                          -- For hierarchy (NULL = top-level)
    category VARCHAR(50) NOT NULL,              -- deity, type, composer, day, occasion, theme, root
    level INTEGER NOT NULL DEFAULT 0,           -- Hierarchy depth (0 = root, 1 = child, etc.)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_id) REFERENCES tag_taxonomy(id) ON DELETE SET NULL,
    
    CHECK (category IN ('deity', 'type', 'composer', 'temple', 'guru', 'day', 'occasion', 'theme', 'root'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_tag_category ON tag_taxonomy(category);
CREATE INDEX IF NOT EXISTS idx_tag_parent ON tag_taxonomy(parent_id);
CREATE INDEX IF NOT EXISTS idx_tag_name ON tag_taxonomy(name);
CREATE INDEX IF NOT EXISTS idx_tag_level ON tag_taxonomy(level);

-- ----------------------------------------------------------------------------
-- 2. TAG TRANSLATIONS (i18n support)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tag_translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER NOT NULL,
    language VARCHAR(10) NOT NULL,              -- ISO 639-1: 'en', 'kn', 'hi', 'te', 'ta'
    translation VARCHAR(100) NOT NULL,          -- Translated name (e.g., 'ಹನುಮಾನ್')
    
    FOREIGN KEY (tag_id) REFERENCES tag_taxonomy(id) ON DELETE CASCADE,
    UNIQUE(tag_id, language)
);

-- Indexes for translation lookups
CREATE INDEX IF NOT EXISTS idx_trans_tag ON tag_translations(tag_id);
CREATE INDEX IF NOT EXISTS idx_trans_lang ON tag_translations(language);

-- ----------------------------------------------------------------------------
-- 3. TAG SYNONYMS (Search aliases)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tag_synonyms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER NOT NULL,
    synonym VARCHAR(100) NOT NULL UNIQUE,       -- Search alias (e.g., 'Anjaneya')
    
    FOREIGN KEY (tag_id) REFERENCES tag_taxonomy(id) ON DELETE CASCADE
);

-- Indexes for synonym search
CREATE INDEX IF NOT EXISTS idx_syn_tag ON tag_synonyms(tag_id);
CREATE INDEX IF NOT EXISTS idx_syn_synonym ON tag_synonyms(synonym);

-- ----------------------------------------------------------------------------
-- 4. BHAJAN TAGS (Many-to-many assignments)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bhajan_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bhajan_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    source VARCHAR(50) DEFAULT 'manual',        -- 'manual', 'ai', 'migration', 'auto'
    confidence REAL DEFAULT 1.0,                -- 0.0 to 1.0 (for AI-assigned tags)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (bhajan_id) REFERENCES bhajans(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tag_taxonomy(id) ON DELETE CASCADE,
    
    UNIQUE(bhajan_id, tag_id)                   -- Prevent duplicate assignments
);

-- Indexes for bhajan-tag queries
CREATE INDEX IF NOT EXISTS idx_bhajan_tags_bhajan ON bhajan_tags(bhajan_id);
CREATE INDEX IF NOT EXISTS idx_bhajan_tags_tag ON bhajan_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_bhajan_tags_created ON bhajan_tags(created_at);
CREATE INDEX IF NOT EXISTS idx_bhajan_tags_source ON bhajan_tags(source);

-- ============================================================================
-- ROLLBACK SECTION (Run this to undo migration)
-- ============================================================================
-- 
-- DROP TABLE IF EXISTS bhajan_tags;
-- DROP TABLE IF EXISTS tag_synonyms;
-- DROP TABLE IF EXISTS tag_translations;
-- DROP TABLE IF EXISTS tag_taxonomy;
-- 
-- ============================================================================
