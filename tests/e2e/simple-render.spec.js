const { test, expect } = require('@playwright/test');

test('page loads and app renders', async ({ page }) => {
    // Set a longer timeout for this test
    test.setTimeout(90000);
    
    // Navigate with longer timeout
    await page.goto('http://localhost:8001', { timeout: 30000 });
    
    // Wait for DOM to be ready (faster than networkidle)
    await page.waitForLoadState('domcontentloaded');
    
    // Check if app container exists
    const appDiv = page.locator('#app');
    await expect(appDiv).toBeAttached({ timeout: 10000 });
    
    // Verify app has content (any child element)
    await expect(appDiv).not.toBeEmpty({ timeout: 10000 });
    
    // Check page title element exists
    const titleElement = page.locator('h1, .text-2xl, [class*="title"]').first();
    await expect(titleElement).toBeAttached({ timeout: 10000 });
});
