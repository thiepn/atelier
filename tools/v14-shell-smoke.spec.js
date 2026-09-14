const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.V14_SMOKE_URL || 'http://127.0.0.1:4173/';

async function waitForV14Shell(page) {
  await page.waitForFunction(() => Boolean(
    globalThis.AtelierV14Shell?.notifications &&
    globalThis.AtelierV14Shell?.dialogs &&
    globalThis.AtelierV14Shell?.commands &&
    globalThis.AtelierV14Shell?.files
  ));
}

async function normalizeDialog(page) {
  const dialog = page.locator('#dialog');
  if (await dialog.evaluate((element) => element.open)) {
    const closeButton = dialog.locator('[data-action="close-dialog"]');
    if (await closeButton.count()) await closeButton.click();
    else await dialog.evaluate((element) => element.close());
    await expect(dialog).not.toHaveAttribute('open', '');
    await page.waitForTimeout(50);
  }
}

function collectRuntimeErrors(page) {
  const pageErrors = [];
  const consoleErrors = [];
  page.on('pageerror', (error) => pageErrors.push(String(error)));
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  return { pageErrors, consoleErrors };
}

test('V14 shell bridges remain responsive, accessible and cross-browser compatible', async ({ page }, testInfo) => {
  const { pageErrors, consoleErrors } = collectRuntimeErrors(page);

  await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  await waitForV14Shell(page);
  await normalizeDialog(page);

  const toggle = page.locator('#atelier-v14-devtools-toggle');
  const panel = page.locator('#atelier-v14-devtools-panel');
  const dialog = page.locator('#dialog');

  await expect(toggle).toHaveText('V14 DEV');
  await expect(toggle).toHaveAttribute('aria-controls', 'atelier-v14-devtools-panel');
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await expect(panel).toHaveAttribute('aria-labelledby', 'atelier-v14-devtools-panel-title');
  await expect(panel.locator('.v14-warning')).toContainText('not V13.3.1 production certification');

  // Responsive gate: the document must not create meaningful horizontal page overflow.
  const overflowPx = await page.evaluate(() => Math.max(
    0,
    document.documentElement.scrollWidth - window.innerWidth,
    document.body?.scrollWidth - window.innerWidth || 0
  ));
  expect(overflowPx).toBeLessThanOrEqual(1);

  if (testInfo.project.name === 'chromium-mobile') {
    expect(await page.evaluate(() => navigator.maxTouchPoints || 0)).toBeGreaterThan(0);
    const viewport = page.viewportSize();
    expect(viewport).toEqual({ width: 390, height: 844 });
  }

  // Keyboard accessibility for the development diagnostics surface.
  await toggle.focus();
  await expect(toggle).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(toggle).toHaveAttribute('aria-expanded', 'true');
  await expect(panel).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(panel).toBeHidden();
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await expect(toggle).toBeFocused();

  // Exercise the real legacy shortcut -> command bridge -> modular dialog path.
  await page.keyboard.press('Control+K');
  await expect(dialog).toHaveAttribute('open', '');
  await expect(dialog).toHaveAttribute('aria-modal', 'true');
  await expect(page.locator('#dialog-title')).toHaveText('Find a tool or an object.');
  const search = page.locator('#command-search');
  await expect(search).toHaveAttribute('aria-label', 'Search commands and objects');
  await expect(search).toBeFocused();

  // Native Escape/cancel must close through the modular dialog bridge and restore focus.
  await page.keyboard.press('Escape');
  await expect(dialog).not.toHaveAttribute('open', '');
  await expect(toggle).toBeFocused();

  // Reopen and verify preserved command action contracts.
  await page.keyboard.press('Control+K');
  await expect(search).toBeFocused();
  await search.fill('Export deliverables');
  const exportCommand = page.locator('#command-results [data-command="export"]');
  await expect(exportCommand).toHaveCount(1);
  await expect(exportCommand).toContainText('Export deliverables');
  await dialog.locator('[data-action="close-dialog"]').click();
  await expect(dialog).not.toHaveAttribute('open', '');
  await expect(toggle).toBeFocused();

  // Exercise migrated services inside the actual browser/runtime DOM.
  await page.evaluate(() => globalThis.AtelierV14Shell.notifications.toast('V14 browser smoke'));
  await expect(page.locator('#toast')).toHaveText('V14 browser smoke');
  await expect(page.locator('#toast')).toHaveClass(/show/);

  const safeName = await page.evaluate(() => globalThis.AtelierV14Shell.files.safeName('Café / Client Plan'));
  expect(safeName).toBe('cafe-client-plan');

  const versions = await page.evaluate(() => ({
    notifications: globalThis.AtelierV14Shell.notifications.version,
    dialogs: globalThis.AtelierV14Shell.dialogs.version,
    commands: globalThis.AtelierV14Shell.commands.version,
    files: globalThis.AtelierV14Shell.files.version,
  }));
  expect(versions).toEqual({
    notifications: '14.0.0-dev.3',
    dialogs: '14.0.0-dev.6',
    commands: '14.0.0-dev.4',
    files: '14.0.0-dev.5',
  });

  expect(pageErrors, `page errors: ${pageErrors.join('\n')}`).toEqual([]);
  expect(consoleErrors, `console errors: ${consoleErrors.join('\n')}`).toEqual([]);
});
