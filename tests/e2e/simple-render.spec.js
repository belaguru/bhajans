const { test, expect } = require('@playwright/test');

test('page loads and app renders', async ({ page }) => {
    // Set a longer timeout
    test.setTimeout(60000);
    
    await page.goto('http://localhost:8001');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check if app container exists
    const appDiv = page.locator('#app');
    await expect(appDiv).toBeAttached();
    
    // Wait for app to render content
    await page.waitForTimeout(2000);
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/homepage.png', fullPage: true });
    
    // Check for any JavaScript errors
    const consoleMessages = [];
    page.on('console', msg => {
        consoleMessages.push(`${msg.type()}: ${msg.text()}`);
    });
    
    // Wait a bit more
    await page.waitForTimeout(2000);
    
    console.log("Console messages:", consoleMessages);
    
    // Check if title is present
    const title = await page.textContent('h1');
    console.log("Page title:", title);
});
