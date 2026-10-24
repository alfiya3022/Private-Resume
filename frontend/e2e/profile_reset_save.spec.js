import { test, expect } from '@playwright/test';

test.describe('Profile Section Reset & Save Controls (Persisted Deletion & Draft Clearing)', () => {
  async function dismissValidationPopup(page) {
    const continueBtn = page.getByRole('button', { name: 'Continue' });
    await expect(continueBtn).toBeVisible({ timeout: 5000 });
    await continueBtn.click();
    await expect(continueBtn).not.toBeVisible({ timeout: 3000 });
  }

  test.beforeEach(async ({ page }) => {
    // Navigate to base URL
    await page.goto('http://localhost:5174/');

    // Ensure signed in as demo user
    const authNavButton = page.locator('aside button').last();
    await authNavButton.click();

    const signOutBtn = page.getByRole('button', { name: 'Sign Out' });
    if (await signOutBtn.isVisible().catch(() => false)) {
      await signOutBtn.click();
      await page.waitForTimeout(500);
    }

    await expect(page.locator('text=Welcome to PrivateResume')).toBeVisible();
    await page.locator('input[type="email"]').fill('demo@privateresume.local');
    await page.locator('input[type="password"]').fill('Password123!');
    await page.getByRole('button', { name: 'Sign In', exact: true }).click();
    await expect(page.locator('aside').getByText('Alex Morgan')).toBeVisible({ timeout: 10000 });

    // Navigate to Profile page
    await page.getByRole('button', { name: 'Profile' }).click();
    await expect(page.getByText('Candidate Profile', { exact: true })).toBeVisible({ timeout: 10000 });
  });

  test('Scenario 1: Personal Info Tab Reset clears form and deletes persisted data from database', async ({ page }) => {
    // 1. Ensure in edit mode and save personal info
    const editPersonalBtn = page.getByRole('button', { name: 'Edit Personal Info' });
    if (await editPersonalBtn.isVisible().catch(() => false)) {
      await editPersonalBtn.click();
    }

    const headlineInput = page.locator('input[placeholder="e.g. Senior Full-Stack Engineer"]');
    const locationInput = page.locator('input[placeholder="e.g. San Francisco, CA"]');
    const summaryInput = page.locator('textarea[placeholder*="Brief factual summary"]');

    await expect(headlineInput).toBeVisible();
    await headlineInput.fill('Lead Systems Architect');
    await locationInput.fill('Chicago, IL');
    await summaryInput.fill('Experienced distributed systems engineer with 10+ years experience.');

    // Save Personal Details
    await page.getByRole('button', { name: 'Save Personal Details' }).click();
    await expect(page.getByText(/Personal info saved successfully/i)).toBeVisible({ timeout: 5000 });
    await dismissValidationPopup(page);

    // Now re-open edit mode and add an unsaved draft alteration
    const editAgainBtn = page.getByRole('button', { name: 'Edit Personal Info' });
    await expect(editAgainBtn).toBeVisible({ timeout: 5000 });
    await editAgainBtn.click();
    await headlineInput.fill('Unsaved Draft Headline');

    // 2. Click Reset on Personal Info tab
    const tabResetBtn = page.getByRole('button', { name: 'Reset', exact: true });
    await tabResetBtn.click();

    // Verify confirmation modal opens
    await expect(page.getByText('Reset Personal Info')).toBeVisible();
    await expect(page.getByText(/Permanently delete all saved personal info records/i)).toBeVisible();

    // Confirm deletion
    await page.getByRole('button', { name: 'Reset & Delete' }).click();

    // Verify success feedback
    await expect(page.getByText(/Successfully reset Personal Info and deleted all saved records/i)).toBeVisible();

    // Verify inputs are cleared
    await expect(headlineInput).toHaveValue('');
    await expect(locationInput).toHaveValue('');
    await expect(summaryInput).toHaveValue('');

    // 3. Reload page to verify database persistence of deletion
    await page.reload();
    await page.getByRole('button', { name: 'Profile' }).click();
    await expect(page.getByText('Candidate Profile', { exact: true })).toBeVisible({ timeout: 10000 });

    const editAfterReload = page.getByRole('button', { name: 'Edit Personal Info' });
    if (await editAfterReload.isVisible().catch(() => false)) {
      await editAfterReload.click();
    }
    await expect(headlineInput).toHaveValue('');
    await expect(locationInput).toHaveValue('');
  });

  test('Scenario 2: Skills Tab Reset deletes persisted skills and clears input draft', async ({ page }) => {
    await page.getByRole('button', { name: /^Skills/ }).click();
    await expect(page.getByText('Skills Controls')).toBeVisible();

    // Add a skill
    const skillInput = page.locator('input[placeholder="e.g. Python, Docker, PostgreSQL"]');
    const categorySelect = page.locator('select').filter({ hasText: 'Select Category' });

    await skillInput.fill('Playwright Test Skill');
    await categorySelect.selectOption('Languages');
    await page.getByRole('button', { name: 'Add Skill' }).click();
    await dismissValidationPopup(page);

    // Now type an unsaved draft
    await skillInput.fill('Unsaved Skill Draft');

    // Click Reset
    const tabResetBtn = page.getByRole('button', { name: 'Reset', exact: true });
    await tabResetBtn.click();

    // Verify confirmation modal
    await expect(page.getByText('Reset Skills')).toBeVisible();
    await page.getByRole('button', { name: 'Reset & Delete' }).click();

    // Verify feedback
    await expect(page.getByText(/Successfully reset Skills and deleted all saved records/i)).toBeVisible();
    await expect(skillInput).toHaveValue('');

    // Verify Skills badge count is 0
    const skillsTab = page.getByRole('button', { name: /^Skills/ });
    await expect(skillsTab).toContainText('0');

    // Reload page to verify persistence
    await page.reload();
    await page.getByRole('button', { name: 'Profile' }).click();
    await expect(page.getByText('Candidate Profile', { exact: true })).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button', { name: /^Skills/ })).toContainText('0');
  });

  test('Scenario 3: Projects Tab Reset deletes persisted projects and clears manual/github drafts', async ({ page }) => {
    await page.getByRole('button', { name: /^Projects/ }).click();
    await expect(page.getByText('Projects Controls')).toBeVisible();

    // Save a project
    await page.getByRole('button', { name: 'Manual Addition' }).click();
    const titleInput = page.locator('input[placeholder="e.g. Distributed Task Engine"]');
    const techInput = page.locator('input[placeholder="e.g. Python, PostgreSQL, Docker, Redis"]');
    const roleInput = page.locator('input[placeholder="e.g. Lead Architect / Creator"]');

    await titleInput.fill('E2E Distributed Architecture Engine');
    await techInput.fill('Go, Docker, Postgres');
    await roleInput.fill('Lead Engineer');
    await page.getByRole('button', { name: 'Add Project' }).click();
    await dismissValidationPopup(page);

    // Verify project appears in list
    await expect(page.getByRole('heading', { name: 'E2E Distributed Architecture Engine' }).first()).toBeVisible();

    // Type an unsaved draft
    await titleInput.fill('Unsaved Draft Project');

    // Click Reset
    const tabResetBtn = page.getByRole('button', { name: 'Reset', exact: true });
    await tabResetBtn.click();

    // Verify confirmation modal
    await expect(page.getByText('Reset Projects')).toBeVisible();
    await page.getByRole('button', { name: 'Reset & Delete' }).click();

    // Verify feedback and deletion
    await expect(page.getByText(/Successfully reset Projects and deleted all saved records/i)).toBeVisible();
    await expect(titleInput).toHaveValue('');
    await expect(page.getByRole('heading', { name: 'E2E Distributed Architecture Engine' })).toHaveCount(0);

    // Reload page to confirm database deletion
    await page.reload();
    await page.getByRole('button', { name: 'Profile' }).click();
    await expect(page.getByText('Candidate Profile', { exact: true })).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button', { name: /^Projects/ })).toContainText('0');
  });

  test('Scenario 4: Reset All deletes records across all Profile tabs and survives reload', async ({ page }) => {
    // 1. Add Personal Info
    const editPersonalBtn = page.getByRole('button', { name: 'Edit Personal Info' });
    if (await editPersonalBtn.isVisible().catch(() => false)) {
      await editPersonalBtn.click();
    }
    const headlineInput = page.locator('input[placeholder="e.g. Senior Full-Stack Engineer"]');
    await headlineInput.fill('Reset All Headline');
    await page.getByRole('button', { name: 'Save Personal Details' }).click();
    await dismissValidationPopup(page);

    // 2. Add Skill
    await page.getByRole('button', { name: /^Skills/ }).click();
    const skillInput = page.locator('input[placeholder="e.g. Python, Docker, PostgreSQL"]');
    const categorySelect = page.locator('select').filter({ hasText: 'Select Category' });
    await skillInput.fill('Reset All Skill');
    await categorySelect.selectOption('Languages');
    await page.getByRole('button', { name: 'Add Skill' }).click();
    await dismissValidationPopup(page);

    // 3. Add an unsaved draft on Projects
    await page.getByRole('button', { name: /^Projects/ }).click();
    await page.getByRole('button', { name: 'Manual Addition' }).click();
    const titleInput = page.locator('input[placeholder="e.g. Distributed Task Engine"]');
    await titleInput.fill('Draft Project For Reset All');

    // 4. Click Global Reset All
    const resetAllBtn = page.getByRole('button', { name: 'Reset All' });
    await resetAllBtn.click();

    // Verify modal
    await expect(page.getByText('Reset All Profile Data')).toBeVisible();
    await expect(page.getByText(/Your uploaded Master Resume PDF will NOT be deleted/i)).toBeVisible();

    // Confirm
    await page.getByRole('button', { name: 'Reset All Sections' }).click();

    // Verify feedback
    await expect(page.getByText(/Successfully reset all Profile sections and deleted all saved records/i)).toBeVisible({ timeout: 5000 });

    // Verify Projects input is cleared
    await expect(titleInput).toHaveValue('');

    // Check all tab badges are 0
    await expect(page.getByRole('button', { name: /^Skills/ })).toContainText('0');
    await expect(page.getByRole('button', { name: /^Projects/ })).toContainText('0');
    await expect(page.getByRole('button', { name: /^Experience/ })).toContainText('0');
    await expect(page.getByRole('button', { name: /^Education/ })).toContainText('0');
    await expect(page.getByRole('button', { name: /^Certifications/ })).toContainText('0');

    // 5. Reload page to verify all deletions persisted in database
    await page.reload();
    await page.getByRole('button', { name: 'Profile' }).click();
    await expect(page.getByText('Candidate Profile', { exact: true })).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button', { name: /^Skills/ })).toContainText('0');
    await expect(page.getByRole('button', { name: /^Projects/ })).toContainText('0');
    await expect(page.getByRole('button', { name: /^Experience/ })).toContainText('0');
    await expect(page.getByRole('button', { name: /^Education/ })).toContainText('0');
    await expect(page.getByRole('button', { name: /^Certifications/ })).toContainText('0');

    // 6. Verify Master Resume PDF card remains intact
    await expect(page.getByText('Master Resume PDF', { exact: true })).toBeVisible();
  });
});
