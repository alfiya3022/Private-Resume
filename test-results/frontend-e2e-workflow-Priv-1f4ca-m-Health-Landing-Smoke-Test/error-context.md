# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: frontend\e2e\workflow.spec.js >> PrivateResume End-to-End User Journeys >> 1. System Health & Landing Smoke Test
- Location: frontend\e2e\workflow.spec.js:4:3

# Error details

```
Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
Call log:
  - navigating to "/", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('PrivateResume End-to-End User Journeys', () => {
  4  |   test('1. System Health & Landing Smoke Test', async ({ page }) => {
> 5  |     await page.goto('/');
     |                ^ Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
  6  | 
  7  |     // Check Branding
  8  |     await expect(page.locator('text=PrivateResume')).toBeVisible();
  9  |     await expect(page.locator('text=Local-First V1')).toBeVisible();
  10 | 
  11 |     // Check Navigation Tabs
  12 |     await expect(page.getByRole('button', { name: 'Workspace' })).toBeVisible();
  13 |     await expect(page.getByRole('button', { name: 'Profile' })).toBeVisible();
  14 |     await expect(page.getByRole('button', { name: 'Applications' })).toBeVisible();
  15 | 
  16 |     // Check Subsystem Connection
  17 |     await expect(page.locator('text=API Connected')).toBeVisible({ timeout: 15000 });
  18 |   });
  19 | 
  20 |   test('2. Candidate Authentication Journey', async ({ page }) => {
  21 |     await page.goto('/');
  22 | 
  23 |     // Switch to Auth tab
  24 |     await page.getByRole('button', { name: 'Auth' }).click();
  25 |     await expect(page.locator('text=Sign In to PrivateResume')).toBeVisible();
  26 | 
  27 |     // Fill in demo candidate credentials
  28 |     await page.locator('input[type="email"]').fill('demo@privateresume.local');
  29 |     await page.locator('input[type="password"]').fill('Password123!');
  30 |     await page.getByRole('button', { name: 'Sign In' }).click();
  31 | 
  32 |     // Verify successful login
  33 |     await expect(page.locator('text=Alex Morgan').first()).toBeVisible({ timeout: 10000 });
  34 |   });
  35 | 
  36 |   test('3. Master Profile Inspection', async ({ page }) => {
  37 |     await page.goto('/');
  38 | 
  39 |     // Switch to Profile tab
  40 |     await page.getByRole('button', { name: 'Profile' }).click();
  41 |     await expect(page.locator('text=Candidate Master Profile')).toBeVisible();
  42 | 
  43 |     // Verify sub-sections exist
  44 |     await expect(page.locator('text=Technical Skills')).toBeVisible();
  45 |     await expect(page.locator('text=Work History')).toBeVisible();
  46 |     await expect(page.locator('text=Education')).toBeVisible();
  47 |   });
  48 | 
  49 |   test('4. Application Tracking Pipeline', async ({ page }) => {
  50 |     await page.goto('/');
  51 | 
  52 |     // Switch to Applications tab
  53 |     await page.getByRole('button', { name: 'Applications' }).click();
  54 |     await expect(page.locator('text=Application Pipeline')).toBeVisible();
  55 | 
  56 |     // Verify filter tabs are rendered
  57 |     await expect(page.getByRole('button', { name: 'All Applications' })).toBeVisible();
  58 |     await expect(page.getByRole('button', { name: 'Applied' })).toBeVisible();
  59 |     await expect(page.getByRole('button', { name: 'Interviewing' })).toBeVisible();
  60 |   });
  61 | });
  62 | 
```