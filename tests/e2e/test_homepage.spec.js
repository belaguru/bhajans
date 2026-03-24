// Test: Homepage loads correctly
const { test, expect } = require('@playwright/test');

// Helper to wait for app to finish loading
async function waitForAppLoaded(page) {
    await page.waitForSelector('#app[data-loaded="true"]', { timeout: 15000 });
}

test.describe('Homepage', () => {
  test('loads successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check title exists (may vary)
    await expect(page).toHaveTitle(/.+/);
    
    // Wait for app to finish loading
    await waitForAppLoaded(page);
    const app = page.locator('#app');
    await expect(app).toBeAttached();
  });

  test('shows content', async ({ page }) => {
    await page.goto('/');
    
    // Wait for app to finish loading
    await waitForAppLoaded(page);
    
    // Check if app has any text
    const appText = await page.locator('#app').textContent();
    expect(appText.length).toBeGreaterThan(0);
  });

  test('has basic structure', async ({ page }) => {
    await page.goto('/');
    
    // Wait for app to finish loading
    await waitForAppLoaded(page);
    const app = page.locator('#app');
    await expect(app).toBeAttached();
  });
});
