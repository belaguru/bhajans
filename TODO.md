# Belaguru Bhajans - TODO

## 🔴 CRITICAL: Test Isolation (MUST DO)

**Problem:** Tests depend on production database state. When data changes, tests break.

**Current (wrong):**
- Tests use real `data/portal.db`
- Tests expect specific data counts (76 tags, etc.)
- Tests create data but don't clean up → pollution
- Database cleanup breaks tests

**Required fix:**
1. Create `tests/conftest.py` with isolated database fixtures
2. Each test creates its OWN setup data
3. Use in-memory SQLite (fast, auto-cleanup)
4. Tests validate against their own data, not production
5. Zero dependency on production database state

**Estimated effort:** 2-3 hours

**Pattern to follow:**
```python
@pytest.fixture
def test_db():
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()

def test_tag_migration(test_db):
    # ARRANGE - Create own data
    test_db.add(Bhajan(title="Test", tags='["Anjaneya"]'))
    test_db.commit()
    
    # ACT
    result = migrate_tags(test_db)
    
    # ASSERT against own data
    assert result['migrated'] == 1
```

**Added:** 2026-03-22  
**Priority:** CRITICAL (blocks reliable CI/CD)  
**Status:** TODO
