const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.V14_SMOKE_URL || 'http://127.0.0.1:4173/';

test.use({ viewport: { width: 1280, height: 800 } });

test('V14 shell bridges operate in the generated artifact', async ({ page }) => {
  const pageErrors = [];
  const consoleErrors = [];
  page.on('pageerror', (error) => pageErrors.push(String(error)));
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });

  await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => Boolean(
    globalThis.AtelierV14Shell?.notifications &&
    globalThis.AtelierV14Shell?.dialogs &&
    globalThis.AtelierV14Shell?.commands &&
    globalThis.AtelierV14Shell?.files
  ));

  await expect(page.locator('#atelier-v14-devtools-toggle')).toHaveText('V14 DEV');

  // Normalize possible first-run modal state, then exercise the real legacy keyboard
  // handler -> commandsDialog bridge -> dialog/command modules -> application DOM.
  const dialog = page.locator('#dialog');
  if (await dialog.evaluate((element) => element.open)) {
    const closeButton = dialog.locator('[data-action="close-dialog"]');
    if (await closeButton.count()) await closeButton.click();
    else await dialog.evaluate((element) => element.close());
  }

  await page.keyboard.press('Control+K');
  await expect(dialog).toHaveAttribute('open', '');
  await expect(page.locator('#dialog-title')).toHaveText('Find a tool or an object.');
  await expect(page.locator('#command-search')).toBeFocused();

  await page.locator('#command-search').fill('Export deliverables');
  const exportCommand = page.locator('#command-results [data-command="export"]');
  await expect(exportCommand).toHaveCount(1);
  await expect(exportCommand).toContainText('Export deliverables');

  await dialog.locator('[data-action="close-dialog"]').click();
  await expect(dialog).not.toHaveAttribute('open', '');

  // Exercise migrated services directly inside the actual browser/runtime DOM.
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
