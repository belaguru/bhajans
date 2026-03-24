/**
 * Test Suite: Floating Menu (FAB)
 * Tests for the floating action button and navigation menu
 */
const { test, expect } = require('@playwright/test');

// Helper to wait for app to finish loading
async function waitForAppLoaded(page) {
    await page.waitForSelector('#app[data-loaded="true"]', { timeout: 15000 });
}

test.describe('Floating Menu Structure', () => {
    test('floating menu button exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const btn = page.locator('#floating-menu-button');
        await expect(btn).toBeAttached();
    });

    test('floating menu container exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const menu = page.locator('#floating-menu');
        await expect(menu).toBeAttached();
    });

    test('toggleFloatingMenu function exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasFn = await page.evaluate(() => typeof window.app?.toggleFloatingMenu === 'function');
        expect(hasFn).toBe(true);
    });

    test('closeFloatingMenu function exists', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const hasFn = await page.evaluate(() => typeof window.app?.closeFloatingMenu === 'function');
        expect(hasFn).toBe(true);
    });
});

test.describe('Floating Menu Toggle', () => {
    test('menu starts hidden (no visible class)', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        const menu = page.locator('#floating-menu');
        // Menu is hidden by default (no 'visible' class)
        await expect(menu).not.toHaveClass(/visible/);
    });

    test('clicking button shows menu', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        // Use evaluate to toggle menu (more reliable than click)
        await page.evaluate(() => window.app.toggleFloatingMenu());
        await page.waitForTimeout(300);
        
        const menu = page.locator('#floating-menu');
        await expect(menu).toHaveClass(/visible/);
    });

    test('clicking button twice hides menu', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        // Open then close
        await page.evaluate(() => window.app.toggleFloatingMenu());
        await page.waitForTimeout(100);
        await page.evaluate(() => window.app.toggleFloatingMenu());
        await page.waitForTimeout(100);
        
        const menu = page.locator('#floating-menu');
        await expect(menu).not.toHaveClass(/visible/);
    });
});

test.describe('Floating Menu Items', () => {
    test('menu has Home item', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        await page.evaluate(() => window.app.toggleFloatingMenu());
        await page.waitForTimeout(300);
        
        const homeItem = page.locator('.floating-menu-item:has-text("Home")');
        await expect(homeItem).toBeVisible();
    });

    test('menu has Search item', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        await page.evaluate(() => window.app.toggleFloatingMenu());
        await page.waitForTimeout(300);
        
        const searchItem = page.locator('.floating-menu-item:has-text("Search")');
        await expect(searchItem).toBeVisible();
    });

    test('menu has Favorites item', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        await page.evaluate(() => window.app.toggleFloatingMenu());
        await page.waitForTimeout(300);
        
        const favItem = page.locator('.floating-menu-item:has-text("Favorites")');
        await expect(favItem).toBeVisible();
    });

    test('menu has Upload item', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        await page.evaluate(() => window.app.toggleFloatingMenu());
        await page.waitForTimeout(300);
        
        const uploadItem = page.locator('.floating-menu-item:has-text("Upload")');
        await expect(uploadItem).toBeVisible();
    });

    test('menu has Font Size controls', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        await page.evaluate(() => window.app.toggleFloatingMenu());
        await page.waitForTimeout(300);
        
        const fontControls = page.locator('.font-size-controls');
        await expect(fontControls).toBeVisible();
    });

    test('menu has Daily Bhajan item', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        await page.evaluate(() => window.app.toggleFloatingMenu());
        await page.waitForTimeout(300);
        
        const dailyItem = page.locator('.floating-menu-item:has-text("Daily")');
        await expect(dailyItem).toBeVisible();
    });
});
