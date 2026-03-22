# Tag Hierarchy Implementation Plan
**Project:** Belaguru Bhajans - Separate Taxonomy Table  
**Branch:** feature/tag-hierarchy  
**Environment:** STAGING ONLY (~/Projects/belaguru-bhajans)  
**Start Date:** March 22, 2026  
**Estimated Duration:** 2-3 weeks (100 hours)

---

## 🎯 **Project Goals**

1. ✅ Implement hierarchical tag system with taxonomy table
2. ✅ Auto-tag 110 untagged bhajans using AI/heuristics
3. ✅ Migrate existing 380 tag instances to new system
4. ✅ Support multilingual search (Kannada, Hindi, English)
5. ✅ Maintain backward compatibility (no breaking changes)
6. ✅ **NEVER touch production** (all work on staging)

---

## 📋 **Complete Task List**

### **Phase 1: Database Schema (Week 1, Days 1-2)**

#### Task 1.1: Create Taxonomy Tables
- [ ] Write SQL migration script (`migrations/001_create_tag_taxonomy.sql`)
- [ ] Create tables:
  - [ ] `tag_taxonomy` (id, name, parent_id, category, level)
  - [ ] `tag_translations` (id, tag_id, language, translation)
  - [ ] `tag_synonyms` (id, tag_id, synonym)
  - [ ] `bhajan_tags` (id, bhajan_id, tag_id, source, confidence)
- [ ] Add indexes for performance
- [ ] Test on staging database

**Deliverable:** Working database schema  
**Time:** 8 hours

---

#### Task 1.2: Populate Core Taxonomy
- [ ] Insert canonical tags (50 core tags)
- [ ] Define hierarchies:
  - [ ] Deities (Shiva → Hanuman, Vishnu → Krishna/Rama)
  - [ ] Types (Bhajan, Stotra, Aarti, Chalisa)
  - [ ] Composers (Purandara Dasa, Tyagaraja)
  - [ ] Temple (Belaguru specific)
  - [ ] Time (Morning, Evening, Festival)
- [ ] Add translations (Kannada, Hindi, Telugu, Tamil)
- [ ] Add synonyms (Anjaneya → Hanuman, Hari → Vishnu)

**Deliverable:** Populated taxonomy with 50 canonical tags  
**Time:** 6 hours

---

### **Phase 2: Migration Scripts (Week 1, Days 3-4)**

#### Task 2.1: Tag Cleanup Mapping
- [ ] Analyze existing 68 tags
- [ ] Create mapping CSV:
  - [ ] Old tag → New canonical tag
  - [ ] Case fixes (Rama → rama becomes "Rama")
  - [ ] Merge duplicates (9 groups)
  - [ ] Remove meta tags (Test, YouTube, Audio, MP3)
- [ ] Generate migration SQL

**Deliverable:** `tag-migration-mapping.csv` + SQL script  
**Time:** 4 hours

---

#### Task 2.2: Data Migration Script
- [ ] Write Python script (`scripts/migrate_tags.py`)
- [ ] Steps:
  1. Parse existing `tags` JSON field
  2. Map to canonical tags (using CSV)
  3. Insert into `bhajan_tags` table
  4. Mark source as 'MIGRATED'
  5. Keep original `tags` field intact (backward compat)
- [ ] Add rollback capability
- [ ] Dry-run mode for testing

**Deliverable:** Migration script with dry-run  
**Time:** 8 hours

---

### **Phase 3: Auto-Tagging System (Week 1-2, Days 5-7)**

#### Task 3.1: Build Auto-Tagger
- [ ] Create `scripts/auto_tag.py`
- [ ] Implement tagging strategies:

**Strategy 1: Title/Lyrics Analysis**
```python
# Deity detection
if "hanuman" in title.lower() or "anjaneya" in lyrics.lower():
    add_tag("Hanuman", source="AUTO_DEITY", confidence=0.9)

# Type detection  
if "chalisa" in title.lower():
    add_tag("Chalisa", source="AUTO_TYPE", confidence=0.95)

# Language detection
if contains_kannada(lyrics):
    add_tag("Kannada", source="AUTO_LANG", confidence=1.0)
```

**Strategy 2: Uploader Pattern**
```python
# JAG uploads tend to be specific types
if uploader == "JAG":
    check_jag_patterns()
```

**Strategy 3: Existing Tags Pattern**
```python
# If bhajan has "Krishna", add "Vishnu" (parent)
if has_tag("Krishna"):
    add_tag("Vishnu", source="AUTO_HIERARCHY", confidence=0.8)
```

- [ ] Confidence scoring (0.0 - 1.0)
- [ ] Manual review queue (confidence < 0.7)

**Deliverable:** Auto-tagging script  
**Time:** 12 hours

---

#### Task 3.2: Tag Untagged Bhajans
- [ ] Run auto-tagger on 110 untagged bhajans
- [ ] Generate review report:
  ```
  High confidence (>0.8): Auto-apply
  Medium (0.5-0.8): Suggest for review
  Low (<0.5): Flag for manual tagging
  ```
- [ ] Manual review session (spot-check)
- [ ] Apply approved tags

**Deliverable:** All bhajans have at least 2-3 tags  
**Time:** 6 hours

---

### **Phase 4: Backend API (Week 2, Days 8-10)**

#### Task 4.1: Update Models
- [ ] Add SQLAlchemy models:
  - [ ] `TagTaxonomy` model
  - [ ] `TagTranslation` model
  - [ ] `TagSynonym` model
  - [ ] `BhajanTag` model (many-to-many)
- [ ] Update `Bhajan` model:
  - [ ] Add relationship: `bhajan.taxonomy_tags`
  - [ ] Keep `tags` field (backward compat)
- [ ] Write unit tests for models

**Deliverable:** ORM models with tests  
**Time:** 6 hours

---

#### Task 4.2: Tag API Endpoints
- [ ] `GET /api/tags` - List all canonical tags
- [ ] `GET /api/tags/tree` - Hierarchical tree structure
- [ ] `GET /api/tags/{id}/children` - Get child tags
- [ ] `GET /api/tags/{id}/synonyms` - Get synonyms
- [ ] `GET /api/bhajans?tag={id}` - Filter by tag (include children)
- [ ] `GET /api/bhajans?search={query}` - Search with synonym matching
- [ ] Write API tests

**Deliverable:** Tag API with tests  
**Time:** 8 hours

---

#### Task 4.3: Dual-Write Strategy
- [ ] When bhajan is created/updated:
  1. Write to new `bhajan_tags` table
  2. Also write to old `tags` JSON field (compatibility)
- [ ] When reading:
  1. Prefer `bhajan_tags` table
  2. Fallback to `tags` JSON if empty
- [ ] Add feature flag: `USE_TAG_TAXONOMY=true`

**Deliverable:** Backward-compatible tag writes  
**Time:** 4 hours

---

### **Phase 5: Frontend UI (Week 2-3, Days 11-14)**

#### Task 5.1: Tag Selector Component
- [ ] Build hierarchical tag selector UI:
  ```
  Deities ▼
    ├─ Shiva ▼
    │   └─ Hanuman
    ├─ Vishnu ▼
    │   ├─ Krishna
    │   └─ Rama
  Types ▼
    ├─ Bhajan
    ├─ Stotra
  ```
- [ ] Multi-select with checkboxes
- [ ] Show translations (e.g., "Hanuman (ಹನುಮಾನ್)")
- [ ] Auto-suggest synonyms
- [ ] Update upload form
- [ ] Update edit form

**Deliverable:** Tag selector UI component  
**Time:** 10 hours

---

#### Task 5.2: Search/Filter UI
- [ ] Update search to use taxonomy:
  - [ ] "Vishnu" → shows Krishna + Rama bhajans
  - [ ] "Anjaneya" → finds Hanuman bhajans (synonym)
- [ ] Tag cloud/filter sidebar:
  - [ ] Show popular tags
  - [ ] Click to filter
  - [ ] Multi-tag filter (AND/OR)
- [ ] Breadcrumbs (Deity > Vishnu > Krishna)

**Deliverable:** Enhanced search/filter UI  
**Time:** 8 hours

---

#### Task 5.3: Admin Tag Management
- [ ] Admin page `/admin/tags`:
  - [ ] View tag tree
  - [ ] Add/edit/delete tags
  - [ ] Edit translations
  - [ ] Manage synonyms
  - [ ] Merge duplicate tags
  - [ ] Bulk tag operations
- [ ] Tag usage statistics
- [ ] Orphaned tags report

**Deliverable:** Admin tag management UI  
**Time:** 10 hours

---

### **Phase 6: Testing & Deployment (Week 3, Days 15-18)**

#### Task 6.1: Integration Testing
- [ ] Test migration on staging:
  1. Backup database
  2. Run migration
  3. Verify all tags migrated
  4. Test API endpoints
  5. Test frontend UI
- [ ] Test auto-tagging:
  - [ ] Accuracy check (sample 20 bhajans)
  - [ ] Edge cases (no tags, mixed language)
- [ ] Test search:
  - [ ] Hierarchical search (Vishnu → Krishna)
  - [ ] Synonym search (Anjaneya → Hanuman)
  - [ ] Multilingual (search in Kannada)

**Deliverable:** Passing test suite  
**Time:** 8 hours

---

#### Task 6.2: Performance Testing
- [ ] Query performance:
  - [ ] Tag filter with 1000 bhajans
  - [ ] Hierarchical search
  - [ ] Synonym matching
- [ ] Add database indexes if needed
- [ ] Cache tag tree (Redis?)
- [ ] Optimize API response times

**Deliverable:** Performance benchmarks  
**Time:** 4 hours

---

#### Task 6.3: Documentation
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Admin guide (how to manage tags)
- [ ] User guide (how to search by tags)
- [ ] Migration runbook
- [ ] Rollback procedure

**Deliverable:** Complete documentation  
**Time:** 4 hours

---

#### Task 6.4: User Acceptance Testing
- [ ] Deploy to staging (qa.bhajans.s365.in)
- [ ] Create test scenarios document
- [ ] User testing session:
  - [ ] Search by deity (find all Krishna bhajans)
  - [ ] Search by type (find all Stotras)
  - [ ] Upload new bhajan with tags
  - [ ] Admin: Add new tag
- [ ] Collect feedback
- [ ] Fix issues

**Deliverable:** UAT approval  
**Time:** 6 hours

---

### **Phase 7: Production Deployment (Week 3-4, Day 19-20)**

#### Task 7.1: Pre-Deployment Checklist
- [ ] **STAGING VERIFICATION:**
  - [ ] All tests passing
  - [ ] Database migration successful
  - [ ] API working correctly
  - [ ] UI functional
  - [ ] Auto-tagging accurate
  - [ ] Performance acceptable
- [ ] **PRODUCTION PREPARATION:**
  - [ ] Backup production database
  - [ ] Schedule maintenance window
  - [ ] Prepare rollback plan
  - [ ] Alert team

**Deliverable:** Ready for production  
**Time:** 2 hours

---

#### Task 7.2: Production Deployment
- [ ] **STOP!** Get explicit approval from Kashi
- [ ] Deploy to production:
  1. Backup database
  2. Run migration script
  3. Deploy new code
  4. Restart services
  5. Smoke test
- [ ] Monitor for 24 hours:
  - [ ] Error logs
  - [ ] Query performance
  - [ ] User feedback
- [ ] Rollback if issues

**Deliverable:** Feature live on production  
**Time:** 4 hours + monitoring

---

## 📊 **Time Breakdown**

| Phase | Tasks | Hours |
|-------|-------|-------|
| Phase 1: Database Schema | 2 | 14 |
| Phase 2: Migration Scripts | 2 | 12 |
| Phase 3: Auto-Tagging | 2 | 18 |
| Phase 4: Backend API | 3 | 18 |
| Phase 5: Frontend UI | 3 | 28 |
| Phase 6: Testing | 4 | 22 |
| Phase 7: Deployment | 2 | 6 |
| **Total** | **18 tasks** | **118 hours** |

**Timeline:** 3 weeks (with buffer)

---

## 🔄 **Migration Strategy**

### Backward Compatibility
```
Old System (Current):
  bhajans.tags = ["Krishna", "Bhajan"]  # JSON array

New System (After):
  bhajans.tags = ["Krishna", "Bhajan"]  # Still works!
  bhajan_tags.tags = [
    {id: 5, name: "Krishna", category: "Deity", parent: "Vishnu"},
    {id: 12, name: "Bhajan", category: "Type"}
  ]  # Rich taxonomy
```

### Dual-Write Period
- **Week 1-2:** New system writes to both old + new tables
- **Week 3:** Monitor production, verify data consistency
- **Week 4+:** Remove old `tags` field (separate PR)

---

## 🚨 **Safety Rules**

### Environment Discipline
```bash
# ✅ ALWAYS work in staging
cd ~/Projects/belaguru-bhajans  # Staging
sqlite3 data/portal.db           # Staging DB

# ❌ NEVER touch production
ssh kreddy@34.93.110.163         # Production server - FORBIDDEN
```

### Verification Checklist
Before EVERY database change:
```bash
# 1. Verify environment
echo $PWD  # Must be ~/Projects/belaguru-bhajans
hostname   # Must be local Mac, NOT remote server

# 2. Verify database
sqlite3 data/portal.db "SELECT COUNT(*) FROM bhajans"  # Should be ~201

# 3. If in doubt, ASK!
```

### Rollback Plan
Every migration has rollback:
```sql
-- migrations/001_create_tag_taxonomy.sql
-- Rollback:
DROP TABLE IF EXISTS bhajan_tags;
DROP TABLE IF EXISTS tag_synonyms;
DROP TABLE IF EXISTS tag_translations;
DROP TABLE IF EXISTS tag_taxonomy;
```

---

## 📁 **File Structure**

```
belaguru-bhajans/
├── migrations/
│   ├── 001_create_tag_taxonomy.sql
│   ├── 002_populate_taxonomy.sql
│   └── 003_migrate_existing_tags.sql
├── scripts/
│   ├── migrate_tags.py        # Migration script
│   ├── auto_tag.py            # Auto-tagging
│   └── verify_migration.py    # Verification
├── models.py                   # Updated ORM models
├── main.py                     # New API endpoints
├── static/
│   ├── app.js                 # Tag selector UI
│   └── admin-tags.html        # Admin UI
├── tests/
│   ├── test_tag_models.py
│   ├── test_tag_api.py
│   └── test_auto_tagging.py
└── TAG-HIERARCHY-IMPLEMENTATION-PLAN.md (this file)
```

---

## 🎯 **Success Metrics**

### Coverage
- [ ] 100% bhajans have tags (currently 60%)
- [ ] Average 3-4 tags per bhajan (currently 2.3)
- [ ] 0 duplicate tags (currently 9 groups)

### Accuracy
- [ ] 95%+ search accuracy
- [ ] Auto-tagging precision: >85%
- [ ] Synonym matching: 100%

### Performance
- [ ] Tag filter query: <100ms
- [ ] Hierarchical search: <200ms
- [ ] API response: <500ms

### User Experience
- [ ] Easy to find bhajans by deity
- [ ] Easy to find bhajans by type
- [ ] Multilingual search works
- [ ] Admin can manage tags easily

---

## 🚀 **Next Steps**

1. **TODAY:** Review this plan
2. **Approve:** Confirm approach
3. **Start Phase 1:** Create database schema
4. **Daily check-ins:** Progress updates
5. **UAT in 2 weeks:** User testing
6. **Production in 3 weeks:** After approval

---

**Questions? Ask before starting any task!**

**Remember: When in doubt about environment, ALWAYS ASK!**
