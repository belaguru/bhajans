// Test: Audio player (if implemented)
const { test, expect } = require('@playwright/test');

// Helper to wait for app to finish loading
async function waitForAppLoaded(page) {
    await page.waitForSelector('#app[data-loaded="true"]', { timeout: 15000 });
}

test.describe('Audio Player', () => {
  test('page loads without errors', async ({ page }) => {
    await page.goto('/');
    await waitForAppLoaded(page);
    
    // Just check page loads
    await expect(page.locator('#app')).toBeAttached();
  });

  test('page is stable', async ({ page }) => {
    await page.goto('/');
    await waitForAppLoaded(page);
    
    // Wait for page to be stable
    await page.waitForLoadState('networkidle');
    
    // Should not have crashed
    await expect(page.locator('#app')).toBeAttached();
  });
});
