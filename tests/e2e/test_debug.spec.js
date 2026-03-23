const { test } = require('@playwright/test');

test('debug upload page', async ({ page }) => {
  await page.goto('http://localhost:8001/');
  await page.waitForLoadState('domcontentloaded');
  
  await page.evaluate(() => {
    window.app.setPage('upload');
  });
  
  await page.waitForTimeout(2000);
  
  // Get all elements with IDs containing "tag"
  const tagElements = await page.$$eval('[id*="tag"]', els => 
    els.map(el => ({ id: el.id, visible: el.offsetParent !== null, innerHTML: el.innerHTML.substring(0, 100) }))
  );
  
  console.log('Elements with "tag" in ID:', JSON.stringify(tagElements, null, 2));
  
  // Get all checkboxes
  const checkboxes = await page.$$eval('input[type="checkbox"]', els => 
    els.map(el => ({ id: el.id, dataTagId: el.dataset.tagId, visible: el.offsetParent !== null }))
  );
  
  console.log('Checkboxes:', JSON.stringify(checkboxes, null, 2));
  
  // Screenshot
  await page.screenshot({ path: '/tmp/upload-page-debug.png', fullPage: true });
  console.log('Screenshot saved to /tmp/upload-page-debug.png');
});
