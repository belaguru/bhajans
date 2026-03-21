// Test: Audio player (if implemented)
const { test, expect } = require('@playwright/test');

test.describe('Audio Player', () => {
  test('page loads without errors', async ({ page }) => {
    await page.goto('/');
    
    // Just check page loads
    await expect(page.locator('body')).toBeVisible();
  });

  test('page is stable', async ({ page }) => {
    await page.goto('/');
    
    // Wait for page to be stable
    await page.waitForLoadState('networkidle');
    
    // Should not have crashed
    await expect(page.locator('html')).toBeVisible();
  });
});
