/**
 * Test Suite: Navigation & URL Routing
 * Tests for page navigation
 */
const { test, expect } = require('@playwright/test');

// Helper to wait for app to finish loading
async function waitForAppLoaded(page) {
    await page.waitForSelector('#app[data-loaded="true"]', { timeout: 15000 });
}

test.describe('Page Navigation', () => {
    test('root URL loads homepage', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const currentPage = await page.evaluate(() => window.app?.currentPage);
        expect(currentPage).toBe('home');
    });

    test('can navigate to upload via setPage', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        await page.evaluate(() => window.app.setPage('upload'));
        await page.waitForTimeout(300);
        
        const content = await page.locator('#app').innerHTML();
        expect(content.toLowerCase()).toMatch(/upload|add/);
    });

    test('can navigate to favorites via setPage', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        await page.evaluate(() => window.app.setPage('favorites'));
        await page.waitForTimeout(300);
        
        const content = await page.locator('#app').innerHTML();
        expect(content.toLowerCase()).toContain('favorite');
    });

    test('settings handled in setPage', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        // Check if settings is handled in setPage by checking source
        const appSource = await page.evaluate(() => window.app.setPage.toString());
        expect(appSource).toContain('settings');
    });
});

test.describe('Navigation Functions', () => {
    test('setPage function exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasFn = await page.evaluate(() => typeof window.app?.setPage === 'function');
        expect(hasFn).toBe(true);
    });

    test('loadFromURL function exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasFn = await page.evaluate(() => typeof window.app?.loadFromURL === 'function');
        expect(hasFn).toBe(true);
    });

    test('initURLListener function exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasFn = await page.evaluate(() => typeof window.app?.initURLListener === 'function');
        expect(hasFn).toBe(true);
    });
});

test.describe('Multi-Page Navigation', () => {
    test('setPage navigates between pages', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        // Navigate to upload
        await page.evaluate(() => window.app.setPage('upload'));
        await page.waitForTimeout(300);
        expect(await page.evaluate(() => window.app?.currentPage)).toBe('upload');
        
        // Navigate to favorites
        await page.evaluate(() => window.app.setPage('favorites'));
        await page.waitForTimeout(300);
        expect(await page.evaluate(() => window.app?.currentPage)).toBe('favorites');
        
        // Navigate home
        await page.evaluate(() => window.app.setPage('home'));
        await page.waitForTimeout(300);
        expect(await page.evaluate(() => window.app?.currentPage)).toBe('home');
    });
});
