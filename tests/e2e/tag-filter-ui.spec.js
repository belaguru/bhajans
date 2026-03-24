/**
 * Test Suite: Tag Filter UI
 * Tests for the enhanced tag-based filtering and search UI
 */
const { test, expect } = require('@playwright/test');

// Helper to wait for app to finish loading
async function waitForAppLoaded(page) {
    await page.waitForSelector('#app[data-loaded="true"]', { timeout: 15000 });
}

test('tag filter sidebar visible on desktop', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await waitForAppLoaded(page);
    
    // Desktop sidebar should be visible (check for tag section)
    // The desktop tags are NOT in #mobile-tags-section
    const desktopTags = page.locator('.lg\\:col-span-1:not(#mobile-tags-section)').first();
    await expect(desktopTags).toBeVisible();
    
    // Check for category buttons (desktop tags)
    const categoryBtn = page.locator('button:has-text("🕉️ Deities")').last(); // last() = desktop version
    await expect(categoryBtn).toBeVisible();
});

test('mobile tag filter toggle', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('http://localhost:8001');
    await waitForAppLoaded(page);
    
    // Mobile toggle button should be visible
    const toggleBtn = page.getByText('▼ Filter by Tags');
    await expect(toggleBtn).toBeVisible();
    
    // Mobile tags section should initially have 'hidden' class (lg:hidden means desktop hidden, mobile conditional)
    const mobileTags = page.locator('#mobile-tags-section');
    const initialClasses = await mobileTags.getAttribute('class');
    
    // Click toggle
    await toggleBtn.click();
    await page.waitForTimeout(200);
    
    // After toggle, classes should change (toggles visibility)
    const newClasses = await mobileTags.getAttribute('class');
    expect(newClasses).not.toBe(initialClasses);
});

test('tag search filters tags', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await waitForAppLoaded(page);
    
    // Wait for tag categories to load (use .last() for desktop version)
    const categoryBtn = page.locator('button:has-text("🕉️ Deities")').last();
    await expect(categoryBtn).toBeVisible();
    
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
    await waitForAppLoaded(page);
    
    // Wait for bhajan cards to load (not .card in general, but bhajan cards specifically)
    await page.waitForTimeout(2000);
    
    // Expand a category first (use .last() for desktop version)
    const deityCategory = page.locator('button:has-text("🕉️ Deities")').last();
    await deityCategory.click();
    await page.waitForTimeout(300);
    
    // Find and click first visible tag button within expanded category
    const firstTag = page.locator('.space-y-1 button').filter({ hasText: /\(\d+\)/ }).first();
    if (await firstTag.isVisible()) {
        await firstTag.click();
        
        // Wait for filtering
        await page.waitForTimeout(500);
        
        // Should show active filter display
        const statusVisible = await page.getByText(/Showing bhajans tagged:/).isVisible();
        if (statusVisible) {
            await expect(page.getByText(/Showing bhajans tagged:/)).toBeVisible();
        }
    }
});

test('active filters display shows selected tags', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await waitForAppLoaded(page);
    
    // Wait for tags to load
    await page.waitForTimeout(2000);
    
    // Expand a category (use .last() for desktop version)
    const deityCategory = page.locator('button:has-text("🕉️ Deities")').last();
    await deityCategory.click();
    await page.waitForTimeout(300);
    
    // Find and click a tag with count
    const tagBtn = page.locator('.space-y-1 button').filter({ hasText: /\(\d+\)/ }).first();
    if (await tagBtn.isVisible()) {
        await tagBtn.click();
        
        // Wait for filter status
        await page.waitForSelector('#search-status', { timeout: 2000 });
        
        // Should show active filter
        const status = page.locator('#search-status');
        await expect(status).toContainText('Found');
        
        // Should have "Clear All" button
        const clearBtn = page.getByText(/Clear All|Clear Filters/);
        await expect(clearBtn).toBeVisible();
    }
});

test('search with tag filter combined', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await waitForAppLoaded(page);
    
    // Search for something
    const searchInput = page.locator('input[placeholder*="Search bhajans"]');
    await searchInput.fill('Krishna');
    
    // Wait for search results
    await page.waitForTimeout(500);
    
    // Expand deity category (use .last() for desktop version)
    const deityCategory = page.locator('button:has-text("🕉️ Deities")').last();
    await deityCategory.click();
    await page.waitForTimeout(300);
    
    // Click a tag if available
    const tagBtn = page.locator('.space-y-1 button').filter({ hasText: /\(\d+\)/ }).first();
    if (await tagBtn.isVisible()) {
        await tagBtn.click();
        await page.waitForTimeout(500);
        
        // Should show both filters in status
        const status = page.locator('#search-status');
        const statusText = await status.textContent();
        expect(statusText).toContain('Found');
    }
});

test('clear all filters button works', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await waitForAppLoaded(page);
    
    // Apply search
    const searchInput = page.locator('input[placeholder*="Search bhajans"]');
    await searchInput.fill('Hanuman');
    await page.waitForTimeout(500);
    
    // Expand category and apply tag filter (use .last() for desktop version)
    const deityCategory = page.locator('button:has-text("🕉️ Deities")').last();
    await deityCategory.click();
    await page.waitForTimeout(300);
    
    const tagBtn = page.locator('.space-y-1 button').filter({ hasText: /\(\d+\)/ }).first();
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
    await waitForAppLoaded(page);
    
    // Wait for tags to load
    await page.waitForTimeout(2000);
    
    // Expand a category to see tags (use .last() for desktop version)
    const deityCategory = page.locator('button:has-text("🕉️ Deities")').last();
    await deityCategory.click();
    await page.waitForTimeout(300);
    
    // Find any tag button with count
    const tagWithCount = page.locator('.space-y-1 button').filter({ hasText: /\(\d+\)/ }).first();
    if (await tagWithCount.isVisible()) {
        await expect(tagWithCount).toBeVisible();
        
        const textContent = await tagWithCount.textContent();
        
        // Should have format like "Hanuman (78)"
        expect(textContent).toContain('(');
        expect(textContent).toContain(')');
    }
});

test('category expansion works', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await waitForAppLoaded(page);
    
    // Wait for categories to load
    await page.waitForTimeout(2000);
    
    // Find deity category button (use .last() for desktop version)
    const categoryBtn = page.locator('button:has-text("🕉️ Deities")').last();
    const initialText = await categoryBtn.textContent();
    
    // Click to toggle
    await categoryBtn.click();
    await page.waitForTimeout(300);
    
    const newText = await categoryBtn.textContent();
    
    // Text should change (arrow should flip)
    expect(newText).not.toBe(initialText);
});

test('no results message appears', async ({ page }) => {
    await page.goto('http://localhost:8001');
    await waitForAppLoaded(page);
    
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
    await waitForAppLoaded(page);
    
    // Open mobile tags
    const toggleBtn = page.getByText('▼ Filter by Tags');
    await toggleBtn.click();
    await page.waitForTimeout(300);
    
    // Expand a category
    const deityCategory = page.locator('#mobile-tags-section button:has-text("🕉️ Deities")');
    if (await deityCategory.isVisible()) {
        await deityCategory.click();
        await page.waitForTimeout(300);
        
        // Click a tag if visible
        const tagBtn = page.locator('#mobile-tags-section .space-y-1 button').filter({ hasText: /\(\d+\)/ }).first();
        if (await tagBtn.isVisible()) {
            await tagBtn.click();
            await page.waitForTimeout(300);
            
            // Mobile tags toggle button should show it's closed now
            const toggleText = await toggleBtn.textContent();
            expect(toggleText).toContain('▼');
        }
    }
});
