# Favorites Functionality - E2E Test Coverage

## Test File
`test_favorites.spec.js`

## Test Cases Implemented

### 1. Complete Favorites User Flow (Primary Test)
**Steps tested:**
1. ✅ Navigate to a bhajan from home page
2. ✅ Click "Add to Favorites" button (empty heart)
3. ✅ Verify favorite added:
   - Success feedback message appears
   - localStorage updated with bhajan ID
   - Heart icon changes to filled (❤️)
4. ✅ Navigate to Favorites page using `app.setPage('favorites')`
5. ✅ Verify bhajan appears in favorites list
6. ✅ Click bhajan in favorites to view it
7. ✅ Remove from favorites (click filled heart)
8. ✅ Verify removal feedback message
9. ✅ Navigate back to Favorites page
10. ✅ Verify empty state message: "No favorites yet"
11. ✅ Verify localStorage is empty

### 2. Multiple Bhajans to Favorites
- Adds up to 3 bhajans to favorites
- Verifies correct count in favorites page
- Verifies localStorage has all IDs

### 3. Favorites Persist Across Navigation
- Adds bhajan to favorites
- Navigates away and back
- Verifies favorite still exists

### 4. Heart Icon Toggle
- Verifies initial empty heart state
- Clicks to add favorite → filled heart appears
- Clicks to remove → empty heart returns

### 5. Empty Favorites State
- Navigates to favorites with no items
- Verifies "No favorites yet" message
- Verifies no bhajan cards present

### 6. Remove from Favorites Page
- Adds bhajan to favorites
- Opens favorites page
- Removes directly from favorites page (heart button)
- Verifies empty state appears

## Technical Details

### Selectors Used
- Bhajan cards: `.bhajan-card, .bhajan-item`
- Add button: `button[title*="Add to favorites"]` or emoji 🤍/♡
- Remove button: `button[title*="Remove from favorites"]` or emoji ❤️/♥
- Feedback messages: Div containing "Added to favorites" or "Removed from favorites"
- Empty state: `p:has-text("No favorites yet")`

### localStorage Keys
- `bhajan_favorites`: Array of integer bhajan IDs

### Navigation Method
Uses `window.app.setPage('favorites')` to navigate programmatically

### Test Isolation
- `beforeEach` hook clears localStorage before each test
- Ensures clean state for every test run

## Running the Tests

```bash
# Run all favorites tests
npx playwright test test_favorites.spec.js

# Run specific test
npx playwright test test_favorites.spec.js -g "complete favorites user flow"

# Run with UI mode (debugging)
npx playwright test test_favorites.spec.js --ui

# Show browser (headed mode)
npx playwright test test_favorites.spec.js --headed
```

## Coverage Summary
- ✅ Add to favorites
- ✅ Remove from favorites  
- ✅ Toggle favorite state
- ✅ Favorites page display
- ✅ Empty state handling
- ✅ localStorage persistence
- ✅ UI feedback (heart icons, messages)
- ✅ Navigation between pages
- ✅ Multiple favorites management
- ✅ Remove from favorites page directly

## Notes
- Tests use Playwright's best practices (await, expect, proper waits)
- Matches existing test patterns in the project
- Uses 500ms slowMo for visibility during runs
- Takes screenshots/videos on failure (configured in playwright.config.js)
