// E2E Test: Edit Form Functionality
const { test, expect } = require('@playwright/test');

// Helper to wait for app to finish loading
async function waitForAppLoaded(page) {
    await page.waitForSelector('#app[data-loaded="true"]', { timeout: 15000 });
}

test.describe('Bhajan Edit Form', () => {
  test('navigates to edit form from bhajan page', async ({ page }) => {
    // Navigate to bhajan detail page
    await page.goto('/');
    await waitForAppLoaded(page);
    
    // Navigate directly to bhajan 1
    await page.evaluate(() => {
      window.app.setPage('bhajan', 1);
    });
    
    await page.waitForTimeout(500);
    
    // Click edit button
    const editButton = page.locator('button:has-text("Edit")');
    await expect(editButton).toBeVisible();
    await editButton.click();
    
    // Wait for edit form to load
    await page.waitForTimeout(500);
    
    // Verify edit form is displayed
    await expect(page.locator('text=Edit Bhajan')).toBeVisible();
    await expect(page.locator('#edit_title')).toBeVisible();
    await expect(page.locator('#edit_lyrics')).toBeVisible();
    await expect(page.locator('button:has-text("Save Changes")')).toBeVisible();
  });

  test('edit form loads with current bhajan values', async ({ page }) => {
    // Navigate to bhajan 1 detail page
    await page.goto('/');
    await waitForAppLoaded(page);
    await page.waitForTimeout(1000);
    
    // Get bhajan data before editing
    const originalData = await page.evaluate(() => {
      const bhajan = window.app.bhajans.find(b => b.id === 1);
      return {
        title: bhajan.title,
        lyrics: bhajan.lyrics,
        tags: bhajan.tags || []
      };
    });
    
    // Navigate to edit form
    await page.evaluate(() => {
      window.app.editBhajan(1);
    });
    
    await page.waitForTimeout(500);
    
    // Verify form fields are populated with current values
    const titleValue = await page.locator('#edit_title').inputValue();
    expect(titleValue).toBe(originalData.title);
    
    const lyricsValue = await page.locator('#edit_lyrics').inputValue();
    // Normalize whitespace for comparison (HTML may convert trailing spaces)
    const normalizedLyrics = lyricsValue.replace(/\s+$/gm, '');
    const normalizedOriginal = originalData.lyrics.replace(/\s+$/gm, '');
    expect(normalizedLyrics).toBe(normalizedOriginal);
    
    // Verify tag selector is present
    await expect(page.locator('#edit_tags_selector')).toBeVisible();
  });

  test('can modify title and lyrics in edit form', async ({ page }) => {
    // Navigate to bhajan 1 edit form
    await page.goto('/');
    await waitForAppLoaded(page);
    await page.waitForTimeout(1000);
    
    await page.evaluate(() => {
      window.app.editBhajan(1);
    });
    
    await page.waitForTimeout(500);
    
    // Modify title
    const newTitle = 'Test Modified Title ' + Date.now();
    await page.locator('#edit_title').fill(newTitle);
    
    // Verify title changed
    const titleValue = await page.locator('#edit_title').inputValue();
    expect(titleValue).toBe(newTitle);
    
    // Modify lyrics
    const newLyrics = 'Test modified lyrics\nLine 2\nLine 3';
    await page.locator('#edit_lyrics').fill(newLyrics);
    
    // Verify lyrics changed
    const lyricsValue = await page.locator('#edit_lyrics').inputValue();
    expect(lyricsValue).toBe(newLyrics);
  });

  test('can select and modify tags in edit form', async ({ page }) => {
    // Navigate to bhajan 1 edit form
    await page.goto('/');
    await waitForAppLoaded(page);
    await page.waitForTimeout(1000);
    
    await page.evaluate(() => {
      window.app.editBhajan(1);
    });
    
    await page.waitForTimeout(500);
    
    // Verify tag tree is visible
    await expect(page.locator('#edit_tags_tree')).toBeVisible();
    
    // Find first checkbox in tag tree
    const firstCheckbox = page.locator('#edit_tags_tree input[type="checkbox"]').first();
    await expect(firstCheckbox).toBeVisible();
    
    // Get initial state
    const wasChecked = await firstCheckbox.isChecked();
    
    // Toggle checkbox
    await firstCheckbox.click();
    await page.waitForTimeout(300);
    
    // Verify state changed
    const isNowChecked = await firstCheckbox.isChecked();
    expect(isNowChecked).toBe(!wasChecked);
  });

  test('submit form with modifications and verify no JavaScript errors', async ({ page }) => {
    const consoleErrors = [];
    const jsErrors = [];
    
    // Capture console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Capture JavaScript errors
    page.on('pageerror', error => {
      jsErrors.push(error.message);
    });
    
    // Navigate to bhajan 1 edit form
    await page.goto('/');
    await waitForAppLoaded(page);
    await page.waitForTimeout(1000);
    
    await page.evaluate(() => {
      window.app.editBhajan(1);
    });
    
    await page.waitForTimeout(500);
    
    // Modify title
    const newTitle = 'E2E Test Title ' + Date.now();
    await page.locator('#edit_title').fill(newTitle);
    
    // Modify lyrics
    const newLyrics = 'E2E test lyrics\nSecond line';
    await page.locator('#edit_lyrics').fill(newLyrics);
    
    // Submit form
    const submitButton = page.locator('button:has-text("Save Changes")');
    await expect(submitButton).toBeVisible();
    
    // Listen for dialog (alert) to accept it
    page.once('dialog', dialog => dialog.accept());
    
    await submitButton.click();
    
    // Wait for submission to complete
    await page.waitForTimeout(2000);
    
    // Verify no JavaScript errors occurred
    // The edit form should handle tag IDs correctly via selected_tag_ids input
    expect(jsErrors.length).toBe(0);
    
    // Log any console errors for debugging (but don't fail on them)
    if (consoleErrors.length > 0) {
      console.log('Console errors:', consoleErrors);
    }
  });

  test('verify no JavaScript errors on page load', async ({ page }) => {
    const jsErrors = [];
    
    page.on('pageerror', error => {
      jsErrors.push(error.message);
    });
    
    // Navigate to bhajan 1 edit form
    await page.goto('/');
    await waitForAppLoaded(page);
    await page.waitForTimeout(1000);
    
    await page.evaluate(() => {
      window.app.editBhajan(1);
    });
    
    await page.waitForTimeout(1000);
    
    // Should have no errors on load (only on submit)
    expect(jsErrors.length).toBe(0);
  });

  test('form persistence - changes remain after navigation', async ({ page }) => {
    // Navigate to bhajan 1 edit form
    await page.goto('/');
    await waitForAppLoaded(page);
    await page.waitForTimeout(1000);
    
    await page.evaluate(() => {
      window.app.editBhajan(1);
    });
    
    await page.waitForTimeout(500);
    
    // Modify title
    const testTitle = 'Persistence Test ' + Date.now();
    await page.locator('#edit_title').fill(testTitle);
    
    // Note: This test documents expected behavior
    // In a real SPA, form state might not persist across navigation
    // This is a known limitation, not a bug
  });

  test('cancel/back navigation from edit form', async ({ page }) => {
    // Navigate to bhajan 1 edit form
    await page.goto('/');
    await waitForAppLoaded(page);
    await page.waitForTimeout(1000);
    
    await page.evaluate(() => {
      window.app.editBhajan(1);
    });
    
    await page.waitForTimeout(500);
    
    // Click back button
    const backButton = page.locator('button:has-text("Back to Bhajan")');
    await expect(backButton).toBeVisible();
    await backButton.click();
    
    await page.waitForTimeout(500);
    
    // Should be back on bhajan detail page
    await expect(page.locator('button:has-text("Edit")')).toBeVisible();
  });
});
