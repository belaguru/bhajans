-- ============================================================================
-- Belaguru Bhajans Tag Taxonomy Data Population - Migration 002
-- ============================================================================
-- 
-- Populates canonical tag taxonomy with:
-- 1. Root category (Deity)
-- 2. Level 1 deities (Shiva, Vishnu, Devi, Ganesha)
-- 3. Level 2 deities (Hanuman→Shiva, Krishna→Vishnu, Rama→Vishnu)
-- 4. Types (Bhajan, Stotra, Aarti, Chalisa, Kirtan, Mantra)
-- 5. Composers (Purandara Dasa, Tyagaraja, Kanaka Dasa)
-- 6. Languages (Kannada, Hindi, Sanskrit, Telugu, Tamil, English)
-- 7. Occasions (Morning, Evening, Festival, Temple)
-- 8. Translations (Kannada + Hindi for deities)
-- 9. Synonyms (from tag-migration-mapping.csv)
--
-- Based on: data/tag-migration-mapping.csv
-- ============================================================================

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- ============================================================================
-- 1. ROOT CATEGORY
-- ============================================================================

INSERT INTO tag_taxonomy (name, parent_id, category, level) VALUES
('Deity', NULL, 'root', 0);

-- ============================================================================
-- 2. LEVEL 1 DEITIES (Direct children of Deity root)
-- ============================================================================

INSERT INTO tag_taxonomy (name, parent_id, category, level) VALUES
('Shiva', (SELECT id FROM tag_taxonomy WHERE name = 'Deity'), 'deity', 1),
('Vishnu', (SELECT id FROM tag_taxonomy WHERE name = 'Deity'), 'deity', 1),
('Devi', (SELECT id FROM tag_taxonomy WHERE name = 'Deity'), 'deity', 1),
('Ganesha', (SELECT id FROM tag_taxonomy WHERE name = 'Deity'), 'deity', 1);

-- ============================================================================
-- 3. LEVEL 2 DEITIES (Children of Level 1 deities)
-- ============================================================================

-- Hanuman (child of Shiva)
INSERT INTO tag_taxonomy (name, parent_id, category, level) VALUES
('Hanuman', (SELECT id FROM tag_taxonomy WHERE name = 'Shiva'), 'deity', 2);

-- Krishna (child of Vishnu)
INSERT INTO tag_taxonomy (name, parent_id, category, level) VALUES
('Krishna', (SELECT id FROM tag_taxonomy WHERE name = 'Vishnu'), 'deity', 2);

-- Rama (child of Vishnu)
INSERT INTO tag_taxonomy (name, parent_id, category, level) VALUES
('Rama', (SELECT id FROM tag_taxonomy WHERE name = 'Vishnu'), 'deity', 2);

-- ============================================================================
-- 4. TYPES (Bhajan categories)
-- ============================================================================

INSERT INTO tag_taxonomy (name, parent_id, category, level) VALUES
('Bhajan', NULL, 'type', 0),
('Stotra', NULL, 'type', 0),
('Aarti', NULL, 'type', 0),
('Chalisa', NULL, 'type', 0),
('Kirtan', NULL, 'type', 0),
('Mantra', NULL, 'type', 0);

-- ============================================================================
-- 5. COMPOSERS
-- ============================================================================

INSERT INTO tag_taxonomy (name, parent_id, category, level) VALUES
('Purandara Dasa', NULL, 'composer', 0),
('Tyagaraja', NULL, 'composer', 0),
('Kanaka Dasa', NULL, 'composer', 0);

-- ============================================================================
-- 6. LANGUAGES (as theme tags)
-- ============================================================================

INSERT INTO tag_taxonomy (name, parent_id, category, level) VALUES
('Kannada', NULL, 'theme', 0),
('Hindi', NULL, 'theme', 0),
('Sanskrit', NULL, 'theme', 0),
('Telugu', NULL, 'theme', 0),
('Tamil', NULL, 'theme', 0),
('English', NULL, 'theme', 0);

-- ============================================================================
-- 7. OCCASIONS
-- ============================================================================

INSERT INTO tag_taxonomy (name, parent_id, category, level) VALUES
('Morning', NULL, 'occasion', 0),
('Evening', NULL, 'occasion', 0),
('Festival', NULL, 'occasion', 0),
('Temple', NULL, 'occasion', 0);

-- ============================================================================
-- 8. TRANSLATIONS (Kannada + Hindi for deities)
-- ============================================================================

-- Shiva
INSERT INTO tag_translations (tag_id, language, translation) VALUES
((SELECT id FROM tag_taxonomy WHERE name = 'Shiva'), 'kn', 'ಶಿವ'),
((SELECT id FROM tag_taxonomy WHERE name = 'Shiva'), 'hi', 'शिव');

-- Vishnu
INSERT INTO tag_translations (tag_id, language, translation) VALUES
((SELECT id FROM tag_taxonomy WHERE name = 'Vishnu'), 'kn', 'ವಿಷ್ಣು'),
((SELECT id FROM tag_taxonomy WHERE name = 'Vishnu'), 'hi', 'विष्णु');

-- Devi
INSERT INTO tag_translations (tag_id, language, translation) VALUES
((SELECT id FROM tag_taxonomy WHERE name = 'Devi'), 'kn', 'ದೇವಿ'),
((SELECT id FROM tag_taxonomy WHERE name = 'Devi'), 'hi', 'देवी');

-- Ganesha
INSERT INTO tag_translations (tag_id, language, translation) VALUES
((SELECT id FROM tag_taxonomy WHERE name = 'Ganesha'), 'kn', 'ಗಣೇಶ'),
((SELECT id FROM tag_taxonomy WHERE name = 'Ganesha'), 'hi', 'गणेश');

-- Hanuman
INSERT INTO tag_translations (tag_id, language, translation) VALUES
((SELECT id FROM tag_taxonomy WHERE name = 'Hanuman'), 'kn', 'ಹನುಮಾನ್'),
((SELECT id FROM tag_taxonomy WHERE name = 'Hanuman'), 'hi', 'हनुमान');

-- Krishna
INSERT INTO tag_translations (tag_id, language, translation) VALUES
((SELECT id FROM tag_taxonomy WHERE name = 'Krishna'), 'kn', 'ಕೃಷ್ಣ'),
((SELECT id FROM tag_taxonomy WHERE name = 'Krishna'), 'hi', 'कृष्ण');

-- Rama
INSERT INTO tag_translations (tag_id, language, translation) VALUES
((SELECT id FROM tag_taxonomy WHERE name = 'Rama'), 'kn', 'ರಾಮ'),
((SELECT id FROM tag_taxonomy WHERE name = 'Rama'), 'hi', 'राम');

-- ============================================================================
-- 9. SYNONYMS (from tag-migration-mapping.csv)
-- ============================================================================

-- Hanuman synonyms
INSERT INTO tag_synonyms (tag_id, synonym) VALUES
((SELECT id FROM tag_taxonomy WHERE name = 'Hanuman'), 'Anjaneya'),
((SELECT id FROM tag_taxonomy WHERE name = 'Hanuman'), 'maruti'),
((SELECT id FROM tag_taxonomy WHERE name = 'Hanuman'), 'Vijaya Maruti');

-- Case-based synonyms (lowercase variants)
INSERT INTO tag_synonyms (tag_id, synonym) VALUES
((SELECT id FROM tag_taxonomy WHERE name = 'Shiva'), 'shiva'),
((SELECT id FROM tag_taxonomy WHERE name = 'Vishnu'), 'vishnu'),
((SELECT id FROM tag_taxonomy WHERE name = 'Devi'), 'devi'),
((SELECT id FROM tag_taxonomy WHERE name = 'Ganesha'), 'ganesha'),
((SELECT id FROM tag_taxonomy WHERE name = 'Hanuman'), 'hanuman'),
((SELECT id FROM tag_taxonomy WHERE name = 'Krishna'), 'krishna'),
((SELECT id FROM tag_taxonomy WHERE name = 'Rama'), 'rama'),
((SELECT id FROM tag_taxonomy WHERE name = 'Chalisa'), 'chalisa');

-- Additional known synonyms from mapping
INSERT INTO tag_synonyms (tag_id, synonym) VALUES
((SELECT id FROM tag_taxonomy WHERE name = 'Rama'), 'narayana'),
((SELECT id FROM tag_taxonomy WHERE name = 'Vishnu'), 'Narayana');

-- ============================================================================
-- VERIFICATION QUERIES (Run these to validate data)
-- ============================================================================

-- Count tags by category
-- SELECT category, COUNT(*) as count FROM tag_taxonomy GROUP BY category;

-- Show deity hierarchy
-- SELECT 
--     t1.name as child,
--     t1.level,
--     t2.name as parent
-- FROM tag_taxonomy t1
-- LEFT JOIN tag_taxonomy t2 ON t1.parent_id = t2.id
-- WHERE t1.category IN ('deity', 'root')
-- ORDER BY t1.level, t1.name;

-- Show translations for Hanuman
-- SELECT 
--     t.name,
--     tr.language,
--     tr.translation
-- FROM tag_taxonomy t
-- JOIN tag_translations tr ON t.id = tr.tag_id
-- WHERE t.name = 'Hanuman';

-- Show synonyms for Hanuman
-- SELECT 
--     t.name as canonical,
--     s.synonym
-- FROM tag_taxonomy t
-- JOIN tag_synonyms s ON t.id = s.tag_id
-- WHERE t.name = 'Hanuman';

-- ============================================================================
-- ROLLBACK (Run this to undo migration)
-- ============================================================================
-- 
-- DELETE FROM tag_synonyms;
-- DELETE FROM tag_translations;
-- DELETE FROM tag_taxonomy;
-- 
-- ============================================================================
