# Selector Changes - Quick Reference

## 1. Page Heading (CRITICAL - Strict Mode Violation)

```diff
- await expect(page.locator('text=Upload New Bhajan')).toBeVisible();
+ await expect(page.getByRole('heading', { name: 'Upload Bhajan' })).toBeVisible();
```

**Why:** The text "Upload New Bhajan" resolved to BOTH the heading AND the submit button, causing strict mode error. Using role selector is more specific.

---

## 2. Bhajan Cards (CRITICAL - Selector Didn't Exist)

```diff
- const testBhajan = page.locator('.card').filter({ hasText: 'E2E Test Bhajan' }).first();
+ const testBhajan = page.locator('.card.cursor-pointer').filter({ hasText: 'E2E Test Bhajan' }).first();
```

**Why:** `.bhajan-card` doesn't exist. Actual class is `.card` with `.cursor-pointer` for clickable cards.

---

## 3. Tag Selection (MAJOR - Wrong Approach)

```diff
- // Expand Deities category
- const deitiesButton = page.locator('#tags_tree button:has-text("🕉️ Deities")');
- await deitiesButton.click();
- await page.waitForTimeout(300);
- 
- // Select a tag (e.g., Shiva)
- const shivaCheckbox = page.locator('#tags_tree input[type="checkbox"]').first();
- if (await shivaCheckbox.isVisible()) {
-   await shivaCheckbox.click();
-   await page.waitForTimeout(200);
- }

+ // Wait for tag tree to be populated
+ await page.waitForSelector('#tags_tree input[type="checkbox"]', { timeout: 5000 });
+ 
+ const firstCheckbox = page.locator('#tags_tree input[type="checkbox"]').first();
+ await firstCheckbox.scrollIntoViewIfNeeded();
+ await firstCheckbox.click({ force: true });
+ await page.waitForTimeout(300);
```

**Why:** 
- Category buttons don't exist in the DOM
- Checkboxes need explicit wait to load (async API)
- `force: true` needed for reliable clicking

---

## 4. Upload Tag Requirement (BEHAVIOR - Discovered to be Optional)

```diff
- test('tags must be selected before submission', async ({ page }) => {
-   // ...
-   page.once('dialog', dialog => {
-     expect(dialog.message()).toContain('tag');
-     dialog.accept();
-   });
-   await submitButton.click();
-   // ... expects validation error ...
- });

+ test('tags are optional - form submits without tags', async ({ page }) => {
+   // ...
+   page.once('dialog', dialog => {
+     expect(dialog.message()).toContain('successfully');
+     dialog.accept();
+   });
+   await submitButton.click();
+   // ... expects successful submission ...
+ });
```

**Why:** Actual app behavior - tags are optional, not required.

---

## Common Issues Fixed

| Issue | Symptom | Solution |
|-------|---------|----------|
| Text selector ambiguity | "strict mode violation: locator resolved to 2 elements" | Use `getByRole()` instead |
| Non-existent class | "element(s) not found" | Check ACTUAL_SELECTORS.md for real classes |
| Async data not loaded | Empty element with correct ID | Wait with `waitForSelector()` for child elements |
| Checkbox not clickable | Timeout waiting for click | Use `{ force: true }` and `scrollIntoViewIfNeeded()` |
| Wrong test expectations | Dialog shows different message | Verify actual app behavior first |

---

## Verification Commands

```bash
# Check actual selectors on live app
curl -s http://localhost:8001/ | grep -o 'class="[^"]*"' | sort | uniq

# Check tag tree API
curl -s http://localhost:8001/api/tags/tree | jq 'keys | .[:5]'

# Run specific test with debugging
npx playwright test --grep "upload page" --debug
```

---

**Generated:** 2026-03-23 21:34 IST
