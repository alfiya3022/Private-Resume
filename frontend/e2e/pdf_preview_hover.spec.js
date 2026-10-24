import { test, expect } from '@playwright/test';

test('Verify PDF Previewer renders with yellow hover highlight and LinkedIn link', async ({ page }) => {
  // Use fresh token for User 2 (Alfiya Shaikh) who has Job 17 and tailored resumes
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3OTI3MDI2OTQsInN1YiI6IjIifQ.d6YPTQId474baIRIw8GP1BVEYgJ3hRoeN2U-BkIkkD0';

  await page.goto('http://localhost:5174/');
  await page.evaluate((t) => {
    localStorage.setItem('token', t);
  }, token);

  await page.goto('http://localhost:5174/');
  await page.waitForTimeout(1000);

  // Navigate to Workspace
  const workspaceBtn = page.getByRole('button', { name: 'Workspace' });
  await workspaceBtn.click();
  await page.waitForTimeout(1000);

  // Select a saved job (e.g., Job 17 or any saved job) to set activeJob and activeTailoredResume
  const savedJobBtn = page.locator('button:has-text("#17")').or(page.locator('button:has-text("Data Analyst")')).first();
  if (await savedJobBtn.isVisible()) {
    await savedJobBtn.click();
    await page.waitForTimeout(1500);
  }

  // Click on Stage 5: PDF
  const stage5Tab = page.locator('button', { hasText: '5. PDF' });
  if (await stage5Tab.isVisible()) {
    await stage5Tab.click();
  }

  // Wait for the PDF previewer root to appear
  const previewer = page.locator('.pdf-previewer-root');
  await expect(previewer).toBeVisible({ timeout: 15000 });

  // Wait for the canvas to render
  const canvas = page.locator('.pdf-page-wrapper canvas').first();
  await expect(canvas).toBeVisible({ timeout: 15000 });

  // Find interactive link overlays (wait for PDF.js annotations to finish rendering)
  const links = page.locator('.pdf-interactive-link-overlay');
  await expect(links.first()).toBeVisible({ timeout: 15000 });
  const count = await links.count();
  console.log(`Found ${count} interactive link overlays in PDF previewer`);
  expect(count).toBeGreaterThan(0);

  // Find the LinkedIn link
  let linkedinLink = null;
  for (let i = 0; i < count; i++) {
    const l = links.nth(i);
    const href = await l.getAttribute('href');
    console.log(`Link ${i}: ${href}`);
    if (href && href.includes('linkedin.com')) {
      linkedinLink = l;
      break;
    }
  }

  expect(linkedinLink).not.toBeNull();

  // Hover over the LinkedIn link
  await linkedinLink.hover();
  await page.waitForTimeout(500);

  // Verify the computed background color turns yellow
  const bgColor = await linkedinLink.evaluate((el) => {
    return window.getComputedStyle(el).backgroundColor;
  });
  console.log('Hovered background color:', bgColor);

  // Check that the background is yellow (rgba(254, 240, 138, ...) or rgb(254, 240, 138) or similar yellow)
  expect(bgColor).toMatch(/rgba?\(254,\s*240,\s*138/);

  // Take screenshot of the preview
  await page.screenshot({ path: 'pdf_preview_hover_verification.png', fullPage: false });
  console.log('Screenshot saved to pdf_preview_hover_verification.png');
});
