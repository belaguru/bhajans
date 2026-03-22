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

  test('Chants return mp3_file filenames', async ({ request }) => {
    const response = await request.get('/api/bhajans?tag=chant');
    expect(response.ok()).toBeTruthy();
    
    const chants = await response.json();
    expect(chants.length).toBeGreaterThanOrEqual(5);
    
    // Check each chant has mp3_file populated
    for (const chant of chants.slice(0, 5)) {
      expect(chant.mp3_file).toBeTruthy();
      expect(chant.mp3_file).toContain('.mp3');
    }
  });

  test('GET /api/bhajans/274 returns Mahamrityunjaya with MP3', async ({ request }) => {
    const response = await request.get('/api/bhajans/274');
    expect(response.ok()).toBeTruthy();
    
    const chant = await response.json();
    expect(chant.id).toBe(274);
    expect(chant.title).toContain('Mahamrityunjaya');
    expect(chant.mp3_file).toBe('mahamrityunjaya.mp3');
  });

  test('All 5 chants have correct MP3 files', async ({ request }) => {
    const expectedChants = [
      { id: 270, mp3: 'om-namah-shivaya.mp3' },
      { id: 271, mp3: 'gayatri-mantra.mp3' },
      { id: 272, mp3: 'hare-rama-krishna.mp3' },
      { id: 273, mp3: 'om-namo-narayanaya.mp3' },
      { id: 274, mp3: 'mahamrityunjaya.mp3' }
    ];
    
    for (const expected of expectedChants) {
      const response = await request.get(`/api/bhajans/${expected.id}`);
      const chant = await response.json();
      
      expect(chant.mp3_file).toBe(expected.mp3);
      // Tags are now capitalized in the new tag system
      expect(chant.tags.some(tag => tag.toLowerCase().includes('mantra'))).toBeTruthy();
    }
  });

  test('Chants have all required fields', async ({ request }) => {
    const response = await request.get('/api/bhajans/274');
    const chant = await response.json();
    
    expect(chant).toHaveProperty('id');
    expect(chant).toHaveProperty('title');
    expect(chant).toHaveProperty('lyrics');
    expect(chant).toHaveProperty('tags');
    expect(chant).toHaveProperty('mp3_file');
    expect(chant).toHaveProperty('uploader_name');
    expect(chant).toHaveProperty('created_at');
    expect(chant).toHaveProperty('updated_at');
    
    expect(typeof chant.id).toBe('number');
    expect(typeof chant.title).toBe('string');
    expect(typeof chant.mp3_file).toBe('string');
    expect(Array.isArray(chant.tags)).toBeTruthy();
  });
});
