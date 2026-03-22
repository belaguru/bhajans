# Tag Hierarchy Implementation Plan (TDD + Parallel Execution)
**Project:** Belaguru Bhajans - Separate Taxonomy Table  
**Branch:** feature/tag-hierarchy  
**Environment:** STAGING ONLY (~/Projects/belaguru-bhajans)  
**Lead:** Main Agent (Simba) on Opus  
**Workers:** Subagents on Sonnet  
**Escalation:** Kashi (only for emergencies or loops)  
**Start Date:** March 22, 2026  
**Estimated Duration:** 10-12 days (parallelized from 3 weeks)

---

## 🎯 **Execution Strategy**

### **TDD Mandate**
Every task follows **Red-Green-Refactor**:
1. ✅ **RED:** Write failing test FIRST
2. ✅ **GREEN:** Implement minimum code to pass
3. ✅ **REFACTOR:** Clean up while tests still pass
4. ✅ **VALIDATE:** Run full test suite before commit

### **Parallelization**
- **Main Agent (Opus):** Orchestration, decision-making, code review
- **Subagents (Sonnet):** Parallel execution of independent tasks
- **Rule:** Max 3 parallel subagents at once (quality > speed)

### **Validation Gates**
Each phase has mandatory validation:
- ✅ Unit tests pass (100% for new code)
- ✅ Integration tests pass
- ✅ Manual QA checklist completed
- ✅ Git commit with tests included
- ✅ Documentation updated

---

## 📋 **Parallelized Task Graph**

```
WEEK 1 (Days 1-5)
┌─────────────────────────────────────────────────────┐
│ PARALLEL STREAM A: Database + Migration            │
│ ├─ Task 1.1: Schema (Agent A) ────────┐            │
│ ├─ Task 1.2: Populate Taxonomy (Agent A) │ → Merge │
│ └─ Task 2.1: Tag Mapping (Agent B) ──────┘         │
│                                                      │
│ PARALLEL STREAM B: Auto-Tagging                    │
│ └─ Task 3.1: Build Auto-Tagger (Agent C) ─────────┐│
│                                                     ││
│ SEQUENTIAL (depends on above)                      ││
│ └─ Task 2.2: Migration Script ←─────────────────┬──┘│
│ └─ Task 3.2: Tag Untagged Bhajans ←─────────────┘   │
└─────────────────────────────────────────────────────┘

WEEK 2 (Days 6-10)
┌─────────────────────────────────────────────────────┐
│ PARALLEL STREAM C: Backend                         │
│ ├─ Task 4.1: Update Models (Agent D) ──────┐       │
│ ├─ Task 4.2: Tag API Endpoints (Agent E) ──┤ Merge │
│ └─ Task 4.3: Dual-Write Strategy (Agent F) ┘       │
│                                                      │
│ PARALLEL STREAM D: Frontend (can start early)      │
│ ├─ Task 5.1: Tag Selector UI (Agent G) ────┐       │
│ ├─ Task 5.2: Search/Filter UI (Agent H) ───┤ Merge │
│ └─ Task 5.3: Admin UI (Agent I) ────────────┘       │
└─────────────────────────────────────────────────────┘

WEEK 2-3 (Days 11-12)
┌─────────────────────────────────────────────────────┐
│ SEQUENTIAL (Integration)                            │
│ ├─ Task 6.1: Integration Testing                   │
│ ├─ Task 6.2: Performance Testing                   │
│ ├─ Task 6.3: Documentation                         │
│ └─ Task 6.4: UAT                                    │
│                                                      │
│ PRODUCTION (Day 13+ - with approval)                │
│ ├─ Task 7.1: Pre-Deployment Checklist              │
│ └─ Task 7.2: Production Deployment                  │
└─────────────────────────────────────────────────────┘
```

---

## 📋 **Tasks with TDD Validation**

### **Phase 1: Database Schema (Day 1-2, Parallel)**

#### **Task 1.1: Create Taxonomy Tables** [Agent A, Sonnet]
**TDD Cycle:**
1. **RED:** Write test expecting tables to exist
   ```python
   def test_tag_taxonomy_table_exists():
       assert table_exists("tag_taxonomy")
       assert has_columns("tag_taxonomy", ["id", "name", "parent_id"])
   ```
2. **GREEN:** Write SQL migration
3. **REFACTOR:** Add indexes, constraints
4. **VALIDATE:**
   - [ ] Run `pytest tests/test_schema.py`
   - [ ] Verify indexes created
   - [ ] Check foreign key constraints
   - [ ] Run migration on test database
   - [ ] Commit: "feat(db): Add tag taxonomy tables with tests"

**Deliverable:** `migrations/001_create_tag_taxonomy.sql` + tests  
**Time:** 6 hours  
**Subagent:** TagSchemaBuilder (Sonnet)

---

#### **Task 1.2: Populate Core Taxonomy** [Agent A, Sonnet]
**TDD Cycle:**
1. **RED:** Write test expecting 50 core tags
   ```python
   def test_core_tags_populated():
       tags = db.query(TagTaxonomy).all()
       assert len(tags) == 50
       assert has_tag("Krishna", parent="Vishnu")
   ```
2. **GREEN:** Insert canonical tags with SQL
3. **REFACTOR:** Organize by category, add metadata
4. **VALIDATE:**
   - [ ] Run `pytest tests/test_taxonomy.py`
   - [ ] Verify all 6 categories present
   - [ ] Check hierarchies correct (Krishna → Vishnu → Deity)
   - [ ] Verify translations exist (4 languages)
   - [ ] Commit: "feat(db): Populate 50 canonical tags with hierarchy"

**Deliverable:** `migrations/002_populate_taxonomy.sql` + tests  
**Time:** 4 hours  
**Subagent:** TagSchemaBuilder (same as 1.1)

---

### **Phase 2: Migration Scripts (Day 2-3, Parallel after 1.2)**

#### **Task 2.1: Tag Cleanup Mapping** [Agent B, Sonnet]
**TDD Cycle:**
1. **RED:** Write test expecting all 68 tags mapped
   ```python
   def test_all_tags_have_mapping():
       mapping = load_csv("tag-migration-mapping.csv")
       current_tags = get_all_current_tags()
       assert len(mapping) == len(current_tags)
       assert all(tag in mapping for tag in current_tags)
   ```
2. **GREEN:** Create mapping CSV (manual + script)
3. **REFACTOR:** Group by action (MERGE, MAP, DELETE)
4. **VALIDATE:**
   - [ ] Run `pytest tests/test_tag_mapping.py`
   - [ ] Manual review of 9 duplicate groups
   - [ ] Verify case fixes correct
   - [ ] Check meta tags flagged for deletion
   - [ ] Commit: "feat(migration): Create tag cleanup mapping with validation"

**Deliverable:** `tag-migration-mapping.csv` + tests  
**Time:** 3 hours  
**Subagent:** TagMappingAnalyzer (Sonnet)  
**Parallel with:** 1.2

---

#### **Task 2.2: Data Migration Script** [Sequential after 2.1]
**TDD Cycle:**
1. **RED:** Write test expecting 380 tag instances migrated
   ```python
   def test_migration_preserves_all_tags():
       before = count_tag_instances()  # 380
       run_migration(dry_run=False)
       after = count_bhajan_tags()
       assert after >= before
       assert no_data_loss()
   ```
2. **GREEN:** Write `scripts/migrate_tags.py`
3. **REFACTOR:** Add rollback, dry-run, logging
4. **VALIDATE:**
   - [ ] Run `pytest tests/test_migration.py`
   - [ ] Dry-run test: no changes to database
   - [ ] Real migration test: verify data integrity
   - [ ] Test rollback: database restored
   - [ ] Manual QA: spot-check 10 bhajans
   - [ ] Commit: "feat(migration): Add tag migration script with rollback"

**Deliverable:** `scripts/migrate_tags.py` + tests  
**Time:** 6 hours  
**Subagent:** MigrationScriptDev (Sonnet)

---

### **Phase 3: Auto-Tagging (Day 3-4, Parallel with 2.1)**

#### **Task 3.1: Build Auto-Tagger** [Agent C, Sonnet]
**TDD Cycle:**
1. **RED:** Write tests for each tagging strategy
   ```python
   def test_deity_detection():
       bhajan = {"title": "Hanuman Chalisa", "lyrics": "..."}
       tags = auto_tag(bhajan)
       assert "Hanuman" in tags
       assert tags["Hanuman"]["confidence"] > 0.8
   
   def test_type_detection():
       bhajan = {"title": "Shiva Stotra", "lyrics": "..."}
       tags = auto_tag(bhajan)
       assert "Stotra" in tags
   ```
2. **GREEN:** Implement auto_tag() function
3. **REFACTOR:** Extract strategies, add confidence scoring
4. **VALIDATE:**
   - [ ] Run `pytest tests/test_auto_tag.py`
   - [ ] Precision test on 20 known bhajans (>85%)
   - [ ] Edge case tests (empty lyrics, mixed language)
   - [ ] Performance test (<1s per bhajan)
   - [ ] Commit: "feat(tagging): Add auto-tagger with 85%+ precision"

**Deliverable:** `scripts/auto_tag.py` + tests  
**Time:** 8 hours  
**Subagent:** AutoTaggerDev (Sonnet)  
**Parallel with:** 2.1

---

#### **Task 3.2: Tag Untagged Bhajans** [Sequential after 3.1]
**TDD Cycle:**
1. **RED:** Write test expecting 0 untagged bhajans
   ```python
   def test_all_bhajans_have_tags():
       bhajans = get_all_bhajans()
       for bhajan in bhajans:
           assert len(bhajan.tags) >= 2  # At least 2 tags
   ```
2. **GREEN:** Run auto-tagger on 110 untagged bhajans
3. **REFACTOR:** Manual review of low-confidence tags
4. **VALIDATE:**
   - [ ] Run `pytest tests/test_tagged_coverage.py`
   - [ ] Generate review report (high/medium/low confidence)
   - [ ] Manual QA: Review 10 medium-confidence bhajans
   - [ ] Verify tag distribution (avg 3-4 per bhajan)
   - [ ] Commit: "feat(tagging): Auto-tag 110 bhajans with review"

**Deliverable:** Tagged bhajans + review report  
**Time:** 4 hours  
**Subagent:** AutoTaggerDev (same as 3.1)

---

### **Phase 4: Backend API (Day 5-7, Parallel)**

#### **Task 4.1: Update Models** [Agent D, Sonnet]
**TDD Cycle:**
1. **RED:** Write model tests first
   ```python
   def test_tag_taxonomy_model():
       tag = TagTaxonomy(name="Krishna", parent_id=5)
       assert tag.parent.name == "Vishnu"
       assert tag.category == "Deity"
   
   def test_bhajan_tag_relationship():
       bhajan = Bhajan.query.first()
       assert len(bhajan.taxonomy_tags) >= 2
   ```
2. **GREEN:** Create SQLAlchemy models
3. **REFACTOR:** Add helper methods, validations
4. **VALIDATE:**
   - [ ] Run `pytest tests/test_tag_models.py`
   - [ ] Test relationships (parent/child)
   - [ ] Test cascading deletes
   - [ ] Test backward compatibility (old tags field)
   - [ ] Commit: "feat(models): Add tag taxonomy ORM models"

**Deliverable:** Updated `models.py` + tests  
**Time:** 5 hours  
**Subagent:** ModelsDev (Sonnet)  
**Parallel with:** 4.2, 4.3

---

#### **Task 4.2: Tag API Endpoints** [Agent E, Sonnet]
**TDD Cycle:**
1. **RED:** Write API tests first
   ```python
   def test_get_tags_tree():
       response = client.get("/api/tags/tree")
       assert response.status_code == 200
       tree = response.json()
       assert "Deities" in tree
       assert tree["Deities"]["children"]["Vishnu"]["children"]["Krishna"]
   
   def test_hierarchical_search():
       response = client.get("/api/bhajans?tag=Vishnu")
       bhajans = response.json()
       # Should include Krishna AND Rama bhajans
       assert any("Krishna" in b["tags"] for b in bhajans)
       assert any("Rama" in b["tags"] for b in bhajans)
   ```
2. **GREEN:** Implement API endpoints
3. **REFACTOR:** Optimize queries, add caching
4. **VALIDATE:**
   - [ ] Run `pytest tests/test_tag_api.py`
   - [ ] Test all 6 endpoints
   - [ ] Test synonym matching
   - [ ] Test hierarchical search
   - [ ] Performance test (<200ms)
   - [ ] Commit: "feat(api): Add tag taxonomy endpoints"

**Deliverable:** Updated `main.py` + tests  
**Time:** 6 hours  
**Subagent:** APIDev (Sonnet)  
**Parallel with:** 4.1, 4.3

---

#### **Task 4.3: Dual-Write Strategy** [Agent F, Sonnet]
**TDD Cycle:**
1. **RED:** Write backward compatibility tests
   ```python
   def test_dual_write():
       bhajan = create_bhajan(tags=["Krishna", "Bhajan"])
       # Old system
       assert "Krishna" in bhajan.tags  # JSON field
       # New system
       assert any(t.name == "Krishna" for t in bhajan.taxonomy_tags)
   
   def test_backward_compat_read():
       old_bhajan = create_old_format_bhajan()  # Only has JSON tags
       assert old_bhajan.get_tags() == old_bhajan.tags  # Fallback works
   ```
2. **GREEN:** Implement dual-write logic
3. **REFACTOR:** Add feature flag, clean up code
4. **VALIDATE:**
   - [ ] Run `pytest tests/test_dual_write.py`
   - [ ] Test create/update/delete paths
   - [ ] Test migration from old to new
   - [ ] Verify zero data loss
   - [ ] Commit: "feat(api): Add dual-write strategy for tags"

**Deliverable:** Updated `main.py` + tests  
**Time:** 3 hours  
**Subagent:** DualWriteDev (Sonnet)  
**Parallel with:** 4.1, 4.2

---

### **Phase 5: Frontend UI (Day 6-9, Parallel with Phase 4)**

#### **Task 5.1: Tag Selector Component** [Agent G, Sonnet]
**TDD Cycle:**
1. **RED:** Write Playwright tests first
   ```javascript
   test('tag selector shows hierarchy', async ({ page }) => {
     await page.goto('/upload');
     await page.click('text=Deities');
     await page.click('text=Vishnu');
     await expect(page.locator('text=Krishna')).toBeVisible();
   });
   ```
2. **GREEN:** Build React/JS component
3. **REFACTOR:** Add keyboard nav, accessibility
4. **VALIDATE:**
   - [ ] Run `npm run test:e2e`
   - [ ] Test multi-select
   - [ ] Test translations display
   - [ ] Test synonym suggestions
   - [ ] Manual QA on upload/edit forms
   - [ ] Commit: "feat(ui): Add hierarchical tag selector"

**Deliverable:** Updated `static/app.js` + E2E tests  
**Time:** 8 hours  
**Subagent:** UIDevTagSelector (Sonnet)  
**Parallel with:** 5.2, 5.3

---

#### **Task 5.2: Search/Filter UI** [Agent H, Sonnet]
**TDD Cycle:**
1. **RED:** Write E2E search tests
   ```javascript
   test('hierarchical search works', async ({ page }) => {
     await page.goto('/');
     await page.fill('input[name=search]', 'Vishnu');
     await page.click('button:has-text("Search")');
     // Should show Krishna AND Rama bhajans
     await expect(page.locator('text=Krishna')).toBeVisible();
     await expect(page.locator('text=Rama')).toBeVisible();
   });
   ```
2. **GREEN:** Implement search/filter UI
3. **REFACTOR:** Add breadcrumbs, tag cloud
4. **VALIDATE:**
   - [ ] Run `npm run test:e2e`
   - [ ] Test synonym search
   - [ ] Test multi-tag filter
   - [ ] Test AND/OR logic
   - [ ] Performance test (filter 200 bhajans <500ms)
   - [ ] Commit: "feat(ui): Add hierarchical search/filter"

**Deliverable:** Updated `static/app.js` + E2E tests  
**Time:** 6 hours  
**Subagent:** UIDevSearch (Sonnet)  
**Parallel with:** 5.1, 5.3

---

#### **Task 5.3: Admin Tag Management** [Agent I, Sonnet]
**TDD Cycle:**
1. **RED:** Write admin E2E tests
   ```javascript
   test('admin can add new tag', async ({ page }) => {
     await page.goto('/admin/tags');
     await page.click('button:has-text("Add Tag")');
     await page.fill('input[name=name]', 'NewDeity');
     await page.selectOption('select[name=parent]', 'Deity');
     await page.click('button:has-text("Save")');
     await expect(page.locator('text=NewDeity')).toBeVisible();
   });
   ```
2. **GREEN:** Build admin UI
3. **REFACTOR:** Add bulk operations, usage stats
4. **VALIDATE:**
   - [ ] Run `npm run test:e2e`
   - [ ] Test CRUD operations
   - [ ] Test translations editor
   - [ ] Test synonym manager
   - [ ] Test merge duplicates
   - [ ] Commit: "feat(ui): Add admin tag management"

**Deliverable:** `static/admin-tags.html` + E2E tests  
**Time:** 8 hours  
**Subagent:** UIDevAdmin (Sonnet)  
**Parallel with:** 5.1, 5.2

---

### **Phase 6: Testing & Integration (Day 10-11, Sequential)**

#### **Task 6.1: Integration Testing** [Main Agent, Opus]
**Full System Test:**
1. **Migration Test:**
   ```bash
   # Fresh database
   python scripts/migrate_tags.py --dry-run
   python scripts/migrate_tags.py
   pytest tests/test_migration_integration.py
   ```
2. **API Test:**
   ```bash
   pytest tests/test_api_integration.py -v
   ```
3. **UI Test:**
   ```bash
   npm run test:e2e
   ```
4. **VALIDATE:**
   - [ ] All 61+ unit tests pass
   - [ ] All 10+ E2E tests pass
   - [ ] Manual QA checklist (20 scenarios)
   - [ ] No regressions (old features work)
   - [ ] Commit: "test: Add full integration test suite"

**Deliverable:** Passing test suite + QA report  
**Time:** 6 hours  
**Owner:** Main Agent (Opus)

---

#### **Task 6.2: Performance Testing** [Main Agent, Opus]
**Benchmarks:**
```python
def test_tag_filter_performance():
    start = time.time()
    bhajans = filter_by_tag("Vishnu", limit=1000)
    elapsed = time.time() - start
    assert elapsed < 0.1  # <100ms

def test_hierarchical_search_performance():
    start = time.time()
    bhajans = search("Vishnu", include_children=True)
    elapsed = time.time() - start
    assert elapsed < 0.2  # <200ms
```

**VALIDATE:**
- [ ] Run `pytest tests/test_performance.py`
- [ ] All queries <200ms
- [ ] Add indexes if needed
- [ ] Cache tag tree (if >500ms)
- [ ] Commit: "perf: Optimize tag queries with indexes"

**Deliverable:** Performance benchmarks  
**Time:** 3 hours  
**Owner:** Main Agent (Opus)

---

#### **Task 6.3: Documentation** [Parallel Subagent, Sonnet]
**Deliverables:**
- [ ] API docs (Swagger/OpenAPI spec)
- [ ] Admin guide (tag management)
- [ ] User guide (searching with tags)
- [ ] Migration runbook
- [ ] Rollback procedure
- [ ] CHANGELOG.md entry

**VALIDATE:**
- [ ] All endpoints documented
- [ ] Screenshots included
- [ ] Examples tested
- [ ] Commit: "docs: Add tag hierarchy documentation"

**Time:** 3 hours  
**Subagent:** DocsWriter (Sonnet)  
**Parallel with:** 6.1, 6.2

---

#### **Task 6.4: User Acceptance Testing** [Main Agent, Opus]
**UAT Scenarios:**
1. As a user, search for "Vishnu" → find Krishna + Rama bhajans
2. As a user, upload new bhajan → select hierarchical tags
3. As a user, search in Kannada → synonym matching works
4. As admin, add new tag → appears in selector
5. As admin, merge duplicate tags → data preserved

**VALIDATE:**
- [ ] Deploy to qa.bhajans.s365.in
- [ ] Run all 5 scenarios with business users
- [ ] Collect feedback
- [ ] Fix critical issues
- [ ] Commit: "fix: UAT feedback implementation"

**Deliverable:** UAT approval  
**Time:** 4 hours  
**Owner:** Main Agent (Opus)

---

### **Phase 7: Production Deployment (Day 12+, with approval)**

#### **Task 7.1: Pre-Deployment Checklist** [Main Agent, Opus]
**Verification:**
- [ ] All tests passing (unit + E2E + integration)
- [ ] Performance acceptable (<200ms queries)
- [ ] UAT approved
- [ ] Documentation complete
- [ ] Rollback plan tested
- [ ] Production backup created
- [ ] Maintenance window scheduled

**ESCALATE TO KASHI:** Get explicit approval before proceeding

**Time:** 2 hours  
**Owner:** Main Agent (Opus)

---

#### **Task 7.2: Production Deployment** [Main Agent, Opus]
**Deployment Steps:**
1. Backup production database
2. Deploy code to production
3. Run migration script
4. Smoke test (5 critical paths)
5. Monitor for 24 hours

**VALIDATE:**
- [ ] Zero errors in logs
- [ ] Query performance <200ms
- [ ] User feedback positive
- [ ] Rollback plan ready (if needed)

**Deliverable:** Feature live on production  
**Time:** 4 hours + 24h monitoring  
**Owner:** Main Agent (Opus)

---

## 🔄 **TDD Workflow (Every Task)**

```
┌─────────────────────────────────────┐
│ 1. RED: Write Failing Test         │
│    - Test doesn't compile           │
│    - Or fails with expected error   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 2. GREEN: Minimum Code to Pass     │
│    - Simplest solution              │
│    - Test turns green               │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 3. REFACTOR: Clean Up               │
│    - Improve code quality           │
│    - Tests still pass               │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 4. VALIDATE: Full Suite             │
│    - Run ALL tests                  │
│    - Manual QA checklist            │
│    - Git commit (code + tests)      │
└─────────────────────────────────────┘
```

**Rule:** Code without tests = NOT DONE

---

## 🚀 **Parallelization Strategy**

### **Parallel Streams**

**Week 1 (Database + Auto-Tagging):**
```
Stream A (Agent A): Schema → Populate Taxonomy
Stream B (Agent B): Tag Mapping (parallel with A)
Stream C (Agent C): Auto-Tagger (parallel with A+B)
Sequential: Migration Script (depends on A+B)
Sequential: Tag Untagged (depends on C)
```

**Week 2 (Backend + Frontend):**
```
Stream D: Models (Agent D)
Stream E: API (Agent E, parallel with D)
Stream F: Dual-Write (Agent F, parallel with D+E)

Stream G: Tag Selector UI (Agent G, parallel with D+E+F)
Stream H: Search UI (Agent H, parallel with G)
Stream I: Admin UI (Agent I, parallel with G+H)
```

### **Subagent Coordination**

**Main Agent (Opus) responsibilities:**
- Spawn subagents with clear tasks
- Collect results via `sessions_yield()`
- Review code quality
- Merge work streams
- Run integration tests
- Make decisions (escalate if stuck >30 min)

**Subagent (Sonnet) responsibilities:**
- Execute assigned task
- Follow TDD cycle
- Return deliverable + tests
- Report blockers immediately
- Never touch production

---

## 📊 **Revised Timeline (Parallelized)**

| Day | Parallel Streams | Hours |
|-----|------------------|-------|
| 1-2 | Schema + Mapping + Auto-Tagger (3 agents) | 24 → 8 |
| 3 | Migration Script + Tag Bhajans (sequential) | 10 → 10 |
| 4-5 | Models + API + Dual-Write (3 agents) | 24 → 8 |
| 6-8 | UI Components (3 agents) | 36 → 12 |
| 9-10 | Integration Testing (main agent) | 12 → 12 |
| 11 | Documentation + UAT (parallel) | 8 → 4 |
| 12+ | Production Deployment | 6 → 6 |
| **Total** | **120 hours → 60 hours** | **10-12 days** |

**Parallelization savings: 50% time reduction**

---

## ✅ **Validation Checklist (Every Phase)**

### **Phase Complete When:**
- [ ] All tasks have passing tests
- [ ] Integration tests pass
- [ ] Manual QA checklist completed
- [ ] Code reviewed by Main Agent
- [ ] Documentation updated
- [ ] Git committed with tests
- [ ] No production touched

### **Ready for Next Phase When:**
- [ ] Previous phase 100% complete
- [ ] All validation gates passed
- [ ] Dependencies resolved
- [ ] Resources available

---

## 🚨 **Escalation Triggers**

**Escalate to Kashi ONLY when:**
1. ❌ Stuck in a loop for >30 minutes
2. ❌ Production accidentally touched
3. ❌ Critical bug found (data loss risk)
4. ❌ Scope change needed (>20% time increase)
5. ❌ Before production deployment (mandatory approval)

**DO NOT escalate for:**
- ✅ Normal development questions (Main Agent decides)
- ✅ Test failures (debug and fix)
- ✅ Subagent errors (retry or reassign)
- ✅ Minor delays (<1 hour)

---

## 📁 **File Locations**

**Obsidian (for review):**
```
SW Work/Projects/Belaguru/Tag Hierarchy - Implementation Plan (TDD + Parallel).md
```

**Git Repo (for execution):**
```
~/Projects/belaguru-bhajans/TAG-HIERARCHY-IMPLEMENTATION-PLAN.md
```

---

## 🎯 **Success Metrics**

### **Process Metrics:**
- [ ] 100% tasks have tests
- [ ] 0 commits without tests
- [ ] <10% rework (good first-time quality)
- [ ] 50% time savings via parallelization

### **Quality Metrics:**
- [ ] 100% bhajans tagged
- [ ] 95%+ search accuracy
- [ ] <200ms query performance
- [ ] 0 production incidents

### **User Metrics:**
- [ ] Easy to find bhajans by deity/type
- [ ] Multilingual search works
- [ ] Admin can manage tags easily
- [ ] UAT approval with minimal feedback

---

## 🚀 **Execution Starts Now**

**Main Agent (Opus) will:**
1. ✅ Move this plan to Obsidian (done)
2. ✅ Update git repo version
3. ✅ Start Phase 1 parallelization
4. ✅ Spawn 3 subagents (Schema, Mapping, Auto-Tagger)
5. ✅ Only escalate for emergencies

**Kashi: You're on standby. I'll run the show.**

---

**Last Updated:** March 22, 2026, 1:06 PM IST  
**Version:** 2.0 (TDD + Parallel Execution)  
**Lead:** Main Agent (Simba) on Opus  
**Status:** READY TO EXECUTE
