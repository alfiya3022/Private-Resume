import { test, expect } from '@playwright/test';

test.describe('PrivateResume E2E Candidate Workflow', () => {
  test('1. System Health & Branding Smoke Test', async ({ page }) => {
    await page.goto('/');

    // Check Header Branding
    await expect(page.locator('header').getByText('PrivateResume', { exact: true })).toBeVisible();
    await expect(page.locator('text=Local-First V1')).toBeVisible();

    // Check Navigation Tabs
    await expect(page.getByRole('button', { name: 'Workspace' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Profile' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Applications' })).toBeVisible();

    // Check Subsystem Connection
    await expect(page.locator('text=API Connected')).toBeVisible({ timeout: 10000 });
  });

  test('2. Complete End-to-End Candidate Journey', async ({ page }) => {
    await page.goto('/');

    // 1. Sign In
    const authNavButton = page.locator('header nav button').last();
    await authNavButton.click();

    const signOutBtn = page.getByRole('button', { name: 'Sign Out' });
    if (await signOutBtn.isVisible({ timeout: 1500 }).catch(() => false)) {
      await signOutBtn.click();
      await page.waitForTimeout(500);
    }

    await expect(page.locator('text=Welcome to PrivateResume')).toBeVisible();
    await page.locator('input[type="email"]').fill('demo@privateresume.local');
    await page.locator('input[type="password"]').fill('Password123!');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Verify authentication reflected in navbar
    await expect(page.locator('header').getByText('Alex Morgan')).toBeVisible({ timeout: 10000 });

    // 2. Profile Inspection
    await page.getByRole('button', { name: 'Profile' }).click();
    await expect(page.getByText('Master Resume PDF Parser')).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button', { name: /Personal Info/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Skills/i })).toBeVisible();

    // 3. Workspace Inspection
    await page.getByRole('button', { name: 'Workspace' }).click();
    await expect(page.getByText('1. Add Inputs')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Target Opportunity Details')).toBeVisible();

    // 4. Application Pipeline Inspection
    await page.getByRole('button', { name: 'Applications' }).click();
    await expect(page.getByText('Application Pipeline')).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button', { name: 'All Applications' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Applied' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Interviewing' })).toBeVisible();

    // 5. Clean Sign Out
    await page.locator('header nav button').last().click();
    await page.getByRole('button', { name: 'Sign Out' }).click();
    await expect(page.locator('text=Welcome to PrivateResume')).toBeVisible();
  });
});
