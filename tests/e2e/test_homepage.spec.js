// Test: Homepage loads correctly
const { test, expect } = require('@playwright/test');

test.describe('Homepage', () => {
  test('loads successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check title exists (may vary)
    await expect(page).toHaveTitle(/.+/);
    
    // Wait for app container instead of body (body might have CSS hiding it)
    await page.waitForSelector('#app');
    const app = page.locator('#app');
    await expect(app).toBeAttached();
  });

  test('shows content', async ({ page }) => {
    await page.goto('/');
    
    // Wait for content to load
    await page.waitForLoadState('networkidle');
    
    // Check if app has any text
    const appText = await page.locator('#app').textContent();
    expect(appText.length).toBeGreaterThan(0);
  });

  test('has basic structure', async ({ page }) => {
    await page.goto('/');
    
    // Check app container exists and is attached
    await page.waitForSelector('#app');
    const app = page.locator('#app');
    await expect(app).toBeAttached();
  });
});
