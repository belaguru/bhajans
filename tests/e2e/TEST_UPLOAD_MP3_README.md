# E2E Test: Upload with MP3 File

**File:** `test_upload_with_mp3.spec.js`

## Overview

Comprehensive end-to-end test suite for the MP3 upload functionality in Belaguru Bhajans.

## Test Coverage (12 tests)

### 1. **Form Navigation & Elements**
- Navigate to upload page
- Verify all form fields present (title, lyrics, MP3 input, uploader name, YouTube URL)
- Verify tag selector present

### 2. **Complete Upload Flow**
- Fill in title
- Fill in lyrics (100+ characters)
- Select tags using hierarchical selector
- Attach MP3 file from test fixtures
- Submit form
- Verify success alert
- Verify navigation back to home

### 3. **Bhajan Verification**
- Verify newly created bhajan appears on homepage
- Navigate to bhajan detail page
- Verify audio player present
- Verify audio source URL correct

### 4. **File Validation - Format**
- Reject non-MP3 files (.js, .txt, etc.)
- Verify alert message shows "Only .mp3 files are allowed"
- Verify file input cleared after rejection

### 5. **File Validation - Size**
- Test file under 5MB is accepted
- Verify success indicator shows
- Note: >5MB test requires generating large fixture

### 6. **File Size Display**
- Verify initial help text: "Max 5MB • MP3 format only"
- After upload, verify success message with filename and size
- Verify green checkmark indicator

### 7. **Required Fields Validation**
- Test empty form submission
- Verify HTML5 validation prevents submission
- Verify user stays on upload page

### 8. **Tag Selection Validation**
- Fill all fields except tags
- Verify alert requires tag selection
- Verify submission blocked without tags

### 9. **Optional MP3 Upload**
- Test bhajan creation WITHOUT MP3 file
- Verify successful creation
- Verify bhajan appears on homepage

### 10. **MP3 Persistence**
- Query API for bhajan with MP3
- Verify MP3 field present in response
- Navigate to detail page
- Verify audio player shows correct file

### 11. **Complete User Journey**
- End-to-end flow: upload → view → verify playback
- Tests entire user experience in one flow
- Verifies all components work together

### 12. **Audio Playback Verification**
- Verify audio element readyState
- Verify audio controls present
- Verify source URL matches uploaded file

## Test Fixtures Used

All test files from `static/audio/`:
- `om-namah-shivaya.mp3` (~950KB)
- `gayatri-mantra.mp3` (~950KB)
- `hare-rama-krishna.mp3` (~950KB)
- `mahamrityunjaya.mp3` (~950KB)
- `raghukula-nandana-raaja-raama.mp3` (~4.8MB - largest test file)

## Running the Tests

```bash
# Run all MP3 upload tests
npx playwright test tests/e2e/test_upload_with_mp3.spec.js

# Run specific test
npx playwright test tests/e2e/test_upload_with_mp3.spec.js -g "complete upload flow"

# Run with UI
npx playwright test tests/e2e/test_upload_with_mp3.spec.js --ui

# Run in headed mode (see browser)
npx playwright test tests/e2e/test_upload_with_mp3.spec.js --headed
```

## Test Patterns Used

- **Playwright syntax** matching existing tests
- **Base URL:** `http://localhost:8001`
- **Wait strategies:** `waitForTimeout()` for AJAX/DOM updates
- **Dialog handling:** `page.once('dialog', ...)` for alerts
- **File uploads:** `setInputFiles()` with absolute paths
- **Element selectors:** ID, text, CSS, filter chains
- **Assertions:** `expect().toBeVisible()`, `toContain()`, `toBe()`

## Known Limitations

1. **>5MB test**: Requires generating a large MP3 fixture (not included)
2. **Audio playback**: Can't fully test actual audio playback (browser security)
3. **File cleanup**: Tests create bhajans in database (consider cleanup in teardown)

## Integration Points

- **Frontend:** `static/app.js` (upload form, validation, tag selector)
- **Backend:** `/api/bhajans` (POST endpoint for creation)
- **Storage:** `static/audio/` (MP3 file storage)
- **Database:** Bhajans table (mp3_file column)

## Success Criteria

All 12 tests must pass for MP3 upload feature to be considered fully functional.

## Related Tests

- `test_edit_form.spec.js` - Edit form (includes MP3 replacement)
- `test_mp3_chants_api.spec.js` - API-level MP3 field verification
- `test_audio_player.spec.js` - Audio player component
