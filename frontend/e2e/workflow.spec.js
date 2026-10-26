import { test, expect } from "@playwright/test";

test.describe("Verity E2E Candidate Workflow", () => {
  test("1. System Health & Branding Smoke Test", async ({ page }) => {
    await page.goto("http://localhost:5174/");

    // Check Sidebar Branding
    await expect(
      page.locator("aside").getByText("Verity", { exact: true }),
    ).toBeVisible();

    // Check Vertical Navigation Tabs
    await expect(page.getByRole("button", { name: "Workspace" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Profile" })).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Applications" }),
    ).toBeVisible();

    // Check Subsystem Connection
    await expect(page.locator("text=API Connected")).toBeVisible({
      timeout: 10000,
    });
  });

  test("2. Complete End-to-End Candidate Journey", async ({ page }) => {
    await page.goto("http://localhost:5174/");

    // 1. Sign In
    const authNavButton = page.locator("aside button").last();
    await authNavButton.click();

    const signOutBtn = page.getByRole("button", { name: "Sign Out" });
    if (await signOutBtn.isVisible({ timeout: 1500 }).catch(() => false)) {
      await signOutBtn.click();
      await page.waitForTimeout(500);
    }

    await expect(page.locator("text=Welcome to Verity")).toBeVisible();
    await page.locator('input[type="email"]').fill("demo@Verity.local");
    await page.locator('input[type="password"]').fill("Password123!");
    await page.getByRole("button", { name: "Sign In", exact: true }).click();

    // Verify authentication reflected in sidebar
    await expect(page.locator("aside").getByText("Alex Morgan")).toBeVisible({
      timeout: 10000,
    });

    // 2. Profile Inspection
    await page.getByRole("button", { name: "Profile" }).click();
    await expect(
      page.getByText("Master Resume PDF", { exact: true }),
    ).toBeVisible({ timeout: 10000 });
    await expect(
      page.getByRole("button", { name: "Personal Info", exact: true }),
    ).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole("button", { name: /^Skills/ })).toBeVisible();

    // 3. Workspace Inspection
    await page.getByRole("button", { name: "Workspace" }).click();
    await expect(page.getByText("1. Add Inputs")).toBeVisible({
      timeout: 10000,
    });
    await expect(page.getByText("Target Opportunity Details")).toBeVisible();

    // 4. Application Pipeline Inspection
    await page.getByRole("button", { name: "Applications" }).click();
    await expect(page.getByText("Application Pipeline")).toBeVisible({
      timeout: 10000,
    });
    await expect(
      page.getByRole("button", { name: "All Applications" }),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Applied" })).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Interviewing" }),
    ).toBeVisible();

    // 5. Clean Sign Out
    await page.locator("aside button").last().click();
    await page.getByRole("button", { name: "Sign Out" }).click();
    await expect(page.locator("text=Welcome to Verity")).toBeVisible();
  });
});
