# E2E Test: Delete Bhajan Functionality

## File Location
`tests/e2e/test_delete_bhajan.spec.js`

## Test Coverage

### 1. **Create Test Bhajan via API** ✓
- Creates a test bhajan using the POST `/api/bhajans` endpoint
- Stores bhajan ID for use in subsequent tests
- Verifies API response and ID assignment

### 2. **Navigate and Verify Delete Button** ✓
- Navigates to bhajan detail page
- Verifies delete button exists and is visible
- Checks button styling (red background #dc2626)

### 3. **Confirmation Dialog** ✓
- Clicks delete button
- Verifies confirmation dialog appears
- Checks dialog message content
- Dismisses dialog (cancel operation)

### 4. **Cancel Confirmation** ✓
- Tests that dismissing confirmation keeps bhajan intact
- Verifies bhajan still accessible via API after cancel

### 5. **Confirm Deletion (Critical)** ✓
- Accepts confirmation dialog
- Verifies success alert shown
- **CRITICAL: Verifies bhajan returns 404 after deletion**
- Checks page redirects to home
- Monitors for JavaScript errors

### 6. **Deleted Bhajan Not in List** ✓
- Creates new bhajan
- Verifies it appears in search results
- Deletes the bhajan
- **CRITICAL: Verifies it no longer appears in list**

### 7. **No JavaScript Errors** ✓
- Monitors `pageerror` events during entire delete flow
- Ensures clean deletion without console errors

### 8. **Direct API Delete** ✓
- Tests DELETE endpoint directly
- Verifies correct response format: `{status: "deleted", id: X}`
- Confirms 404 on subsequent GET request

### 9. **Delete Non-Existent Bhajan** ✓
- Tests edge case: deleting bhajan ID 999999
- Verifies 404 response

## Test Strategy

### Data Verification
- **Soft Delete**: Backend sets `deleted_at` timestamp
- **API Behavior**: Deleted bhajans return 404 on GET
- **UI Behavior**: Deleted bhajans don't appear in lists
- **Actual Deletion**: Tests verify data is truly inaccessible, not just hidden

### Error Monitoring
- Captures JavaScript `pageerror` events
- Captures console errors
- Ensures clean UI operation during deletion

### User Flow
1. Create test data via API (isolated, no UI dependency)
2. Navigate to bhajan detail page
3. Click delete button
4. Handle confirmation dialog
5. Verify deletion (404 response)
6. Verify UI updates (removed from list)
7. Verify no errors

## Running Tests

```bash
# Run all delete tests
npx playwright test tests/e2e/test_delete_bhajan.spec.js

# Run with UI (headed mode)
npx playwright test tests/e2e/test_delete_bhajan.spec.js --headed

# Run specific test
npx playwright test tests/e2e/test_delete_bhajan.spec.js -g "confirm deletion"

# Debug mode
npx playwright test tests/e2e/test_delete_bhajan.spec.js --debug
```

## Important Notes

### Sequential Dependencies
Tests are designed to run independently, but some tests create their own test data:
- Test 1 creates shared test bhajan for tests 2-5
- Tests 6, 7, 8, 9 create their own isolated test data

### Base URL
Tests use `http://localhost:8001` - ensure server is running:
```bash
cd ~/Projects/belaguru-bhajans
python main.py
```

### Soft Delete Implementation
Backend uses soft delete (sets `deleted_at` timestamp), but API treats soft-deleted bhajans as non-existent:
- GET returns 404
- List endpoints exclude deleted bhajans
- This is the correct behavior and tests verify it

### Critical Assertions
The most important test is **"confirm deletion and verify bhajan is deleted"**:
```javascript
const response = await request.get(`http://localhost:8001/api/bhajans/${testBhajanId}`);
expect(response.status()).toBe(404); // Must return 404!
```

This ensures data is truly deleted, not just hidden in the UI.

## Test Output Example

```
Running 9 tests using 1 worker

  ✓ create test bhajan via API (1.2s)
  ✓ navigate to test bhajan and verify delete button exists (2.3s)
  ✓ delete button shows confirmation dialog (1.8s)
  ✓ cancel confirmation keeps bhajan intact (2.1s)
  ✓ confirm deletion and verify bhajan is deleted (3.5s)
  ✓ deleted bhajan not visible in list (4.2s)
  ✓ verify no JavaScript errors during delete operation (2.8s)
  ✓ direct API delete returns correct response (1.4s)
  ✓ delete non-existent bhajan returns 404 (0.8s)

  9 passed (20.1s)
```

## Maintenance

When updating delete functionality:
1. Update backend soft delete logic → Run test 8 (API delete)
2. Update UI delete button → Run test 2 (verify button)
3. Update confirmation dialog → Run test 3 (confirmation)
4. Update list filtering → Run test 6 (not in list)
5. Full regression → Run all 9 tests

## Integration with CI/CD

Add to `package.json` scripts:
```json
{
  "scripts": {
    "test:delete": "playwright test tests/e2e/test_delete_bhajan.spec.js"
  }
}
```

Add to nightly test suite in `run-nightly-tests.sh`.
