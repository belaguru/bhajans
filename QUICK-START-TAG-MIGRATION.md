# Quick Start: Tag Migration Guide
**5-Minute Setup Guide for Developers**

## 📋 TL;DR

**Current state:** 68 tags, fragmented and inconsistent  
**Target state:** ~50 canonical tags, hierarchical, multilingual  
**Recommended solution:** Separate taxonomy table (Option C)  
**Timeline:** 2-3 weeks  
**Risk:** Low (backward compatible)

## 🚀 Quick Start (15 minutes)

### Step 1: Review the Analysis (5 min)
```bash
cd ~/Projects/belaguru-bhajans

# Read executive summary
head -100 TAG-ANALYSIS-AND-HIERARCHY-PROPOSAL.md

# View visual hierarchy
cat TAG-HIERARCHY-TREE.txt

# Check deliverables
cat DELIVERABLES-SUMMARY.md
```

### Step 2: Understand the Schema (5 min)
```bash
# Open SQL schema
less tag-taxonomy-schema.sql

# Key tables:
# - tag_taxonomy: Master tag list with hierarchy
# - tag_translations: i18n support (Kannada, Hindi, etc.)
# - tag_synonyms: Search aliases (Anjaneya → Hanuman)
# - bhajan_tags: Many-to-many assignments
```

### Step 3: Run Migration Test (5 min)
```bash
# Create test database
sqlite3 test_tags.db < tag-taxonomy-schema.sql

# Verify tables created
sqlite3 test_tags.db ".tables"
# Should show: bhajan_tags, tag_synonyms, tag_taxonomy, tag_translations

# Check sample data
sqlite3 test_tags.db "SELECT * FROM tag_taxonomy LIMIT 10;"

# Test hierarchy query
sqlite3 test_tags.db "SELECT t.display_name, p.display_name AS parent 
  FROM tag_taxonomy t 
  LEFT JOIN tag_taxonomy p ON t.parent_id = p.id 
  LIMIT 10;"
```

## 📦 What's in the Box?

### 1. Analysis Documents
- **TAG-ANALYSIS-AND-HIERARCHY-PROPOSAL.md** - Full 40KB report
- **TAG-HIERARCHY-TREE.txt** - Visual taxonomy diagram
- **DELIVERABLES-SUMMARY.md** - This summary

### 2. Implementation Files
- **tag-taxonomy-schema.sql** - Complete database schema
- **tag-migration-mapping.csv** - Tag-by-tag migration plan
- **tag-synonyms.csv** - Synonym dictionary

### 3. Data Files
- **tag-frequency-report.csv** - Usage statistics
- **untagged-bhajans.csv** - 110 bhajans needing tags

## 🎯 Migration Checklist

### Pre-Migration
- [ ] Review TAG-ANALYSIS-AND-HIERARCHY-PROPOSAL.md
- [ ] Approve hierarchical structure
- [ ] Set up development environment
- [ ] Backup production database

### Week 1: Foundation
- [ ] Run `tag-taxonomy-schema.sql` on dev database
- [ ] Verify sample data loaded correctly
- [ ] Test hierarchy queries
- [ ] Build tag migration script (Python/SQL)
- [ ] Create rollback script

### Week 2: Migration & API
- [ ] Run migration on staging database
- [ ] Validate counts match old system
- [ ] Build REST API for tags (CRUD, search, filter)
- [ ] Implement dual-write (old JSON + new tables)
- [ ] Integration tests

### Week 3: UI Development
- [ ] Admin tag management UI
- [ ] User tag selector (autocomplete + categories)
- [ ] Filter sidebar with hierarchy
- [ ] Mobile responsive design

### Week 4: Deployment
- [ ] User acceptance testing
- [ ] Production deployment (dual-write enabled)
- [ ] Monitor for 1 week
- [ ] Switch reads to new system
- [ ] Deprecate old JSON field (after 1 month)

## 🔧 Key Implementation Details

### Hierarchy Support
```sql
-- Recursive query to find all child tags
WITH RECURSIVE tag_tree AS (
  SELECT id FROM tag_taxonomy WHERE name = 'vishnu'
  UNION ALL
  SELECT t.id FROM tag_taxonomy t
  JOIN tag_tree tt ON t.parent_id = tt.id
)
SELECT * FROM tag_tree;
```

### Synonym Search
```sql
-- Search "Anjaneya" finds Hanuman bhajans
SELECT DISTINCT b.* FROM bhajans b
JOIN bhajan_tags bt ON bt.bhajan_id = b.id
JOIN tag_synonyms ts ON ts.tag_id = bt.tag_id
WHERE ts.synonym = 'Anjaneya';
```

### Multilingual Display
```sql
-- Get tag in user's language
SELECT 
  t.display_name AS english,
  COALESCE(tr.translated_name, t.display_name) AS localized
FROM tag_taxonomy t
LEFT JOIN tag_translations tr ON tr.tag_id = t.id AND tr.language = 'kn'
WHERE t.name = 'hanuman';
```

## 📊 Migration Data

### Tags to Merge (Top 5)
1. **Hanuman** ← Anjaneya, maruti, Mangala, Vijaya Maruti (85 total)
2. **Narayana** ← Hari naama, vishnu (28 total)
3. **Rama** ← rama, Venkataramana (27 total)
4. **Shiva** ← shiva (20 total)
5. **Saraswati** ← Sharade, Saraswathi (7 total)

### Tags to Delete
- Test (3)
- YouTube (3)
- Audio (1)
- MP3 (1)
- English (1)
- Kannada (1)

### Bhajans to Tag
- 110 untagged bhajans (see `untagged-bhajans.csv`)

## 🧪 Testing Commands

### Test Synonym Resolution
```bash
sqlite3 data/portal.db "
SELECT 
  b.title,
  json_extract(value, '$') as tag
FROM bhajans b, json_each(b.tags)
WHERE json_extract(value, '$') IN ('Anjaneya', 'maruti', 'Hanuman')
LIMIT 5;
"
```

### Count Tags by Category
```bash
sqlite3 test_tags.db "
SELECT category, COUNT(*) as count
FROM tag_taxonomy
WHERE is_active = 1
GROUP BY category;
"
```

### Find Orphaned Tags
```bash
sqlite3 test_tags.db "
SELECT t.display_name, COUNT(bt.id) as usage
FROM tag_taxonomy t
LEFT JOIN bhajan_tags bt ON bt.tag_id = t.id
GROUP BY t.id
HAVING usage = 0;
"
```

## ❓ Common Questions

**Q: Will this break existing APIs?**  
A: No. We'll use dual-write during transition. Old JSON field stays intact until migration is validated.

**Q: How long will migration take?**  
A: 10-15 minutes for database migration, 2-3 weeks for full UI implementation.

**Q: Can users still use old tags during transition?**  
A: Yes. Dual-write means both old and new systems work simultaneously.

**Q: What if we need to rollback?**  
A: Old JSON field is preserved. Just switch reads back to old system.

**Q: How do we handle new tags users want to add?**  
A: Admin approval workflow. Users suggest tags, admin adds to taxonomy.

## 🎓 Learning Resources

### SQL Recursive Queries
- [SQLite WITH RECURSIVE](https://www.sqlite.org/lang_with.html)
- Used for hierarchical tag traversal

### Tag System Design
- [Tag Taxonomies vs Folksonomies](https://en.wikipedia.org/wiki/Taxonomy_(general))
- This project uses controlled taxonomy (admin-defined) vs folksonomy (user-defined)

### Multilingual Database Design
- Translation table pattern (one-to-many)
- Fallback to English if translation missing

## 🆘 Troubleshooting

**Migration fails with foreign key constraint:**
```sql
-- Check if foreign key enforcement is on
PRAGMA foreign_keys;

-- Enable if needed
PRAGMA foreign_keys = ON;
```

**Counts don't match after migration:**
```sql
-- Compare old vs new
SELECT 
  (SELECT COUNT(DISTINCT b.id) FROM bhajans b WHERE b.tags IS NOT NULL) as old_count,
  (SELECT COUNT(DISTINCT bhajan_id) FROM bhajan_tags) as new_count;
```

**Synonym search not working:**
```sql
-- Check synonym mappings
SELECT s.synonym, t.display_name 
FROM tag_synonyms s
JOIN tag_taxonomy t ON s.tag_id = t.id
WHERE s.synonym = 'YOUR_SEARCH_TERM';
```

## 📞 Need Help?

1. Check **TAG-ANALYSIS-AND-HIERARCHY-PROPOSAL.md** (full details)
2. Review **tag-migration-mapping.csv** (tag-by-tag plan)
3. Test with **tag-taxonomy-schema.sql** (runnable schema)
4. Contact main agent for clarifications

---

**Remember:** This is analysis/design only. No implementation done yet. Ready when you are! 🚀
