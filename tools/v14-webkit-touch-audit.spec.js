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

async function start(page) {
  await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  await waitForShell(page);
  const dialog = page.locator('#dialog');
  if (await dialog.evaluate(element => element.open)) {
    const close = dialog.locator('[data-action="close-dialog"]');
    if (await close.count()) await close.click();
    else await dialog.evaluate(element => element.close());
  }
}

async function openCommands(page) {
  return page.evaluate(() => {
    const shell = globalThis.AtelierV14Shell;
    const dialogAdapter = { closeContextMenu() {}, setModalReturn() {} };
    return shell.commands.open({
      icon() { return '<svg aria-hidden="true"></svg>'; },
      esc: shell.text.escapeHtml,
      commands: [['export', 'Export deliverables', 'download']],
      catalog: {},
      openDialog(title, html) { return shell.dialogs.open(title, html, {}, dialogAdapter); },
    });
  });
}

test('webkit touch environment and horizontal overflow', async ({ page }, testInfo) => {
  await start(page);
  const metrics = await page.evaluate(() => ({
    touchPoints: navigator.maxTouchPoints || 0,
    innerWidth,
    innerHeight,
    docWidth: document.documentElement.scrollWidth,
    bodyWidth: document.body?.scrollWidth || 0,
  }));
  expect(metrics.touchPoints, `touch points: ${JSON.stringify(metrics)}`).toBeGreaterThan(0);
  expect(Math.max(0, metrics.docWidth - metrics.innerWidth, metrics.bodyWidth - metrics.innerWidth), `metrics: ${JSON.stringify(metrics)}`).toBeLessThanOrEqual(1);
  expect(page.viewportSize(), `project=${testInfo.project.name} metrics=${JSON.stringify(metrics)}`).toBeTruthy();
});

test('webkit touch diagnostics toggle', async ({ page }) => {
  await start(page);
  const toggle = page.locator('#atelier-v14-devtools-toggle');
  const panel = page.locator('#atelier-v14-devtools-panel');
  await expect(toggle).toBeVisible();
  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-expanded', 'true');
  await expect(panel).toBeVisible();
  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await expect(panel).toBeHidden();
});

test('webkit touch command and dialog modules', async ({ page }) => {
  await start(page);
  expect(await openCommands(page)).toBe(true);
  const dialog = page.locator('#dialog');
  await expect(dialog).toHaveAttribute('open', '');
  await expect(dialog).toHaveAttribute('aria-modal', 'true');
  const search = page.locator('#command-search');
  await expect(search).toBeVisible();
  await search.fill('Export deliverables');
  await expect(page.locator('#command-results [data-command="export"]')).toContainText('Export deliverables');
  await dialog.locator('[data-action="close-dialog"]').click();
  await expect(dialog).not.toHaveAttribute('open', '');
});

test('webkit touch helpers and runtime errors', async ({ page }) => {
  const pageErrors = [];
  const consoleErrors = [];
  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  await start(page);
  const probe = await page.evaluate(() => ({
    safeName: globalThis.AtelierV14Shell.files.safeName('Café / Client Plan'),
    dimension: globalThis.AtelierV14Shell.units.formatDimension(1, 'ft-in'),
    html: globalThis.AtelierV14Shell.text.escapeHtml(`<b>'&'</b>`),
  }));
  expect(probe).toEqual({
    safeName: 'cafe-client-plan',
    dimension: '3′ 3.375″',
    html: '&lt;b&gt;&#39;&amp;&#39;&lt;/b&gt;',
  });
  expect(pageErrors).toEqual([]);
  expect(consoleErrors).toEqual([]);
});
