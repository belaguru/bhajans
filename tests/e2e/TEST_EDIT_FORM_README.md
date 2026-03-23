# Edit Form E2E Test Suite

**File:** `test_edit_form.spec.js`  
**Base URL:** http://localhost:8001  
**Test Framework:** Playwright  
**Status:** ✅ All tests passing (8/8)

## Test Coverage

This test suite provides comprehensive E2E coverage for the Belaguru Bhajans edit form functionality.

### Tests Included

1. **Navigation Test** - Verifies user can navigate from bhajan detail page to edit form
2. **Data Loading Test** - Confirms edit form loads with current bhajan values
3. **Title/Lyrics Modification** - Tests ability to modify title and lyrics fields
4. **Tag Selection** - Verifies tag selector functionality and interaction
5. **Form Submission** - Tests full edit workflow with no JavaScript errors
6. **Page Load Validation** - Ensures no errors occur when loading edit form
7. **Form Persistence** - Documents expected behavior for form state
8. **Cancel/Back Navigation** - Tests navigation back to bhajan detail page

## Key Features Tested

- ✅ Edit button click from bhajan page
- ✅ Form fields populated with existing data
- ✅ Title and lyrics modification
- ✅ Hierarchical tag selector rendering
- ✅ Tag selection/deselection
- ✅ Form submission workflow
- ✅ JavaScript error detection
- ✅ Back navigation

## Technical Details

### Form Elements

- **Title Field:** `#edit_title` (text input)
- **Lyrics Field:** `#edit_lyrics` (textarea)
- **Tag Selector:** `#edit_tags_selector` (hierarchical component)
- **Tag Hidden Input:** `#selected_tag_ids` (comma-separated tag IDs)
- **Uploader Name:** `#edit_uploader_name` (text input)
- **YouTube URL:** `#edit_youtube_url` (url input)
- **MP3 File:** `#edit_mp3_file` (file input)
- **Submit Button:** Button with text "Save Changes"

### JavaScript Integration

The edit form uses the `app.editBhajan(id)` method to navigate to edit mode.  
Form submission is handled by `app.handleEditSubmit(event, bhajanId)`.

The form correctly reads tag IDs from the `#selected_tag_ids` hidden input created by the hierarchical tag selector.

### Known Issues & Notes

**Whitespace Handling:**  
The test normalizes trailing whitespace when comparing lyrics because HTML textareas may handle whitespace differently than raw data. This is expected behavior.

**Alert Handling:**  
The submission test automatically accepts any browser alerts (success messages) to prevent test hanging.

**Timing:**  
Tests use `waitForTimeout()` to ensure asynchronous rendering completes. Adjust timeouts if tests become flaky on slower systems.

## Running the Tests

### Run all edit form tests:
```bash
cd ~/Projects/belaguru-bhajans
npx playwright test test_edit_form.spec.js
```

### Run specific test:
```bash
npx playwright test test_edit_form.spec.js --grep "submit form"
```

### Run with UI mode (debugging):
```bash
npx playwright test test_edit_form.spec.js --ui
```

### Run with trace (detailed debugging):
```bash
npx playwright test test_edit_form.spec.js --trace on
```

## Test Results

Last run: 2026-03-23  
**Result:** ✅ 8/8 passed  
**Duration:** ~44 seconds  
**Browser:** Chromium (Desktop Chrome)

## Historical Context

**Original Bug Report:**  
The edit form was initially reported to have a null reference error when submitting because the code tried to access `document.getElementById("edit_tags_value")` which didn't exist.

**Bug Status:** ✅ **FIXED**  
The code has been corrected to use `document.getElementById("selected_tag_ids")` which is the actual hidden input created by the hierarchical tag selector.

The test suite now validates that the edit form works correctly with the hierarchical tag selector implementation.

## Future Enhancements

Potential improvements to test coverage:

- [ ] Test MP3 file upload functionality
- [ ] Test YouTube URL validation
- [ ] Test empty form submission (validation)
- [ ] Test special characters in title/lyrics
- [ ] Test very long lyrics (performance)
- [ ] Test concurrent edits (optimistic locking)
- [ ] Test offline behavior (network errors)
- [ ] Visual regression testing (screenshots)

## Maintenance

**Update triggers:**
- UI changes to edit form layout
- Tag selector implementation changes
- Form validation rule changes
- API endpoint changes for PUT /api/bhajans/:id

**Test review schedule:** Quarterly or when edit form is modified
