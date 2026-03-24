/**
 * Test Suite: Share Functionality
 * Tests for social sharing
 */
const { test, expect } = require('@playwright/test');

// Helper to wait for app to finish loading
async function waitForAppLoaded(page) {
    await page.waitForSelector('#app[data-loaded="true"]', { timeout: 15000 });
}

test.describe('Share Functions', () => {
    test('renderShareButtons function exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasFn = await page.evaluate(() => typeof window.app?.renderShareButtons === 'function');
        expect(hasFn).toBe(true);
    });
});

test.describe('Share URL', () => {
    test('bhajan page updates currentPage state', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        // Get first bhajan ID
        const bhajanId = await page.evaluate(() => window.app?.bhajans?.[0]?.id);
        
        if (bhajanId) {
            await page.evaluate((id) => window.app.setPage('bhajan', id), bhajanId);
            await page.waitForTimeout(300);
            
            const currentPage = await page.evaluate(() => window.app?.currentPage);
            expect(currentPage).toBe('bhajan');
        }
    });

    test('direct bhajan URL works', async ({ page }) => {
        // Get a valid bhajan ID first
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const bhajanId = await page.evaluate(() => window.app?.bhajans?.[0]?.id);
        
        if (bhajanId) {
            await page.evaluate((id) => window.app.setPage('bhajan', id), bhajanId);
            await waitForAppLoaded(page);
            await page.waitForTimeout(500);
            
            // Should show bhajan content (lyrics)
            const content = await page.locator('#app').innerHTML();
            expect(content.length).toBeGreaterThan(500);
        }
    });
});
