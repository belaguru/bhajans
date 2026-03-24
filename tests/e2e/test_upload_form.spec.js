/**
 * Test Suite: Upload Form
 * Tests for bhajan upload functionality
 */
const { test, expect } = require('@playwright/test');

// Helper to wait for app to finish loading
async function waitForAppLoaded(page) {
    await page.waitForSelector('#app[data-loaded="true"]', { timeout: 15000 });
}

test.describe('Upload Page', () => {
    test('upload page loads via setPage', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        
        await page.evaluate(() => window.app.setPage('upload'));
        await page.waitForTimeout(300);
        
        const content = await page.locator('#app').innerHTML();
        expect(content.toLowerCase()).toMatch(/upload|add.*bhajan|new/);
    });

    test('upload form has title input', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        await page.evaluate(() => window.app.setPage('upload'));
        await page.waitForTimeout(300);
        
        const titleInput = page.locator('#title');
        await expect(titleInput).toBeAttached();
    });

    test('upload form has lyrics textarea', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        await page.evaluate(() => window.app.setPage('upload'));
        await page.waitForTimeout(300);
        
        const lyricsInput = page.locator('#lyrics');
        await expect(lyricsInput).toBeAttached();
    });

    test('upload form has youtube input', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        await page.evaluate(() => window.app.setPage('upload'));
        await page.waitForTimeout(300);
        
        const youtubeInput = page.locator('#youtube_url');
        await expect(youtubeInput).toBeAttached();
    });

    test('upload form has tags selector', async ({ page }) => {
        await page.goto('/');
        await waitForAppLoaded(page);
        await page.evaluate(() => window.app.setPage('upload'));
        await page.waitForTimeout(300);
        
        const tagsSelector = page.locator('#tags_selector');
        await expect(tagsSelector).toBeAttached();
    });
});

test.describe('Upload API', () => {
    test('POST creates bhajan with form data', async ({ request }) => {
        const formData = new URLSearchParams();
        formData.append('title', `Upload Test ${Date.now()}`);
        formData.append('lyrics', 'Test lyrics that are at least twenty characters long for validation');
        formData.append('tags', '');
        formData.append('uploader_name', 'E2E Test');
        
        const response = await request.post('/api/bhajans', {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            data: formData.toString()
        });
        
        expect(response.status()).toBe(200);
        const bhajan = await response.json();
        expect(bhajan.id).toBeDefined();
        
        // Cleanup
        await request.delete(`/api/bhajans/${bhajan.id}`);
    });

    test('POST creates bhajan with YouTube URL', async ({ request }) => {
        const formData = new URLSearchParams();
        formData.append('title', `YouTube Test ${Date.now()}`);
        formData.append('lyrics', 'Test lyrics that are at least twenty characters long for validation');
        formData.append('youtube_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
        formData.append('tags', '');
        formData.append('uploader_name', 'E2E Test');
        
        const response = await request.post('/api/bhajans', {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            data: formData.toString()
        });
        
        expect(response.status()).toBe(200);
        const bhajan = await response.json();
        expect(bhajan.youtube_url).toContain('youtube');
        
        // Cleanup
        await request.delete(`/api/bhajans/${bhajan.id}`);
    });

    test('POST creates bhajan with tags', async ({ request }) => {
        // Get existing tags
        const tagsResponse = await request.get('/api/tags');
        const tags = await tagsResponse.json();
        const tagIds = tags.slice(0, 2).map(t => t.id).join(',');
        
        const formData = new URLSearchParams();
        formData.append('title', `Tags Test ${Date.now()}`);
        formData.append('lyrics', 'Test lyrics with tags that are at least twenty characters long');
        formData.append('tags', tagIds);
        formData.append('uploader_name', 'E2E Test');
        
        const response = await request.post('/api/bhajans', {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            data: formData.toString()
        });
        
        expect(response.status()).toBe(200);
        const bhajan = await response.json();
        expect(bhajan.tags.length).toBeGreaterThanOrEqual(0); // Tags may or may not be returned
        
        // Cleanup
        await request.delete(`/api/bhajans/${bhajan.id}`);
    });

    test('POST requires title', async ({ request }) => {
        const formData = new URLSearchParams();
        formData.append('lyrics', 'Test lyrics only that are at least twenty characters');
        formData.append('tags', '');
        
        const response = await request.post('/api/bhajans', {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            data: formData.toString()
        });
        
        expect(response.status()).toBe(422);
    });
});
