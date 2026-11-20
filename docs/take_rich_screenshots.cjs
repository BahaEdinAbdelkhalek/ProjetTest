const { chromium } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
  const out = process.env.SCREENSHOT_DIR || 'c:/Users/TUF/Desktop/ProjetTest/ProjetTest/docs/app_screenshots';
  const base = process.env.BASE_URL || 'http://localhost:4200';
  fs.mkdirSync(out, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 950 },
    deviceScaleFactor: 1
  });
  const page = await context.newPage();

  // 1. Dashboard as sales
  await page.goto(base);
  await page.getByLabel('Username').fill('sales');
  await page.getByLabel('Password').fill('Sales123!');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.getByText(/Signed in as sales/).waitFor({ timeout: 10000 });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(out, '01-dashboard-sales.png'), fullPage: false });
  console.log('Saved 01-dashboard-sales.png');

  // 2. Products table
  await page.getByRole('button', { name: 'Products' }).click();
  await page.locator('h2').filter({ hasText: 'products' }).waitFor();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(out, '02-products.png'), fullPage: false });
  console.log('Saved 02-products.png');

  // 3. Customers table
  await page.getByRole('button', { name: 'Customers' }).click();
  await page.locator('h2').filter({ hasText: 'customers' }).waitFor();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(out, '03-customers.png'), fullPage: false });
  console.log('Saved 03-customers.png');

  // 4. Orders with View items expanded
  await page.getByRole('button', { name: 'Orders' }).click();
  await page.locator('h2').filter({ hasText: 'orders' }).waitFor();
  await page.waitForTimeout(1000);
  // click first 'View items' if present
  const viewButtons = page.getByRole('button', { name: 'View items' });
  if (await viewButtons.count() > 0) {
    await viewButtons.first().click();
    await page.waitForTimeout(500);
  }
  await page.screenshot({ path: path.join(out, '04-orders.png'), fullPage: false });
  console.log('Saved 04-orders.png');

  // 5. Admin Audit Trail
  await page.getByLabel('Username').fill('admin');
  await page.getByLabel('Password').fill('Admin123!');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.getByText(/Signed in as admin/).waitFor({ timeout: 10000 });
  await page.getByRole('button', { name: 'Audit' }).click();
  await page.locator('h2').filter({ hasText: 'audit' }).waitFor();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(out, '05-audit-admin.png'), fullPage: false });
  console.log('Saved 05-audit-admin.png');

  // 6. Viewer Restricted View (Proving RBAC)
  await page.getByLabel('Username').fill('viewer');
  await page.getByLabel('Password').fill('View123!');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.getByText(/Signed in as viewer/).waitFor({ timeout: 10000 });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(out, '06-viewer-restricted.png'), fullPage: false });
  console.log('Saved 06-viewer-restricted.png');

  await browser.close();
  console.log('All rich screenshots taken successfully!');
})();
