-- Bhajan Tagging Migration V2 - PRIMARY SUBJECTS ONLY (FIXED)
-- Generated: 2026-03-23 06:36:00
-- Total bhajans: 208
-- Rule: Tag PRIMARY subject only, maximum 3-5 tags
-- FIX: Delete ALL automated tags (AI_ANALYSIS, ai, migration)

BEGIN TRANSACTION;

-- Step 1: Clear ALL previous automated tags (not just 'ai'/'migration')
DELETE FROM bhajan_tags WHERE source IN ('AI_ANALYSIS', 'ai', 'migration', 'auto');

-- Verify clean slate
SELECT 'Tags removed:' as status, changes() as count;

COMMIT;
