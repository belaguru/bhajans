/**
 * Test Suite: Delete Functionality
 * Tests for bhajan soft delete via API
 */
const { test, expect } = require('@playwright/test');

test.describe('Delete API', () => {
    test('DELETE endpoint soft deletes bhajan', async ({ request }) => {
        // First create a new bhajan to delete using form data
        const formData = new URLSearchParams();
        formData.append('title', `Delete Test ${Date.now()}`);
        formData.append('lyrics', 'Will be deleted - this is at least twenty characters');
        formData.append('tags', '');
        formData.append('uploader_name', 'Test');
        
        const createResponse = await request.post('/api/bhajans', {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            data: formData.toString()
        });
        expect(createResponse.status()).toBe(200);
        const bhajan = await createResponse.json();
        
        // Delete it
        const deleteResponse = await request.delete(`/api/bhajans/${bhajan.id}`);
        expect(deleteResponse.status()).toBe(200);
        
        const result = await deleteResponse.json();
        expect(result.status).toBe('deleted');
    });

    test('deleted bhajan not returned in list', async ({ request }) => {
        // Create and delete using form data
        const formData = new URLSearchParams();
        formData.append('title', `Delete List Test ${Date.now()}`);
        formData.append('lyrics', 'Will be deleted - this is at least twenty characters');
        formData.append('tags', '');
        formData.append('uploader_name', 'Test');
        
        const createResponse = await request.post('/api/bhajans', {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            data: formData.toString()
        });
        expect(createResponse.status()).toBe(200);
        const bhajan = await createResponse.json();
        await request.delete(`/api/bhajans/${bhajan.id}`);
        
        // Verify not in list
        const listResponse = await request.get('/api/bhajans');
        const bhajans = await listResponse.json();
        const found = bhajans.find(b => b.id === bhajan.id);
        expect(found).toBeUndefined();
    });

    test('deleted bhajan returns 404', async ({ request }) => {
        // Create and delete using form data
        const formData = new URLSearchParams();
        formData.append('title', `Delete 404 Test ${Date.now()}`);
        formData.append('lyrics', 'Will be deleted - this is at least twenty characters');
        formData.append('tags', '');
        formData.append('uploader_name', 'Test');
        
        const createResponse = await request.post('/api/bhajans', {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            data: formData.toString()
        });
        expect(createResponse.status()).toBe(200);
        const bhajan = await createResponse.json();
        await request.delete(`/api/bhajans/${bhajan.id}`);
        
        // Verify 404
        const getResponse = await request.get(`/api/bhajans/${bhajan.id}`);
        expect(getResponse.status()).toBe(404);
    });

    test('cannot delete non-existent bhajan', async ({ request }) => {
        const response = await request.delete('/api/bhajans/999999');
        expect(response.status()).toBe(404);
    });
});
