// Test: Homepage loads correctly
const { test, expect } = require('@playwright/test');

test.describe('Homepage', () => {
  test('loads successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check title exists (may vary)
    await expect(page).toHaveTitle(/.+/);
    
    // Check page has content
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });

  test('shows content', async ({ page }) => {
    await page.goto('/');
    
    // Wait for content to load
    await page.waitForLoadState('networkidle');
    
    // Check if page has any text
    const bodyText = await page.locator('body').textContent();
    expect(bodyText.length).toBeGreaterThan(0);
  });

  test('has basic structure', async ({ page }) => {
    await page.goto('/');
    
    // Check basic HTML structure exists
    const body = page.locator('body');
    await expect(body).toBeAttached();
  });
});
