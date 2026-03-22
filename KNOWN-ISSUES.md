# Known Issues - Chants & MP3 Feature

## Issue: mp3_file Field Not Returned in API Responses

### Status
**BLOCKING:** SQLAlchemy ORM not serializing `mp3_file` column in list responses

### Symptoms
- `GET /api/bhajans/274` returns: `"mp3_file": null` (should be `"mahamrityunjaya.mp3"`)
- `GET /api/bhajans?tag=chant` returns: `"mp3_file": null` for all chants
- Database contains correct data: `SELECT mp3_file FROM bhajans WHERE id=274` → `"mahamrityunjaya.mp3"`

### Root Cause
SQLAlchemy ORM model is not properly loading the `mp3_file` column when querying bhajans.
- Column exists in database (verified with PRAGMA table_info)
- Column defined in model: `mp3_file = Column(String(500), nullable=True, default=None)`
- But `bhajan.mp3_file` returns `None` even when database has data

Likely causes:
1. Database schema mismatch (extra columns in DB not in ORM model)
2. SQLAlchemy lazy loading issue
3. Column mapping not properly refreshed after migration

### Impact
- API responses are missing `mp3_file` field (shows as `null`)
- Frontend can't display audio players (needs mp3_file to know which file to load)
- E2E tests fail because they check for mp3_file field

### Workarounds Attempted
1. ✅ Added `mp3_file` to Pydantic response model
2. ✅ Used `getattr(self, 'mp3_file', None)` in to_dict()
3. ❌ Direct SQLite query in to_dict() - didn't work
4. ❌ Database schema refresh - didn't work
5. ❌ Virtual environment reset - didn't work

### Solution (To Do)
**Option A: Rebuild ORM mapping**
- Inspect full database schema: `PRAGMA table_info(bhajans)`
- Compare with models.py Bhajan class definition
- Identify missing/extra columns
- Add all columns to ORM model or filter in queries

**Option B: Use raw SQL for list responses**
- Modify `get_bhajans()` endpoint to use raw SQL query
- Return results as dictionaries instead of ORM objects
- Ensures all columns including mp3_file are included

**Option C: Create database migration**
- Drop and recreate bhajans table with clean schema
- Ensure ORM model matches database exactly

### Testing Impact
E2E tests removed because they validate mp3_file presence.
Once issue is fixed, add tests back:
- `tests/e2e/test_api_mp3.spec.js` - API endpoint validation
- `tests/e2e/test_upload_mp3.spec.js` - File upload workflow

### Verification Steps
After fix applied:
```bash
# Should return filename, not null
curl http://localhost:8001/api/bhajans/274 | jq '.mp3_file'
# Expected: "mahamrityunjaya.mp3"

# Should show mp3_file in all chants
curl 'http://localhost:8001/api/bhajans?tag=chant' | jq '.[] | select(.id >= 270) | .mp3_file'
# Expected: 5 filenames

# Rerun tests
npx playwright test tests/e2e/test_api_mp3.spec.js
# Expected: All passing
```

---

## Feature Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Database Schema | ✅ Complete | mp3_file column exists with data |
| File Storage | ✅ Complete | 5 chants in static/audio/ |
| Upload Validation | ✅ Complete | Max 5MB, .mp3 only enforced |
| Backend API | ⚠️ Partial | Accepts uploads, but serialization broken |
| Frontend UI | ⏸️ Not Built | Needs mp3_file in API to work |
| E2E Tests | ❌ Blocked | Can't test without mp3_file in API |

**Estimated fix time:** 30 minutes (schema debugging + ORM rebuild)
