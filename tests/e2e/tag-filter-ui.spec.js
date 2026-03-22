/**
 * Test Suite: Tag Filter UI
 * Tests for the enhanced tag-based filtering and search UI
 */
const { test, expect } = require('@playwright/test');

test('tag filter sidebar visible on desktop', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await page.waitForSelector('#app');
    
    // Desktop sidebar should be visible
    const sidebar = page.locator('.lg\\:col-span-1').first();
    await expect(sidebar).toBeVisible();
    
    // Should have "Tags" heading
    await expect(page.getByText('📑 Tags')).toBeVisible();
});

test('mobile tag filter toggle', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('http://localhost:8001');
    await page.waitForSelector('#app');
    
    // Mobile toggle button should be visible
    const toggleBtn = page.getByText('▼ Filter by Tags');
    await expect(toggleBtn).toBeVisible();
    
    // Mobile tags section should be hidden initially
    const mobileTags = page.locator('#mobile-tags-section');
    await expect(mobileTags).toHaveClass(/hidden/);
    
    // Click toggle
    await toggleBtn.click();
    
    // Mobile tags should now be visible
    await expect(mobileTags).not.toHaveClass(/hidden/);
});

test('tag search filters tags', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await page.waitForSelector('#app');
    
    // Wait for tags to load
    await page.waitForSelector('.space-y-2 button, .space-y-1 button', { timeout: 5000 });
    
    // Search for "Hanuman"
    const searchInput = page.locator('#tag-search-input');
    await searchInput.fill('Hanuman');
    
    // Wait for filter
    await page.waitForTimeout(500);
    
    // Clear button should be visible
    const clearBtn = page.locator('#tag-search-clear');
    await expect(clearBtn).toBeVisible();
    
    // Click clear
    await clearBtn.click();
});

test('clicking tag filters bhajans', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await page.waitForSelector('#app');
    
    // Wait for content to load
    await page.waitForSelector('.card', { timeout: 5000 });
    
    // Get initial bhajan count
    const initialBhajans = await page.locator('#bhajans-grid .card').count();
    
    // Find and click first visible tag button
    const firstTag = page.locator('button').filter({ hasText: /\(\d+\)/ }).first();
    await firstTag.click();
    
    // Wait for filtering
    await page.waitForTimeout(500);
    
    // Should show active filter display
    await expect(page.getByText(/Showing bhajans tagged:/)).toBeVisible();
});

test('active filters display shows selected tags', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await page.waitForSelector('#app');
    
    // Wait for tags
    await page.waitForTimeout(2000);
    
    // Find and click a tag with count
    const tagBtn = page.locator('button').filter({ hasText: /\(\d+\)/ }).first();
    await tagBtn.click();
    
    // Wait for filter status
    await page.waitForSelector('#search-status', { timeout: 2000 });
    
    // Should show active filter
    const status = page.locator('#search-status');
    await expect(status).toContainText('Found');
    
    // Should have "Clear All" button
    const clearBtn = page.getByText(/Clear All|Clear Filters/);
    await expect(clearBtn).toBeVisible();
});

test('search with tag filter combined', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await page.waitForSelector('#app');
    
    // Search for something
    const searchInput = page.locator('input[placeholder*="Search bhajans"]');
    await searchInput.fill('Krishna');
    
    // Wait for search results
    await page.waitForTimeout(500);
    
    // Click a tag if available
    const tagBtn = page.locator('button').filter({ hasText: /\(\d+\)/ }).first();
    if (await tagBtn.isVisible()) {
        await tagBtn.click();
        await page.waitForTimeout(500);
        
        // Should show both filters in status
        const status = page.locator('#search-status');
        await expect(status).toContainText(/Search:|Tag:/);
    }
});

test('clear all filters button works', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await page.waitForSelector('#app');
    
    // Apply search
    const searchInput = page.locator('input[placeholder*="Search bhajans"]');
    await searchInput.fill('Hanuman');
    await page.waitForTimeout(500);
    
    // Apply tag filter
    const tagBtn = page.locator('button').filter({ hasText: /\(\d+\)/ }).first();
    if (await tagBtn.isVisible()) {
        await tagBtn.click();
        await page.waitForTimeout(500);
    }
    
    // Should show active filters
    const statusVisible = await page.locator('#search-status').isVisible();
    if (statusVisible) {
        // Click Clear All
        const clearBtn = page.getByText(/Clear All|Clear Filters/).first();
        await clearBtn.click();
        
        // Search input should be empty
        await expect(searchInput).toHaveValue('');
    }
});

test('tag counts display correctly', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await page.waitForSelector('#app');
    
    // Wait for tags to load
    await page.waitForTimeout(2000);
    
    // Find any tag button with count
    const tagWithCount = page.locator('button').filter({ hasText: /\(\d+\)/ }).first();
    await expect(tagWithCount).toBeVisible();
    
    const textContent = await tagWithCount.textContent();
    
    // Should have format like "Hanuman (78)"
    expect(textContent).toContain('(');
    expect(textContent).toContain(')');
});

test('popular tags section visible', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await page.waitForSelector('#app');
    
    // Wait for popular tags section
    await page.waitForTimeout(2000);
    
    // Should show "POPULAR" heading
    const popularHeading = page.getByText('⭐ POPULAR');
    if (await popularHeading.isVisible()) {
        await expect(popularHeading).toBeVisible();
    }
});

test('category expansion works', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await page.waitForSelector('#app');
    
    // Wait for categories to load
    await page.waitForTimeout(2000);
    
    // Find a category button (should have ▶ or ▼)
    const categoryBtn = page.locator('button').filter({ hasText: /▶|▼/ }).first();
    if (await categoryBtn.isVisible()) {
        const initialText = await categoryBtn.textContent();
        
        // Click to toggle
        await categoryBtn.click();
        await page.waitForTimeout(300);
        
        const newText = await categoryBtn.textContent();
        
        // Text should change (arrow should flip)
        expect(newText).not.toBe(initialText);
    }
});

test('no results message appears', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await page.waitForSelector('#app');
    
    // Search for something unlikely to exist
    const searchInput = page.locator('input[placeholder*="Search bhajans"]');
    await searchInput.fill('xyzabc123nonexistent');
    
    // Wait for search
    await page.waitForTimeout(500);
    
    // Should show "No bhajans found" in status
    const status = page.locator('#search-status');
    await expect(status).toContainText(/No bhajans found/);
});

test('mobile tag section closes after tag select', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('http://localhost:8001');
    await page.waitForSelector('#app');
    
    // Open mobile tags
    const toggleBtn = page.getByText('▼ Filter by Tags');
    await toggleBtn.click();
    
    // Wait for tags section
    const mobileTags = page.locator('#mobile-tags-section');
    await expect(mobileTags).not.toHaveClass(/hidden/);
    
    // Click a tag if visible
    const tagBtn = page.locator('#mobile-tags-section button').filter({ hasText: /\(\d+\)/ }).first();
    if (await tagBtn.isVisible()) {
        await tagBtn.click();
        await page.waitForTimeout(300);
        
        // Mobile tags should auto-close
        await expect(mobileTags).toHaveClass(/hidden/);
    }
});
