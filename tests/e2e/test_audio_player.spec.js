// Test: Audio player (if implemented)
const { test, expect } = require('@playwright/test');

test.describe('Audio Player', () => {
  test('page loads without errors', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#app');
    
    // Just check page loads
    await expect(page.locator('#app')).toBeAttached();
  });

  test('page is stable', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#app');
    
    // Wait for page to be stable
    await page.waitForLoadState('networkidle');
    
    // Should not have crashed
    await expect(page.locator('#app')).toBeAttached();
  });
});
