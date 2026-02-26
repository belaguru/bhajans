# Safe Schema Migrations

## NEVER AGAIN: Database Safety Rules

### Rule 1: Always Backup Before Schema Changes
```bash
# Before ANY database changes:
cp ~/.belaguru/portal.db ~/.belaguru/portal.db.backup.$(date +%Y%m%d_%H%M%S)
```

### Rule 2: Use ALTER TABLE for Safe Migrations
```python
# Instead of deleting DB, use:
cursor.execute("ALTER TABLE bhajans ADD COLUMN new_col DATATYPE")
conn.commit()
```

### Rule 3: Test on Backup First
```bash
# Test migration on a copy first
cp ~/.belaguru/portal.db /tmp/test.db
# Run migration on /tmp/test.db
# Verify it works
# Then apply to real database
```

### Rule 4: Get User Confirmation for Destructive Operations
```
"About to delete database. This cannot be undone. Continue? (yes/no)"
```

### Rule 5: Always Communicate Changes
- Warn before any destructive operations
- Explain what will happen
- Get explicit approval

---

## What Went Wrong (Lesson Learned)

I added a `deleted_at` column to the schema. Instead of:
1. ❌ Deleting the entire database

I should have:
1. ✅ Backed up the database
2. ✅ Used `ALTER TABLE` to add the column
3. ✅ Tested the migration
4. ✅ Applied it to the real database
5. ✅ Kept the backup for rollback if needed

---

## Going Forward

All future schema changes will:
- [ ] Create backup first
- [ ] Use migration script
- [ ] Test on copy
- [ ] Get user approval
- [ ] Preserve all data
