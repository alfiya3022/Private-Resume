import { test, expect } from "@playwright/test";
import path from "path";

async function ensureLoggedOut(page) {
  await page.goto("http://localhost:5174/auth");
  await page.waitForLoadState("networkidle");

  const signOutBtn = page.getByRole("button", { name: "Sign Out" });
  if (await signOutBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
    await signOutBtn.click();
    await page.waitForLoadState("networkidle");
  }

  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
  await page.goto("http://localhost:5174/auth");
  await page.waitForLoadState("networkidle");
}

async function loginAsDemo(page) {
  await page.goto("http://localhost:5174/auth");
  await page.waitForLoadState("networkidle");

  const signOutBtn = page.getByRole("button", { name: "Sign Out" });
  if (await signOutBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
    return;
  }

  const demoBtn = page.locator('[data-testid="auth-demo-btn"]');
  if (await demoBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
    await demoBtn.click();
  } else {
    await page.locator('input[type="email"]').fill("demo@Verity.local");
    await page.locator('input[type="password"]').fill("Password123!");
  }

  await page.locator('[data-testid="auth-submit-btn"]').click();
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500);
}

test.describe("First-Time User Onboarding & Routing Specification Tests", () => {
  test("1. Existing user login → Workspace Stage 1", async ({ page }) => {
    await ensureLoggedOut(page);

    await page.locator('input[type="email"]').fill("demo@Verity.local");
    await page.locator('input[type="password"]').fill("Password123!");
    await page.locator('[data-testid="auth-submit-btn"]').click();
    await page.waitForLoadState("networkidle");

    // Verify direct navigation to default workspace
    await expect(
      page.getByText("Add Job Description & Master Inputs"),
    ).toBeVisible({ timeout: 10000 });
    // Verify Welcome Guide is NOT shown
    await expect(page.getByText("Welcome to Verity!")).not.toBeVisible();
    await expect(
      page.locator(".fixed.inset-0.bg-black\\/60"),
    ).not.toBeVisible();
  });

  test("2 & 3. New user registration → Dedicated Welcome Guide page (not a modal over workspace)", async ({
    page,
  }) => {
    await ensureLoggedOut(page);

    const testEmail = `newuser_${Date.now()}@test.local`;
    await page.locator('[data-testid="auth-tab-register"]').click();
    await page
      .locator('input[placeholder="Enter your name"]')
      .fill("Test New User");
    await page.locator('input[type="email"]').fill(testEmail);
    await page.locator('input[type="password"]').fill("Password123!");
    await page.locator('[data-testid="auth-submit-btn"]').click();
    await page.waitForLoadState("networkidle");

    // Verify navigation to dedicated /onboarding page
    await expect(page.getByText("Welcome to Verity!")).toBeVisible({
      timeout: 10000,
    });
    await expect(page).toHaveURL(/.*onboarding/);

    // Verify Workspace is NOT rendered behind it
    await expect(
      page.getByText("Add Job Description & Master Inputs"),
    ).not.toBeVisible();
    // Verify it is NOT a modal overlay
    await expect(
      page.locator(".fixed.inset-0.bg-black\\/60"),
    ).not.toBeVisible();

    // Verify all 3 required action buttons exist
    await expect(
      page.locator('[data-testid="onboarding-add-resume-btn"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="onboarding-skip-btn"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="onboarding-later-btn"]'),
    ).toBeVisible();
  });

  test("4 & 5. Add Master Resume → Existing upload flow → Successful upload → Workspace Stage 1", async ({
    page,
  }) => {
    test.setTimeout(90000);
    await ensureLoggedOut(page);

    const testEmail = `newuser_up_${Date.now()}@test.local`;
    await page.locator('[data-testid="auth-tab-register"]').click();
    await page
      .locator('input[placeholder="Enter your name"]')
      .fill("Upload Test User");
    await page.locator('input[type="email"]').fill(testEmail);
    await page.locator('input[type="password"]').fill("Password123!");
    await page.locator('[data-testid="auth-submit-btn"]').click();
    await page.waitForLoadState("networkidle");

    // Onboarding page active
    await expect(page.getByText("Welcome to Verity!")).toBeVisible({
      timeout: 10000,
    });

    // Click "Add Master Resume"
    await page.locator('[data-testid="onboarding-add-resume-btn"]').click();
    await page.waitForLoadState("networkidle");

    // 4. Verify routed to Profile master resume upload flow
    await expect(page.getByText("Master Resume PDF")).toBeVisible({
      timeout: 10000,
    });
    await expect(page).toHaveURL(/.*profile/);
    await expect(
      page.getByText("First-Time Setup:", { exact: false }),
    ).toBeVisible();

    // Set input file using real test PDF fixture
    const pdfPath = path.resolve(
      "../backend/tests/fixtures/master_resume_reference.pdf",
    );
    const fileInput = page.locator('input[type="file"][accept=".pdf"]');
    await fileInput.setInputFiles(pdfPath);

    // 5. Verify upload finishes and routes to Workspace Stage 1
    await expect(
      page.getByText("Add Job Description & Master Inputs"),
    ).toBeVisible({ timeout: 60000 });
  });

  test("6. Skip for now → Workspace Stage 1", async ({ page }) => {
    await ensureLoggedOut(page);

    const testEmail = `newuser_skip_${Date.now()}@test.local`;
    await page.locator('[data-testid="auth-tab-register"]').click();
    await page
      .locator('input[placeholder="Enter your name"]')
      .fill("Skip Test User");
    await page.locator('input[type="email"]').fill(testEmail);
    await page.locator('input[type="password"]').fill("Password123!");
    await page.locator('[data-testid="auth-submit-btn"]').click();
    await page.waitForLoadState("networkidle");

    await expect(page.getByText("Welcome to Verity!")).toBeVisible({
      timeout: 10000,
    });

    // Click "Skip for now"
    await page.locator('[data-testid="onboarding-skip-btn"]').click();
    await page.waitForLoadState("networkidle");

    // Verify redirected to Workspace Stage 1
    await expect(
      page.getByText("Add Job Description & Master Inputs"),
    ).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("Welcome to Verity!")).not.toBeVisible();
  });

  test("7. I'll do this later → Workspace Stage 1", async ({ page }) => {
    await ensureLoggedOut(page);

    const testEmail = `newuser_later_${Date.now()}@test.local`;
    await page.locator('[data-testid="auth-tab-register"]').click();
    await page
      .locator('input[placeholder="Enter your name"]')
      .fill("Later Test User");
    await page.locator('input[type="email"]').fill(testEmail);
    await page.locator('input[type="password"]').fill("Password123!");
    await page.locator('[data-testid="auth-submit-btn"]').click();
    await page.waitForLoadState("networkidle");

    await expect(page.getByText("Welcome to Verity!")).toBeVisible({
      timeout: 10000,
    });

    // Click "I'll do this later"
    await page.locator('[data-testid="onboarding-later-btn"]').click();
    await page.waitForLoadState("networkidle");

    // Verify redirected to Workspace Stage 1
    await expect(
      page.getByText("Add Job Description & Master Inputs"),
    ).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("Welcome to Verity!")).not.toBeVisible();
  });

  test("8. Existing user with no master resume → No automatic welcome guide", async ({
    page,
  }) => {
    // Register user and skip onboarding so user exists with 0 resumes
    await ensureLoggedOut(page);
    const testEmail = `noresume_${Date.now()}@test.local`;
    await page.locator('[data-testid="auth-tab-register"]').click();
    await page
      .locator('input[placeholder="Enter your name"]')
      .fill("No Resume User");
    await page.locator('input[type="email"]').fill(testEmail);
    await page.locator('input[type="password"]').fill("Password123!");
    await page.locator('[data-testid="auth-submit-btn"]').click();
    await page.waitForLoadState("networkidle");

    await page.locator('[data-testid="onboarding-skip-btn"]').click();
    await page.waitForLoadState("networkidle");
    await expect(
      page.getByText("Add Job Description & Master Inputs"),
    ).toBeVisible();

    // Sign Out
    await page.goto("http://localhost:5174/auth");
    await page.getByRole("button", { name: "Sign Out" }).click();
    await page.waitForLoadState("networkidle");

    // Sign back in as existing user with 0 resumes
    await page.locator('input[type="email"]').fill(testEmail);
    await page.locator('input[type="password"]').fill("Password123!");
    await page.locator('[data-testid="auth-submit-btn"]').click();
    await page.waitForLoadState("networkidle");

    // Verify goes straight to Workspace Stage 1, NO welcome guide
    await expect(
      page.getByText("Add Job Description & Master Inputs"),
    ).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("Welcome to Verity!")).not.toBeVisible();
  });

  test("9. Refreshing an existing session does not incorrectly trigger onboarding", async ({
    page,
  }) => {
    await loginAsDemo(page);
    await page.goto("http://localhost:5174/");
    await page.waitForLoadState("networkidle");

    await expect(
      page.getByText("Add Job Description & Master Inputs"),
    ).toBeVisible();

    // Reload page
    await page.reload();
    await page.waitForLoadState("networkidle");

    // Verify still in Workspace Stage 1, NO onboarding
    await expect(
      page.getByText("Add Job Description & Master Inputs"),
    ).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("Welcome to Verity!")).not.toBeVisible();
  });

  test("10. Welcome route is protected from unauthenticated users", async ({
    page,
  }) => {
    await ensureLoggedOut(page);

    // Attempt direct navigation to /onboarding while unauthenticated
    await page.goto("http://localhost:5174/onboarding");
    await page.waitForLoadState("networkidle");

    // Verify redirected to /auth
    await expect(page).toHaveURL(/.*auth/);
    await expect(page.locator('[data-testid="auth-submit-btn"]')).toBeVisible({
      timeout: 10000,
    });
    await expect(page.getByText("Welcome to Verity!")).not.toBeVisible();
  });

  test("Workflow State Bug A: Refresh preserves workspace stage and does not reset to Stage 1", async ({
    page,
  }) => {
    await loginAsDemo(page);

    await page.goto("http://localhost:5174/");
    await page.waitForLoadState("networkidle");

    await page.locator('input[placeholder="e.g. Stripe"]').fill("Stripe");
    await page
      .locator('input[placeholder="e.g. Software Engineer"]')
      .fill("Software Engineer");
    await page
      .locator(
        'textarea[placeholder="Paste the target job description here..."]',
      )
      .fill("Looking for a Software Engineer skilled in Python and React.");
    await page
      .getByRole("button", { name: /Save & Analyze Job Description/i })
      .click();
    await page.waitForLoadState("networkidle");

    await expect(page.getByText("Stage 2", { exact: false })).toBeVisible({
      timeout: 10000,
    });
    await expect(page).toHaveURL(/.*stage=2/);

    await page.reload();
    await page.waitForLoadState("networkidle");

    await expect(page.getByText("Stage 2", { exact: false })).toBeVisible({
      timeout: 10000,
    });
    await expect(page).toHaveURL(/.*stage=2/);
  });

  test("Workflow State Bug B: Evidence navigation preserves originating workspace stage on return", async ({
    page,
  }) => {
    await loginAsDemo(page);

    await page.goto("http://localhost:5174/profile?from=workspace&stage=3");
    await page.waitForLoadState("networkidle");

    const returnBtn = page.getByRole("button", {
      name: /Return to Workspace/i,
    });
    await expect(returnBtn).toBeVisible({ timeout: 10000 });
    expect(await returnBtn.textContent()).toContain("Stage 3");

    await returnBtn.click();
    await page.waitForLoadState("networkidle");

    await expect(page).toHaveURL(/.*stage=3/);
    await expect(page.getByText("Stage 3", { exact: false })).toBeVisible({
      timeout: 10000,
    });
  });
});
