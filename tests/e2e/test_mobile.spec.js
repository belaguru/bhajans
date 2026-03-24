/**
 * Test Suite: Mobile UI
 * Tests for mobile-specific functionality
 */
const { test, expect } = require('@playwright/test');

// Helper to wait for app to finish loading
async function waitForAppLoaded(page) {
    await page.waitForSelector('#app[data-loaded="true"]', { timeout: 15000 });
}

test.describe('Mobile Layout', () => {
    test.beforeEach(async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
    });

    test('page loads on mobile', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const app = page.locator('#app');
        await expect(app).toBeVisible();
    });

    test('app is responsive on mobile', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const app = page.locator('#app');
        const box = await app.boundingBox();
        
        // App should fit mobile width
        expect(box.width).toBeLessThanOrEqual(375);
    });

    test('floating menu visible on mobile', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const menuBtn = page.locator('#floating-menu-button');
        await expect(menuBtn).toBeVisible();
    });
});

test.describe('Mobile Tag Filter', () => {
    test.beforeEach(async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
    });

    test('mobile has filter UI', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        // Check for tag-related elements
        const content = await page.locator('#app').innerHTML();
        const hasTagUI = content.toLowerCase().includes('filter') || 
                         content.toLowerCase().includes('tag') ||
                         content.toLowerCase().includes('▼');
        expect(hasTagUI).toBe(true);
    });

    test('mobileTagsOpen state exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasState = await page.evaluate(() => 
            typeof window.app?.mobileTagsOpen !== 'undefined'
        );
        expect(hasState).toBe(true);
    });
});

test.describe('Mobile Search', () => {
    test.beforeEach(async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
    });

    test('search input visible on mobile', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const searchInputs = page.locator('input[placeholder*="Search"]');
        const count = await searchInputs.count();
        expect(count).toBeGreaterThanOrEqual(1);
    });

    test('can type in search on mobile', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const searchInput = page.locator('input[placeholder*="Search"]').first();
        await searchInput.fill('test');
        
        const value = await searchInput.inputValue();
        expect(value).toBe('test');
    });
});

test.describe('Mobile Bhajan View', () => {
    test.beforeEach(async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
    });

    test('bhajan detail loads on mobile', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const bhajanId = await page.evaluate(() => window.app?.bhajans?.[0]?.id);
        
        if (bhajanId) {
            await page.evaluate((id) => window.app.setPage('bhajan', id), bhajanId);
            await page.waitForTimeout(500);
            
            const content = await page.locator('#app').innerHTML();
            expect(content.length).toBeGreaterThan(500);
        }
    });

    test('back navigation works on mobile', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const bhajanId = await page.evaluate(() => window.app?.bhajans?.[0]?.id);
        
        if (bhajanId) {
            await page.evaluate((id) => window.app.setPage('bhajan', id), bhajanId);
            await page.waitForTimeout(300);
            
            // Navigate home
            await page.evaluate(() => window.app.setPage('home'));
            await page.waitForTimeout(300);
            
            const currentPage = await page.evaluate(() => window.app?.currentPage);
            expect(currentPage).toBe('home');
        }
    });
});
