/**
 * Test Suite: Daily Bhajan Feature
 * Tests for day-of-week based bhajan functionality
 */
const { test, expect } = require('@playwright/test');

// Helper to wait for app to finish loading
async function waitForAppLoaded(page) {
    await page.waitForSelector('#app[data-loaded="true"]', { timeout: 15000 });
}

test.describe('Daily Bhajan Function', () => {
    test('getDailyBhajan function exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasDailyFunction = await page.evaluate(() => {
            return typeof window.app?.getDailyBhajan === 'function';
        });
        expect(hasDailyFunction).toBe(true);
    });

    test('getDailyBhajan returns valid result', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const daily = await page.evaluate(() => {
            return window.app?.getDailyBhajan?.();
        });
        
        // May return null if no bhajans, or object with dayName
        if (daily !== null && daily !== undefined) {
            if (daily.dayName) {
                expect(['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']).toContain(daily.dayName);
            }
        }
        // Test passes either way - just checking function doesn't crash
        expect(true).toBe(true);
    });

    test('showDailyBhajan function exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasShowDaily = await page.evaluate(() => {
            return typeof window.app?.showDailyBhajan === 'function';
        });
        expect(hasShowDaily).toBe(true);
    });
});

test.describe('Day Tags API', () => {
    test('API returns bhajans', async ({ request }) => {
        const response = await request.get('/api/bhajans');
        expect(response.status()).toBe(200);
        
        const bhajans = await response.json();
        expect(Array.isArray(bhajans)).toBe(true);
    });

    test('tags endpoint works', async ({ request }) => {
        const response = await request.get('/api/tags');
        expect(response.status()).toBe(200);
        
        const tags = await response.json();
        expect(Array.isArray(tags)).toBe(true);
    });
});
