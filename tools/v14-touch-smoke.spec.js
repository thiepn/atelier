const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.V14_SMOKE_URL || 'http://127.0.0.1:4173/';

async function waitForShell(page) {
  await page.waitForFunction(() => Boolean(
    globalThis.AtelierV14Shell?.notifications &&
    globalThis.AtelierV14Shell?.dialogs &&
    globalThis.AtelierV14Shell?.commands &&
    globalThis.AtelierV14Shell?.files &&
    globalThis.AtelierV14Shell?.icons &&
    globalThis.AtelierV14Shell?.text &&
    globalThis.AtelierV14Shell?.units
  ));
}

async function closeOpenDialog(page) {
  const dialog = page.locator('#dialog');
  if (await dialog.evaluate(element => element.open)) {
    const close = dialog.locator('[data-action="close-dialog"]');
    if (await close.count()) await close.click();
    else await dialog.evaluate(element => element.close());
  }
}

async function openCommandModule(page) {
  return page.evaluate(() => {
    const shell = globalThis.AtelierV14Shell;
    const dialogAdapter = { closeContextMenu() {}, setModalReturn() {} };
    return shell.commands.open({
      icon() { return '<svg aria-hidden="true"></svg>'; },
      esc: shell.text.escapeHtml,
      commands: [['export', 'Export deliverables', 'download']],
      catalog: {},
      openDialog(title, html) {
        return shell.dialogs.open(title, html, {}, dialogAdapter);
      },
    });
  });
}

test('V14 touch shell works on WebKit-sized phone and tablet profiles', async ({ page }, testInfo) => {
  const pageErrors = [];
  const consoleErrors = [];
  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });

  await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  await waitForShell(page);
  await closeOpenDialog(page);

  expect(await page.evaluate(() => navigator.maxTouchPoints || 0)).toBeGreaterThan(0);
  const expected = testInfo.project.name === 'webkit-tablet'
    ? { width: 834, height: 1194 }
    : { width: 390, height: 844 };
  expect(page.viewportSize()).toEqual(expected);

  const overflow = await page.evaluate(() => Math.max(
    0,
    document.documentElement.scrollWidth - innerWidth,
    document.body?.scrollWidth - innerWidth || 0
  ));
  expect(overflow, `horizontal overflow on ${testInfo.project.name}`).toBeLessThanOrEqual(1);

  const toggle = page.locator('#atelier-v14-devtools-toggle');
  const panel = page.locator('#atelier-v14-devtools-panel');
  await expect(toggle).toBeVisible();
  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-expanded', 'true');
  await expect(panel).toBeVisible();
  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await expect(panel).toBeHidden();

  expect(await openCommandModule(page)).toBe(true);
  const dialog = page.locator('#dialog');
  await expect(dialog).toHaveAttribute('open', '');
  await expect(dialog).toHaveAttribute('aria-modal', 'true');
  await expect(page.locator('#dialog-title')).toHaveText('Find a tool or an object.');
  const search = page.locator('#command-search');
  await expect(search).toBeVisible();
  await expect(search).toHaveAttribute('aria-label', 'Search commands and objects');
  await search.fill('Export deliverables');
  const result = page.locator('#command-results [data-command="export"]');
  await expect(result).toHaveCount(1);
  await expect(result).toContainText('Export deliverables');
  await dialog.locator('[data-action="close-dialog"]').click();
  await expect(dialog).not.toHaveAttribute('open', '');

  const helperProbe = await page.evaluate(() => ({
    safeName: globalThis.AtelierV14Shell.files.safeName('Café / Client Plan'),
    html: globalThis.AtelierV14Shell.text.escapeHtml(`<b>'&'</b>`),
    dimension: globalThis.AtelierV14Shell.units.formatDimension(1, 'ft-in'),
  }));
  expect(helperProbe).toEqual({
    safeName: 'cafe-client-plan',
    html: '&lt;b&gt;&#39;&amp;&#39;&lt;/b&gt;',
    dimension: '3′ 3.375″',
  });

  expect(pageErrors, `page errors: ${pageErrors.join('\n')}`).toEqual([]);
  expect(consoleErrors, `console errors: ${consoleErrors.join('\n')}`).toEqual([]);
});
