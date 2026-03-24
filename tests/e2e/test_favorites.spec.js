/**
 * Test Suite: Favorites Feature
 * Tests for localStorage-based favorites functionality
 */
const { test, expect } = require('@playwright/test');

// Helper to wait for app to finish loading
async function waitForAppLoaded(page) {
    await page.waitForSelector('#app[data-loaded="true"]', { timeout: 15000 });
}

test.describe('Favorites Functions', () => {
    test('getFavorites function exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasFn = await page.evaluate(() => typeof window.app?.getFavorites === 'function');
        expect(hasFn).toBe(true);
    });

    test('saveFavorites function exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasFn = await page.evaluate(() => typeof window.app?.saveFavorites === 'function');
        expect(hasFn).toBe(true);
    });

    test('toggleFavorite function exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasFn = await page.evaluate(() => typeof window.app?.toggleFavorite === 'function');
        expect(hasFn).toBe(true);
    });

    test('isFavorited function exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasFn = await page.evaluate(() => typeof window.app?.isFavorited === 'function');
        expect(hasFn).toBe(true);
    });
});

test.describe('Favorites LocalStorage', () => {
    test('favorites stored in localStorage', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        // Set favorites via app
        await page.evaluate(() => {
            window.app.saveFavorites([1, 2, 3]);
        });
        
        // Read from localStorage
        const stored = await page.evaluate(() => {
            return localStorage.getItem('bhajan_favorites');
        });
        
        expect(stored).toBe('[1,2,3]');
    });

    test('favorites persist after reload', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        // Set favorites
        await page.evaluate(() => {
            localStorage.setItem('bhajan_favorites', '[5,10,15]');
        });
        
        // Reload
        await page.reload();
        await waitForAppLoaded(page);
        
        // Check persistence
        const favorites = await page.evaluate(() => {
            return window.app.getFavorites();
        });
        
        expect(favorites).toContain(5);
        expect(favorites).toContain(10);
        expect(favorites).toContain(15);
    });

    test('can add favorite', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        // Clear and add
        await page.evaluate(() => {
            localStorage.removeItem('bhajan_favorites');
            window.app.toggleFavorite(42, 'Test');
        });
        
        const favorites = await page.evaluate(() => window.app.getFavorites());
        expect(favorites).toContain(42);
    });

    test('can remove favorite', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        // Set then toggle off
        await page.evaluate(() => {
            localStorage.setItem('bhajan_favorites', '[100]');
        });
        await page.reload();
        await waitForAppLoaded(page);
        
        await page.evaluate(() => {
            window.app.toggleFavorite(100, 'Test');
        });
        
        const favorites = await page.evaluate(() => window.app.getFavorites());
        expect(favorites).not.toContain(100);
    });
});

test.describe('Favorites Page', () => {
    test('renderFavorites function exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasFn = await page.evaluate(() => typeof window.app?.renderFavorites === 'function');
        expect(hasFn).toBe(true);
    });

    test('favorites page accessible via hash', async ({ page }) => {
        await page.goto('/#favorites');
        await waitForAppLoaded(page);
        
        // Should show favorites content
        const content = await page.locator('#app').innerHTML();
        expect(content.toLowerCase()).toContain('favorite');
    });
});
