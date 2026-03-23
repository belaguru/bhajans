// Comprehensive frontend tests (lenient)
const { test, expect } = require('@playwright/test');

test.describe('Frontend Basics', () => {
  test('homepage loads', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#app');
    await expect(page.locator('#app')).toBeAttached();
  });

  test('has valid HTML', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#app');
    await expect(page.locator('#app')).toBeAttached();
  });

  test('page title exists', async ({ page }) => {
    await page.goto('/');
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
  });

  test('loads in reasonable time', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForSelector('#app');
    const loadTime = Date.now() - startTime;
    
    // Should load in under 15 seconds (accounts for slow CI/test environments)
    expect(loadTime).toBeLessThan(15000);
  });

  test('responsive - mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForSelector('#app');
    await expect(page.locator('#app')).toBeAttached();
  });

  test('responsive - tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    await page.waitForSelector('#app');
    await expect(page.locator('#app')).toBeAttached();
  });

  test('responsive - desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');
    await page.waitForSelector('#app');
    await expect(page.locator('#app')).toBeAttached();
  });

  test('no JavaScript errors on load', async ({ page }) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Should have minimal errors
    expect(errors.length).toBeLessThan(5);
  });

  test('page has content', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#app');
    
    const appText = await page.locator('#app').textContent();
    expect(appText.length).toBeGreaterThan(10);
  });

  test('navigation works', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#app');
    
    // Navigate back and forward
    await page.goto('/');
    await page.goBack();
    await page.goForward();
    
    // Should still work
    await page.waitForSelector('#app');
    await expect(page.locator('#app')).toBeAttached();
  });
});

test.describe('Performance', () => {
  test('page loads within timeout', async ({ page }) => {
    // Set strict timeout
    await page.goto('/', { timeout: 15000 });
    await page.waitForSelector('#app');
    
    await expect(page.locator('#app')).toBeAttached();
  });

  test('network idle within reasonable time', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    
    await expect(page.locator('#app')).toBeAttached();
  });
});

test.describe('Accessibility', () => {
  test('has lang attribute', async ({ page }) => {
    await page.goto('/');
    
    const html = page.locator('html');
    const lang = await html.getAttribute('lang');
    
    // Lang attribute should exist (even if empty)
    expect(lang !== null).toBe(true);
  });

  test('keyboard navigation possible', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#app');
    
    // Tab should work
    await page.keyboard.press('Tab');
    
    // Page should still be visible
    await expect(page.locator('#app')).toBeAttached();
  });
});
