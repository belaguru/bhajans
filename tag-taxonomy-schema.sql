-- ============================================================================
-- Belaguru Bhajans Tag Taxonomy Schema
-- Option C: Separate Taxonomy Table (RECOMMENDED)
-- ============================================================================
-- 
-- This schema implements a hierarchical, multilingual tag system with:
-- - Referential integrity (can't assign non-existent tags)
-- - Synonym support (Anjaneya → Hanuman)
-- - Multilingual translations (English, Kannada, Hindi, etc.)
-- - Hierarchical relationships (Krishna → Vishnu → Deity)
-- - Audit trail (who assigned tags, when)
-- 
-- Migration strategy: Dual-write to both old JSON field and new tables
-- during transition period, then deprecate JSON field after validation.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. TAG TAXONOMY (Master tag list with hierarchy)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tag_taxonomy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,          -- Canonical name (lowercase, ASCII, no spaces)
                                                -- e.g., 'hanuman', 'krishna', 'bhajan'
    display_name VARCHAR(100) NOT NULL,         -- Display name (proper case, for UI)
                                                -- e.g., 'Hanuman', 'Krishna', 'Bhajan'
    category VARCHAR(50) NOT NULL,              -- deity, type, composer, day, occasion, theme
    parent_id INTEGER,                          -- For hierarchy (NULL = top-level)
                                                -- e.g., krishna.parent_id = vishnu.id
    description TEXT,                           -- Optional description for admin UI
    sort_order INTEGER DEFAULT 0,               -- Display order within category
    is_active BOOLEAN DEFAULT 1,                -- Soft delete (0 = hidden, not deleted)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_id) REFERENCES tag_taxonomy(id) ON DELETE SET NULL,
    
    CHECK (category IN ('deity', 'type', 'composer', 'temple', 'guru', 'day', 'occasion', 'theme', 'root'))
);

CREATE INDEX idx_tag_category ON tag_taxonomy(category);
CREATE INDEX idx_tag_parent ON tag_taxonomy(parent_id);
CREATE INDEX idx_tag_name ON tag_taxonomy(name);
CREATE INDEX idx_tag_active ON tag_taxonomy(is_active);

-- ----------------------------------------------------------------------------
-- 2. TAG TRANSLATIONS (i18n support)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tag_translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER NOT NULL,
    language VARCHAR(10) NOT NULL,              -- ISO 639-1: 'en', 'kn', 'hi', 'te', 'ta'
    translated_name VARCHAR(100) NOT NULL,      -- e.g., 'ಹನುಮಾನ್' for Kannada
    
    FOREIGN KEY (tag_id) REFERENCES tag_taxonomy(id) ON DELETE CASCADE,
    UNIQUE(tag_id, language)
);

CREATE INDEX idx_trans_tag ON tag_translations(tag_id);
CREATE INDEX idx_trans_lang ON tag_translations(language);

-- ----------------------------------------------------------------------------
-- 3. TAG SYNONYMS (Search aliases)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tag_synonyms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER NOT NULL,
    synonym VARCHAR(100) NOT NULL UNIQUE,       -- e.g., 'Anjaneya' → hanuman
                                                -- Case-insensitive search should normalize
    language VARCHAR(10) DEFAULT 'en',          -- Language of synonym (for display)
    
    FOREIGN KEY (tag_id) REFERENCES tag_taxonomy(id) ON DELETE CASCADE
);

CREATE INDEX idx_syn_tag ON tag_synonyms(tag_id);
CREATE INDEX idx_syn_synonym ON tag_synonyms(synonym);

-- ----------------------------------------------------------------------------
-- 4. BHAJAN TAGS (Many-to-many assignments)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bhajan_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bhajan_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    assigned_by VARCHAR(100) DEFAULT 'system',  -- Username or 'system' for migration
    
    FOREIGN KEY (bhajan_id) REFERENCES bhajans(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tag_taxonomy(id) ON DELETE CASCADE,
    
    UNIQUE(bhajan_id, tag_id)                   -- Prevent duplicate assignments
);

CREATE INDEX idx_bhajan_tags_bhajan ON bhajan_tags(bhajan_id);
CREATE INDEX idx_bhajan_tags_tag ON bhajan_tags(tag_id);
CREATE INDEX idx_bhajan_tags_assigned ON bhajan_tags(assigned_at);

-- ----------------------------------------------------------------------------
-- 5. SAMPLE DATA (Seed with core tags)
-- ----------------------------------------------------------------------------

-- Root categories (for hierarchy)
INSERT INTO tag_taxonomy (id, name, display_name, category, parent_id) VALUES
  (1, 'deity', 'Deity', 'root', NULL),
  (2, 'type', 'Type', 'root', NULL),
  (3, 'composer', 'Composer', 'root', NULL),
  (4, 'day', 'Day of Week', 'root', NULL),
  (5, 'occasion', 'Occasion', 'root', NULL);

-- Deities (primary)
INSERT INTO tag_taxonomy (name, display_name, category, parent_id, sort_order) VALUES
  ('vishnu', 'Vishnu', 'deity', 1, 1),
  ('shiva', 'Shiva', 'deity', 1, 2),
  ('devi', 'Devi', 'deity', 1, 3),
  ('ganesha', 'Ganesha', 'deity', 1, 4),
  ('hanuman', 'Hanuman', 'deity', 1, 5),
  ('dattatreya', 'Dattatreya', 'deity', 1, 6),
  ('ayyappa', 'Ayyappa', 'deity', 1, 7);

-- Vishnu avatars (sub-deities)
INSERT INTO tag_taxonomy (name, display_name, category, parent_id, sort_order) VALUES
  ('narayana', 'Narayana', 'deity', (SELECT id FROM tag_taxonomy WHERE name = 'vishnu'), 1),
  ('rama', 'Rama', 'deity', (SELECT id FROM tag_taxonomy WHERE name = 'vishnu'), 2),
  ('krishna', 'Krishna', 'deity', (SELECT id FROM tag_taxonomy WHERE name = 'vishnu'), 3),
  ('venkataramana', 'Venkataramana', 'deity', (SELECT id FROM tag_taxonomy WHERE name = 'vishnu'), 4);

-- Devi forms (sub-deities)
INSERT INTO tag_taxonomy (name, display_name, category, parent_id, sort_order) VALUES
  ('saraswati', 'Saraswati', 'deity', (SELECT id FROM tag_taxonomy WHERE name = 'devi'), 1),
  ('lakshmi', 'Lakshmi', 'deity', (SELECT id FROM tag_taxonomy WHERE name = 'devi'), 2),
  ('durga', 'Durga', 'deity', (SELECT id FROM tag_taxonomy WHERE name = 'devi'), 3),
  ('rajeshwari', 'Rajeshwari', 'deity', (SELECT id FROM tag_taxonomy WHERE name = 'devi'), 4);

-- Types
INSERT INTO tag_taxonomy (name, display_name, category, parent_id, sort_order) VALUES
  ('bhajan', 'Bhajan', 'type', 2, 1),
  ('mantra', 'Mantra', 'type', 2, 2),
  ('chant', 'Chant', 'type', 2, 3),
  ('stotra', 'Stotra', 'type', 2, 4),
  ('chalisa', 'Chalisa', 'type', 2, 5),
  ('dandakam', 'Dandakam', 'type', 2, 6),
  ('ashtotharam', 'Ashtotharam', 'type', 2, 7),
  ('janapada', 'Janapada', 'type', 2, 8),
  ('kirtan', 'Kirtan', 'type', 2, 9),
  ('aarti', 'Aarti', 'type', 2, 10);

-- Composers
INSERT INTO tag_taxonomy (name, display_name, category, parent_id, sort_order) VALUES
  ('purandara', 'Purandara Dasa', 'composer', 3, 1),
  ('tatva_pada', 'Tatva Pada', 'composer', 3, 2),
  ('shishunaala_sharifa', 'Shishunaala Sharifa', 'composer', 3, 3);

-- Temple/Guru
INSERT INTO tag_taxonomy (name, display_name, category, parent_id, sort_order) VALUES
  ('belaguru', 'Belaguru', 'temple', NULL, 1),
  ('bindu_madhava', 'Bindu Madhava', 'temple', NULL, 2),
  ('guru_stuti', 'Guru Stuti', 'guru', NULL, 1);

-- Days of week
INSERT INTO tag_taxonomy (name, display_name, category, parent_id, sort_order) VALUES
  ('sunday', 'Sunday', 'day', 4, 1),
  ('monday', 'Monday', 'day', 4, 2),
  ('tuesday', 'Tuesday', 'day', 4, 3),
  ('wednesday', 'Wednesday', 'day', 4, 4),
  ('thursday', 'Thursday', 'day', 4, 5),
  ('friday', 'Friday', 'day', 4, 6),
  ('saturday', 'Saturday', 'day', 4, 7);

-- Occasions
INSERT INTO tag_taxonomy (name, display_name, category, parent_id, sort_order) VALUES
  ('yugadi', 'Yugadi', 'occasion', 5, 1),
  ('deepavali', 'Deepavali', 'occasion', 5, 2),
  ('navaratri', 'Navaratri', 'occasion', 5, 3),
  ('shivaratri', 'Shivaratri', 'occasion', 5, 4);

-- ----------------------------------------------------------------------------
-- 6. TRANSLATIONS (Sample)
-- ----------------------------------------------------------------------------

-- Hanuman translations
INSERT INTO tag_translations (tag_id, language, translated_name) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'hanuman'), 'kn', 'ಹನುಮಾನ್'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'hanuman'), 'hi', 'हनुमान'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'hanuman'), 'te', 'హనుమాన్'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'hanuman'), 'ta', 'ஹனுமான்');

-- Rama translations
INSERT INTO tag_translations (tag_id, language, translated_name) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'rama'), 'kn', 'ರಾಮ'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'rama'), 'hi', 'राम'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'rama'), 'te', 'రామ'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'rama'), 'ta', 'ராமர்');

-- Krishna translations
INSERT INTO tag_translations (tag_id, language, translated_name) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'krishna'), 'kn', 'ಕೃಷ್ಣ'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'krishna'), 'hi', 'कृष्ण'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'krishna'), 'te', 'కృష్ణ'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'krishna'), 'ta', 'கிருஷ்ணர்');

-- Shiva translations
INSERT INTO tag_translations (tag_id, language, translated_name) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'shiva'), 'kn', 'ಶಿವ'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'shiva'), 'hi', 'शिव'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'shiva'), 'te', 'శివ'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'shiva'), 'ta', 'சிவன்');

-- Ganesha translations
INSERT INTO tag_translations (tag_id, language, translated_name) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'ganesha'), 'kn', 'ಗಣೇಶ'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'ganesha'), 'hi', 'गणेश'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'ganesha'), 'te', 'గణేష'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'ganesha'), 'ta', 'விநாயகர்');

-- Type translations
INSERT INTO tag_translations (tag_id, language, translated_name) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'bhajan'), 'kn', 'ಭಜನೆ'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'bhajan'), 'hi', 'भजन'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'mantra'), 'kn', 'ಮಂತ್ರ'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'mantra'), 'hi', 'मंत्र');

-- ----------------------------------------------------------------------------
-- 7. SYNONYMS (For search flexibility)
-- ----------------------------------------------------------------------------

-- Hanuman synonyms
INSERT INTO tag_synonyms (tag_id, synonym, language) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'hanuman'), 'Anjaneya', 'en'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'hanuman'), 'maruti', 'en'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'hanuman'), 'Mangala', 'en'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'hanuman'), 'Vijaya Maruti', 'en'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'hanuman'), 'ಆಂಜನೇಯ', 'kn');

-- Narayana synonyms
INSERT INTO tag_synonyms (tag_id, synonym, language) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'narayana'), 'Hari naama', 'en');

-- Krishna synonyms
INSERT INTO tag_synonyms (tag_id, synonym, language) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'krishna'), 'Radhe', 'en');

-- Saraswati synonyms
INSERT INTO tag_synonyms (tag_id, synonym, language) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'saraswati'), 'Sharade', 'en'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'saraswati'), 'Saraswathi', 'en');

-- Bhajan synonyms
INSERT INTO tag_synonyms (tag_id, synonym, language) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'bhajan'), 'Daily Bhajan', 'en'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'bhajan'), 'devotional', 'en'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'bhajan'), 'Devotional', 'en');

-- Chalisa synonyms
INSERT INTO tag_synonyms (tag_id, synonym, language) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'chalisa'), 'ಲೀಸಾ', 'kn'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'chalisa'), 'ಹನುಮಾನ್ಚಾಲೀಸಾ', 'kn');

-- Dandakam synonyms
INSERT INTO tag_synonyms (tag_id, synonym, language) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'dandakam'), 'ದಂಡಕಂ', 'kn');

-- Guru Stuti synonyms
INSERT INTO tag_synonyms (tag_id, synonym, language) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'guru_stuti'), 'gurustuti', 'en'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'guru_stuti'), 'Sadguru', 'en'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'guru_stuti'), 'sadguru', 'en');

-- Monday synonyms
INSERT INTO tag_synonyms (tag_id, synonym, language) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'monday'), 'Monday Bhajans', 'en'),
  ((SELECT id FROM tag_taxonomy WHERE name = 'monday'), 'ಸೋಮವಾರದ ಭಜನೆಗಳು', 'kn');

-- Friday synonyms
INSERT INTO tag_synonyms (tag_id, synonym, language) VALUES
  ((SELECT id FROM tag_taxonomy WHERE name = 'friday'), 'Friday Bhajans', 'en');

-- ----------------------------------------------------------------------------
-- 8. USEFUL VIEWS (For easier querying)
-- ----------------------------------------------------------------------------

-- View: Tags with all synonyms and translations
CREATE VIEW IF NOT EXISTS v_tag_complete AS
SELECT 
    t.id,
    t.name AS canonical,
    t.display_name,
    t.category,
    p.display_name AS parent_name,
    GROUP_CONCAT(DISTINCT s.synonym) AS synonyms,
    GROUP_CONCAT(DISTINCT tr.language || ':' || tr.translated_name) AS translations,
    (SELECT COUNT(*) FROM bhajan_tags bt WHERE bt.tag_id = t.id) AS usage_count
FROM tag_taxonomy t
LEFT JOIN tag_taxonomy p ON t.parent_id = p.id
LEFT JOIN tag_synonyms s ON s.tag_id = t.id
LEFT JOIN tag_translations tr ON tr.tag_id = t.id
WHERE t.is_active = 1
GROUP BY t.id;

-- View: Bhajan tags with full hierarchy
CREATE VIEW IF NOT EXISTS v_bhajan_tags_full AS
SELECT 
    bt.bhajan_id,
    b.title AS bhajan_title,
    t.name AS tag_canonical,
    t.display_name AS tag_display,
    t.category,
    p.display_name AS parent_tag,
    bt.assigned_at,
    bt.assigned_by
FROM bhajan_tags bt
JOIN bhajans b ON bt.bhajan_id = b.id
JOIN tag_taxonomy t ON bt.tag_id = t.id
LEFT JOIN tag_taxonomy p ON t.parent_id = p.id
WHERE t.is_active = 1;

-- ----------------------------------------------------------------------------
-- 9. SAMPLE QUERIES (For reference)
-- ----------------------------------------------------------------------------

-- Find all Vishnu-related bhajans (includes Krishna, Rama, Narayana via hierarchy)
-- WITH RECURSIVE deity_tree AS (
--   SELECT id FROM tag_taxonomy WHERE name = 'vishnu'
--   UNION ALL
--   SELECT t.id 
--   FROM tag_taxonomy t
--   JOIN deity_tree dt ON t.parent_id = dt.id
-- )
-- SELECT DISTINCT b.*
-- FROM bhajans b
-- JOIN bhajan_tags bt ON bt.bhajan_id = b.id
-- WHERE bt.tag_id IN (SELECT id FROM deity_tree);

-- Search by synonym (e.g., user searches "Anjaneya")
-- SELECT DISTINCT b.*
-- FROM bhajans b
-- JOIN bhajan_tags bt ON bt.bhajan_id = b.id
-- JOIN tag_synonyms ts ON ts.tag_id = bt.tag_id
-- WHERE ts.synonym = 'Anjaneya';

-- Get all tags for a bhajan
-- SELECT t.display_name, t.category
-- FROM bhajan_tags bt
-- JOIN tag_taxonomy t ON bt.tag_id = t.id
-- WHERE bt.bhajan_id = 1;

-- Tag usage statistics
-- SELECT 
--   t.category,
--   t.display_name,
--   COUNT(bt.id) AS usage_count
-- FROM tag_taxonomy t
-- LEFT JOIN bhajan_tags bt ON bt.tag_id = t.id
-- WHERE t.is_active = 1
-- GROUP BY t.category, t.display_name
-- ORDER BY t.category, usage_count DESC;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
