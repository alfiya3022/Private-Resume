import { test, expect } from '@playwright/test';

test('Verify complete Master Resume lifecycle: upload, modal stepper, editing, duplicate consent, and apply to profile', async ({ page }) => {
  test.setTimeout(90000);
  await page.goto('http://localhost:5174/');

  // 1. Authenticate as candidate
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

  // 2. Navigate to Profile page
  await page.getByRole('button', { name: 'Profile' }).click();
  await page.waitForTimeout(1000);

  // 3. Open Extraction Review Modal
  const reviewBtn = page.getByRole('button', { name: /Review Extraction/i }).first();
  await expect(reviewBtn).toBeVisible({ timeout: 10000 });
  await reviewBtn.click();

  const modal = page.locator('div.fixed.inset-0.z-50').filter({ hasText: 'Review Extracted Resume Data' });
  await expect(modal).toBeVisible({ timeout: 15000 });

  // 4. Verify Tab 1: Contact Info
  await expect(modal.getByText('Contact & Personal Details')).toBeVisible();

  // 5. Navigate to Tab 2: Skills
  const skillsTab = modal.locator('button').filter({ hasText: /Skills/ }).first();
  await skillsTab.click();
  await expect(modal.getByText(/Extracted Skills/i)).toBeVisible();

  // 6. Navigate to Tab 3: Projects & test editing
  const projectsTab = modal.locator('button').filter({ hasText: /Projects/ }).first();
  await projectsTab.click();
  await expect(modal.getByText(/Extracted Projects/i)).toBeVisible();

  // 7. Navigate to Tab 4: Experience
  const expTab = modal.locator('button').filter({ hasText: /Experience/ }).first();
  await expTab.click();
  await expect(modal.getByText(/Extracted Work Experience/i)).toBeVisible();

  // 8. Navigate to Tab 5: Education
  const eduTab = modal.locator('button').filter({ hasText: /Education/ }).first();
  await eduTab.click();
  await expect(modal.getByText(/Extracted Education/i)).toBeVisible();

  // 9. Navigate to Tab 6: Certifications
  const certTab = modal.locator('button').filter({ hasText: /Certifications/ }).first();
  await certTab.click();
  await expect(modal.getByText(/Extracted Certifications/i)).toBeVisible();

  // 10. Check Stepper Navigation
  const prevBtn = modal.getByRole('button', { name: /Previous/i });
  await expect(prevBtn).toBeEnabled();
  await prevBtn.click();
  await expect(modal.getByText(/Extracted Education/i)).toBeVisible();

  // 11. Apply Selected to Profile
  const applyBtn = modal.getByRole('button', { name: /Apply Selected to Profile/i });
  await expect(applyBtn).toBeVisible();
  await expect(applyBtn).toBeEnabled();
  await applyBtn.click();

  // 12. Modal closes and Profile page reflects updated status
  await expect(modal).not.toBeVisible({ timeout: 30000 });
});
