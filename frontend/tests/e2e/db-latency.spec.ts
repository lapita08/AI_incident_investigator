import { expect, test } from "@playwright/test";

test("database latency demo investigation workflow", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: /load db latency demo/i }).click();
  await expect(page.getByRole("heading", { name: /checkout api latency/i })).toBeVisible();

  await page.getByRole("button", { name: /run investigation/i }).click();
  await expect(page.getByText(/reporting workload likely created database contention/i)).toBeVisible();

  await page.getByRole("button", { name: "hypotheses" }).click();
  await expect(page.getByRole("button", { name: "METRIC-001" }).first()).toBeVisible();
  await page.getByRole("button", { name: "METRIC-001" }).first().click();
  await expect(page.getByRole("heading", { name: "METRIC-001" })).toBeVisible();
  await page.getByRole("button", { name: "Close" }).click();

  await page.getByRole("button", { name: "communications" }).click();
  await expect(page.getByText(/draft/i).first()).toBeVisible();

  const downloadTarget = page.getByRole("link", { name: /export/i });
  await expect(downloadTarget).toHaveAttribute("href", /format=markdown/);
});

