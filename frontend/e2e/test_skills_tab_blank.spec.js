import { test, expect } from '@playwright/test';

test('Verify Skills navigation, rendering, filtering, edit preservation, and full section traversal', async ({ page }) => {
  page.on('console', (msg) => {
    console.log(`[PAGE LOG ${msg.type()}]:`, msg.text());
  });

  page.on('pageerror', (err) => {
    console.log('[PAGE ERROR]:', err.message);
  });

  await page.goto('http://localhost:5174/');

  // Sign In as user 2 (alfiya116shaikh@gmail.com)
  const authNavButton = page.locator('aside button').last();
  await authNavButton.click();

  const signOutBtn = page.getByRole('button', { name: 'Sign Out' });
  if (await signOutBtn.isVisible({ timeout: 1500 }).catch(() => false)) {
    await signOutBtn.click();
    await page.waitForTimeout(500);
  }

  await page.locator('input[type="email"]').fill('alfiya116shaikh@gmail.com');
  await page.locator('input[type="password"]').fill('Password123!');
  await page.getByRole('button', { name: 'Sign In', exact: true }).click();

  await expect(page.locator('aside').getByText('Alfiya Shaikh')).toBeVisible({ timeout: 10000 });

  // Navigate to Profile page
  await page.getByRole('button', { name: 'Profile' }).click();
  await page.waitForTimeout(1500);

  // Click Review Extraction button
  const reviewBtn = page.getByRole('button', { name: /Review Extraction/i }).first();
  await expect(reviewBtn).toBeVisible({ timeout: 10000 });
  await expect(reviewBtn).toBeEnabled({ timeout: 10000 });
  await reviewBtn.click();

  const modal = page.locator('.fixed.inset-0.z-50');
  await expect(modal.getByText('Review Extracted Resume Data')).toBeVisible({ timeout: 15000 });

  // Verify Tab 1 (Contact Info) is active
  await expect(modal.getByText('Contact & Personal Details')).toBeVisible();

  // Navigate to Skills Tab
  const skillsTabBtn = modal.locator('button').filter({ hasText: /Skills/ }).first();
  await skillsTabBtn.click();
  await page.waitForTimeout(500);

  // Confirm NO blank screen and #root is active
  const rootHtml = await page.locator('#root').innerHTML();
  expect(rootHtml.length).toBeGreaterThan(1000);

  // Verify Skills section content rendered correctly
  await expect(modal.getByText(/Extracted Skills/i)).toBeVisible();

  // Test Search functionality
  const searchInput = modal.locator('input[placeholder="Search detected skills..."]');
  await expect(searchInput).toBeVisible();
  await searchInput.fill('Python');
  await page.waitForTimeout(300);
  await expect(modal.locator('span.badge-tag').filter({ hasText: /Python/i }).first()).toBeVisible();
  await searchInput.fill('');
  await page.waitForTimeout(300);

  // Test Category filter chips
  const allChip = modal.locator('button').filter({ hasText: /^All \(/ }).first();
  await expect(allChip).toBeVisible();

  // Test Adding a new skill
  const addSkillInput = modal.locator('input[placeholder="Add missing skill..."]');
  await addSkillInput.fill('Playwright Testing');
  const addBtn = modal.locator('button').filter({ hasText: /^Add$/ }).first();
  await addBtn.click();
  await page.waitForTimeout(300);
  await expect(modal.locator('span.badge-tag').filter({ hasText: /Playwright Testing/i }).first()).toBeVisible();

  // Test Stepper Navigation across remaining sections:
  // Next -> Projects
  const nextBtn = modal.locator('button').filter({ hasText: /^Next$/ }).first();
  await nextBtn.click();
  await page.waitForTimeout(300);
  await expect(modal.getByText(/Extracted Projects/i)).toBeVisible();

  // Next -> Experience
  await nextBtn.click();
  await page.waitForTimeout(300);
  await expect(modal.getByText(/Extracted Work Experience/i)).toBeVisible();

  // Next -> Education
  await nextBtn.click();
  await page.waitForTimeout(300);
  await expect(modal.getByText(/Extracted Education/i)).toBeVisible();

  // Next -> Certifications
  await nextBtn.click();
  await page.waitForTimeout(300);
  await expect(modal.getByText(/Extracted Certifications/i)).toBeVisible();

  // Check if Custom Sections exists, navigate to it if so
  const customTabBtn = modal.locator('button').filter({ hasText: /Preserved Sections/i }).first();
  if (await customTabBtn.isVisible().catch(() => false)) {
    await customTabBtn.click();
    await page.waitForTimeout(300);
    await expect(modal.getByText(/Preserved Custom Sections/i)).toBeVisible();
  }

  // Navigate back to Skills and verify state was preserved!
  await skillsTabBtn.click();
  await page.waitForTimeout(300);
  await expect(modal.locator('span.badge-tag').filter({ hasText: /Playwright Testing/i }).first()).toBeVisible();

  // Test removing a skill
  const removeSkillPill = modal.locator('span.badge-tag').filter({ hasText: /Playwright Testing/i }).first();
  const removeSkillBtn = removeSkillPill.locator('button');
  await removeSkillBtn.click();
  await page.waitForTimeout(300);
  await expect(modal.locator('span.badge-tag').filter({ hasText: /Playwright Testing/i })).toHaveCount(0);

  // Close modal safely
  const cancelBtn = modal.locator('button').filter({ hasText: /Cancel/i }).first();
  await cancelBtn.click();
  await expect(modal).not.toBeVisible();
});
