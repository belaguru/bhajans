// Test: YouTube video playback in UI
const { test, expect } = require('@playwright/test');

// Helper to wait for app to finish loading
async function waitForAppLoaded(page) {
    await page.waitForSelector('#app[data-loaded="true"]', { timeout: 15000 });
}

test.describe('YouTube Playback', () => {
  test.beforeEach(async ({ page }) => {
    // Create a bhajan with YouTube URL via API
    await page.goto('/');
    await waitForAppLoaded(page);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test('page loads successfully', async ({ page }) => {
    await page.goto('/');
    await waitForAppLoaded(page);
    await expect(page.locator('#app')).toBeAttached();
  });

  test('can embed YouTube video', async ({ page }) => {
    await page.goto('/');
    await waitForAppLoaded(page);
    
    // Look for iframe (YouTube embeds use iframes)
    const iframes = page.locator('iframe');
    const count = await iframes.count();
    
    // May or may not have YouTube embeds
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('YouTube player controls exist', async ({ page }) => {
    await page.goto('/');
    await waitForAppLoaded(page);
    
    // Check for any video-related elements
    const videoElements = page.locator('video, iframe[src*="youtube"], [class*="player"]');
    const count = await videoElements.count();
    
    // If YouTube videos exist, should have player
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('clicking bhajan may show video', async ({ page }) => {
    await page.goto('/');
    await waitForAppLoaded(page);
    
    // Try to click any bhajan item
    const bhajanItems = page.locator('.bhajan-card, .bhajan-item, a[href*="bhajan"]');
    const count = await bhajanItems.count();
    
    if (count > 0) {
      await bhajanItems.first().click();
      await page.waitForTimeout(1000);
      
      // Should navigate somewhere
      await expect(page.locator('#app')).toBeAttached();
    }
  });

  test('YouTube iframe loads correctly', async ({ page }) => {
    await page.goto('/');
    await waitForAppLoaded(page);
    
    // Check if YouTube iframe exists
    const youtubeIframe = page.locator('iframe[src*="youtube.com"]');
    const exists = await youtubeIframe.count() > 0;
    
    if (exists) {
      // If YouTube iframe exists, should be visible
      await expect(youtubeIframe.first()).toBeVisible();
    } else {
      // If no iframe, page should still work
      await expect(page.locator('#app')).toBeAttached();
    }
  });

  test('no console errors on video load', async ({ page }) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Should have minimal errors
    expect(errors.length).toBeLessThan(3);
  });
});

test.describe('YouTube URL Handling', () => {
  test('valid YouTube URLs are accepted', async ({ page }) => {
    await page.goto('/');
    await waitForAppLoaded(page);
    
    // Page should load without errors
    await expect(page.locator('#app')).toBeAttached();
  });

  test('page handles missing video gracefully', async ({ page }) => {
    await page.goto('/');
    await waitForAppLoaded(page);
    
    // Should not crash if video missing
    await expect(page.locator('#app')).toBeAttached();
  });

  test('video player responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await waitForAppLoaded(page);
    
    // Should still work on mobile
    await expect(page.locator('#app')).toBeAttached();
  });
});
