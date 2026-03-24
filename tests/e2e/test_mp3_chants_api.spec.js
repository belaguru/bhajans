const { test, expect } = require('@playwright/test');

test.describe('MP3 & Chants API', () => {
  
  test('API returns mp3_file field in list responses', async ({ request }) => {
    const response = await request.get('/api/bhajans');
    expect(response.ok()).toBeTruthy();
    
    const bhajans = await response.json();
    expect(Array.isArray(bhajans)).toBeTruthy();
    expect(bhajans.length).toBeGreaterThan(0);
    
    // Check that mp3_file key exists (even if null for bhajans without MP3)
    const firstBhajan = bhajans[0];
    expect(firstBhajan).toHaveProperty('mp3_file');
  });

  test('Chants return mp3_file filenames when available', async ({ request }) => {
    const response = await request.get('/api/bhajans?tag=chant');
    expect(response.ok()).toBeTruthy();
    
    const chants = await response.json();
    // Chants may or may not exist depending on database state
    // Check structure if chants exist
    if (chants.length > 0) {
      const chantsWithMp3 = chants.filter(c => c.mp3_file);
      // If any chants have MP3, verify format
      for (const chant of chantsWithMp3) {
        expect(chant.mp3_file).toContain('.mp3');
      }
    }
  });

  test('GET /api/bhajans/7 returns bhajan with MP3', async ({ request }) => {
    const response = await request.get('/api/bhajans/7');
    expect(response.ok()).toBeTruthy();
    
    const bhajan = await response.json();
    expect(bhajan.id).toBe(7);
    expect(bhajan.mp3_file).toBe('mahamrityunjaya.mp3');
  });

  test('Bhajans with MP3 files have valid mp3_file field', async ({ request }) => {
    // Get all bhajans and check any with MP3 files
    const response = await request.get('/api/bhajans');
    expect(response.ok()).toBeTruthy();
    
    const bhajans = await response.json();
    const mp3Bhajans = bhajans.filter(b => b.mp3_file && b.mp3_file.endsWith('.mp3'));
    
    // At least some bhajans should have MP3 files
    expect(mp3Bhajans.length).toBeGreaterThan(0);
    
    // Each MP3 bhajan should have valid structure
    for (const bhajan of mp3Bhajans) {
      expect(bhajan.mp3_file).toMatch(/\.mp3$/);
      expect(Array.isArray(bhajan.tags)).toBeTruthy();
    }
  });

  test('Bhajans have all required fields', async ({ request }) => {
    // Get first available bhajan
    const listResponse = await request.get('/api/bhajans?limit=1');
    const bhajans = await listResponse.json();
    expect(bhajans.length).toBeGreaterThan(0);
    
    const response = await request.get(`/api/bhajans/${bhajans[0].id}`);
    expect(response.ok()).toBeTruthy();
    
    const bhajan = await response.json();
    
    expect(bhajan).toHaveProperty('id');
    expect(bhajan).toHaveProperty('title');
    expect(bhajan).toHaveProperty('lyrics');
    expect(bhajan).toHaveProperty('tags');
    expect(bhajan).toHaveProperty('mp3_file');
    expect(bhajan).toHaveProperty('uploader_name');
    expect(bhajan).toHaveProperty('created_at');
    expect(bhajan).toHaveProperty('updated_at');
    
    expect(typeof bhajan.id).toBe('number');
    expect(typeof bhajan.title).toBe('string');
    // mp3_file can be null or string
    expect(bhajan.mp3_file === null || typeof bhajan.mp3_file === 'string').toBeTruthy();
    expect(Array.isArray(bhajan.tags)).toBeTruthy();
  });
});
