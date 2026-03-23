# Floating Menu E2E Test

**File:** `test_floating_menu.spec.js`

## Coverage

### Core Functionality ✅
1. **Button Visibility** - Floating menu button visible on homepage (bottom-right)
2. **Menu Opening** - Click button opens menu with visible class
3. **Menu Content** - All 4 navigation options present:
   - Home 🏠
   - Search 🔍
   - Upload 📝
   - Favorites ❤️
4. **Navigation** - Each option navigates correctly and closes menu
5. **Menu Closing** - Menu closes after each selection
6. **Daily Bhajan** - Conditional test for "Daily Bhajan" option (today's bhajan)

### Mobile Support ✅
- Mobile viewport test (390x844 - iPhone 12 Pro)
- All menu items visible on mobile
- Button and menu work correctly on small screens

### Robustness ✅
- Menu can be opened/closed multiple times
- Button persists after menu closes
- Menu persists across page navigation
- Font size controls present in menu

### Accessibility ✅
- Button has title attribute ("Menu")
- Keyboard accessibility test

## Test Structure

**Total Tests:** 16
- 14 core functionality tests
- 2 accessibility tests

**Follows patterns from:**
- `test_homepage.spec.js` - Page structure and selectors
- `test_frontend_comprehensive.spec.js` - Mobile viewports and robustness

## Running Tests

```bash
# All floating menu tests
npx playwright test test_floating_menu.spec.js

# Specific test
npx playwright test test_floating_menu.spec.js -g "floating menu button is visible"

# With UI
npx playwright test test_floating_menu.spec.js --ui

# Debug mode
npx playwright test test_floating_menu.spec.js --debug
```

## Key Selectors

- `#floating-menu-button` - Main menu button
- `#floating-menu` - Menu container
- `#floating-menu.visible` - Menu when open
- `.floating-menu-item` - Individual menu items
- `.font-size-controls` - Font size adjustment section

## Expected Behavior

1. **Menu Opens:** Button click adds `visible` class to menu
2. **Navigation:** Clicking menu item triggers `app.setPage()` or `app.openSearch()`
3. **Menu Closes:** Navigation calls `app.closeFloatingMenu()` removing `visible` class
4. **Daily Bhajan:** Only appears if `bhajans.length > 0`
5. **Button Persists:** Always visible (bottom-right, fixed position)

## Conditional Tests

**Daily Bhajan:** Tests handle both scenarios:
- If bhajans loaded → verifies Daily Bhajan option and navigation
- If no bhajans → test passes (conditional feature)

## Mobile Viewport

**Dimensions:** 390x844 (iPhone 12 Pro)
**Tests:** Button visible, menu opens, all items visible

## Notes

- Uses `slowMo: 500` from playwright.config.js (visible actions)
- Uses `headless: false` (browser window shown)
- Base URL: `http://localhost:8001`
- Web server auto-starts via `run-staging.sh`

## Priority

**🔴 Critical** - Primary navigation element must work flawlessly!

These tests verify the main way users navigate the Belaguru Bhajans site.
