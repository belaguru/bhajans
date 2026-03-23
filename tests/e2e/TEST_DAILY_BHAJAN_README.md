# Daily Bhajan Banner E2E Tests

## Overview
Comprehensive E2E test suite for the new "Today's Bhajan" feature that shows day-of-week specific bhajan recommendations.

## Test File
`test_daily_bhajan.spec.js`

## Features Tested

### Core Functionality (6 tests)
1. **Banner Existence** - Verifies banner appears on homepage
2. **Date Display** - Confirms today's date and day-of-week shown
3. **Bhajan Title** - Validates a bhajan title is displayed
4. **Click Navigation** - Ensures clicking banner navigates to bhajan detail page
5. **Day Tag Verification** - Confirms bhajan has today's day tag
6. **Clickability** - Verifies banner has onclick handler

### Day-of-Week Coverage (7 tests)
Tests for all 7 days of the week with mocked dates:
- **Monday** → Shiva bhajan
- **Tuesday** → Hanuman bhajan (different from Monday)
- **Wednesday** → Ganesh/Vighnaharta bhajan
- **Thursday** → Guru/Dattareya bhajan
- **Friday** → Devi bhajan
- **Saturday** → Hanuman/Anjaneya bhajan
- **Sunday** → Surya/Sun God bhajan

Each test:
- Mocks the system date to specific day
- Verifies correct day name shown in banner
- Clicks banner to open bhajan detail
- Confirms bhajan has correct day tag

### Edge Cases & Consistency (3 tests)
1. **Consistency Check** - Same day shows same bhajan on reload
2. **Date Format** - Verifies month name and day number displayed
3. **Fallback Mechanism** - Shows random bhajan if no day-specific bhajans exist

## Test Approach

### Date Mocking
Uses Playwright's `context.addInitScript()` to override the `Date` object:
```javascript
await context.addInitScript(() => {
  const OriginalDate = Date;
  Date = class extends OriginalDate {
    constructor(...args) {
      if (args.length === 0) {
        super(2026, 2, 23, 10, 0, 0); // Monday, March 23, 2026
      } else {
        super(...args);
      }
    }
    static now() {
      return new OriginalDate(2026, 2, 23, 10, 0, 0).getTime();
    }
  };
});
```

### Selectors Used
- `.daily-bhajan-banner` - Main banner container
- `.tags` - Tag section in bhajan detail page
- `#bhajan-content` - Bhajan detail content

### Expected User Flow
1. User visits homepage
2. Sees "TODAY'S BHAJAN" banner with current date
3. Banner shows a bhajan appropriate for day-of-week
4. User clicks banner
5. Navigates to bhajan detail page
6. Bhajan has corresponding day tag

## Running Tests

```bash
# Run all daily bhajan tests
npx playwright test test_daily_bhajan.spec.js

# Run specific test
npx playwright test test_daily_bhajan.spec.js -g "Monday shows Shiva"

# Run with UI mode (interactive)
npx playwright test test_daily_bhajan.spec.js --ui

# Run in headed mode (see browser)
npx playwright test test_daily_bhajan.spec.js --headed

# Generate HTML report
npx playwright test test_daily_bhajan.spec.js --reporter=html
```

## Coverage

**Total: 16 tests**
- ✅ Banner rendering and display
- ✅ Click navigation
- ✅ All 7 days of the week
- ✅ Tag verification
- ✅ Date formatting
- ✅ Consistency across reloads
- ✅ Fallback behavior

## Notes

### Why Date Mocking?
The daily bhajan feature depends on `new Date()` to determine which day it is. To reliably test all 7 days of the week, we mock the Date object to return specific dates. This ensures:
- Tests are deterministic (always pass/fail consistently)
- Can test all days without waiting a week
- Can verify logic for days that might not have enough tagged bhajans

### Test Dates Used
- Monday: March 23, 2026
- Tuesday: March 24, 2026
- Wednesday: March 25, 2026
- Thursday: March 26, 2026
- Friday: March 27, 2026
- Saturday: March 28, 2026
- Sunday: March 29, 2026

All at 10:00 AM IST to ensure consistent day-of-year calculations.

### Known Limitations
1. **Requires tagged bhajans** - Tests assume bhajans are properly tagged with day names
2. **Fallback testing** - One test verifies fallback works, but doesn't test all edge cases
3. **Time zone** - Tests use local system time zone (should be Asia/Calcutta for production)

## Related Files
- **Implementation**: `~/Projects/belaguru-bhajans/static/app.js` (getDailyBhajan, renderDailyBhajanBanner)
- **Styling**: Banner CSS in app.js template
- **Data**: Day tags in `data/bhajans.json` and tag taxonomy

## Success Criteria
All 16 tests passing indicates:
- ✅ Daily bhajan feature fully functional
- ✅ All days of week covered
- ✅ Navigation working
- ✅ Tags properly applied
- ✅ UI displaying correctly
- ✅ Fallback mechanism working
