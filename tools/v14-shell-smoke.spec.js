const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.V14_SMOKE_URL || 'http://127.0.0.1:4173/';

async function waitForV14Shell(page) {
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

async function openCommandPaletteThroughModule(page) {
  const opened = await page.evaluate(() => {
    const shell = globalThis.AtelierV14Shell;
    globalThis.__v14SmokeModalReturn = null;
    const dialogAdapter = {
      closeContextMenu() {},
      setModalReturn(value) { globalThis.__v14SmokeModalReturn = value; },
    };
    const commandAdapter = {
      icon() { return '<svg aria-hidden="true"></svg>'; },
      esc: shell.text.escapeHtml,
      commands: [['export', 'Export deliverables', 'download']],
      catalog: {},
      openDialog(title, html) {
        return shell.dialogs.open(title, html, {}, dialogAdapter);
      },
    };
    return shell.commands.open(commandAdapter);
  });
  expect(opened).toBe(true);
}

async function tapCenter(page, locator) {
  await expect(locator).toBeVisible();
  const box = await locator.boundingBox();
  expect(box).not.toBeNull();
  await page.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2);
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

async function assertCoreHelpers(page) {
  const safeName = await page.evaluate(() => globalThis.AtelierV14Shell.files.safeName('Café / Client Plan'));
  expect(safeName).toBe('cafe-client-plan');

  const iconProbe = await page.evaluate(() => globalThis.AtelierV14Shell.icons.render(
    'search',
    20,
    { cube: 'fallback', search: 'M1 1L2 2' }
  ));
  expect(iconProbe).toBe('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 1L2 2"/></svg>');

  const escaped = await page.evaluate(() => ({
    html: globalThis.AtelierV14Shell.text.escapeHtml(`<script a="1">'&'</script>`),
    xml: globalThis.AtelierV14Shell.text.escapeXml(`<tag a="1">'&'</tag>`),
  }));
  expect(escaped).toEqual({
    html: '&lt;script a=&quot;1&quot;&gt;&#39;&amp;&#39;&lt;/script&gt;',
    xml: '&lt;tag a=&quot;1&quot;&gt;&apos;&amp;&apos;&lt;/tag&gt;',
  });

  const unitProbe = await page.evaluate(() => {
    const format = globalThis.AtelierV14Shell.units.formatDimension;
    return {
      metres: format(1.234, 'm'),
      feet: format(1, 'ft'),
      inches: format(1, 'in'),
      centimetres: format(1.2, 'cm'),
      millimetres: format(1.2345, 'mm'),
      feetInches: format(1, 'ft-in'),
    };
  });
  expect(unitProbe).toEqual({
    metres: '1.23 m',
    feet: '3.28 ft',
    inches: '39.37 in',
    centimetres: '120.00 cm',
    millimetres: '1235 mm',
    feetInches: '3′ 3.375″',
  });
}

async function assertModuleVersions(page) {
  const versions = await page.evaluate(() => ({
    notifications: globalThis.AtelierV14Shell.notifications.version,
    dialogs: globalThis.AtelierV14Shell.dialogs.version,
    commands: globalThis.AtelierV14Shell.commands.version,
    files: globalThis.AtelierV14Shell.files.version,
    icons: globalThis.AtelierV14Shell.icons.version,
    text: globalThis.AtelierV14Shell.text.version,
    units: globalThis.AtelierV14Shell.units.version,
  }));
  expect(versions).toEqual({
    notifications: '14.0.0-dev.3',
    dialogs: '14.0.0-dev.6',
    commands: '14.0.0-dev.4',
    files: '14.0.0-dev.5',
    icons: '14.0.0-dev.9',
    text: '14.0.0-dev.10',
    units: '14.0.0-dev.12',
  });
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

  const overflowPx = await page.evaluate(() => Math.max(
    0,
    document.documentElement.scrollWidth - window.innerWidth,
    document.body?.scrollWidth - window.innerWidth || 0
  ));
  expect(overflowPx).toBeLessThanOrEqual(1);

  const touchProjects = {
    'chromium-mobile': { width: 390, height: 844 },
    'webkit-mobile': { width: 390, height: 844 },
    'webkit-tablet': { width: 834, height: 1194 },
  };
  const isTouchProject = Boolean(touchProjects[testInfo.project.name]);
  const isWebKitTouch = testInfo.project.name === 'webkit-mobile' || testInfo.project.name === 'webkit-tablet';

  if (testInfo.project.name === 'chromium-mobile') {
    expect(await page.evaluate(() => navigator.maxTouchPoints || 0)).toBeGreaterThan(0);
    expect(page.viewportSize()).toEqual(touchProjects[testInfo.project.name]);
  }

  if (isWebKitTouch) {
    expect(page.viewportSize()).toEqual(touchProjects[testInfo.project.name]);
    await tapCenter(page, toggle);
    await expect(toggle).toHaveAttribute('aria-expanded', 'true');
    await expect(panel).toBeVisible();
    await tapCenter(page, toggle);
    await expect(toggle).toHaveAttribute('aria-expanded', 'false');
    await expect(panel).toBeHidden();

    expect(await openCommandPaletteThroughModule(page)).toBe(true);
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

    await page.evaluate(() => globalThis.AtelierV14Shell.notifications.toast('V14 browser smoke'));
    await expect(page.locator('#toast')).toHaveText('V14 browser smoke');
    await assertCoreHelpers(page);
    await assertModuleVersions(page);
    expect(pageErrors, `page errors: ${pageErrors.join('\n')}`).toEqual([]);
    expect(consoleErrors, `console errors: ${consoleErrors.join('\n')}`).toEqual([]);
    return;
  }

  if (isTouchProject) {
    await toggle.click();
    await expect(toggle).toHaveAttribute('aria-expanded', 'true');
    await expect(panel).toBeVisible();
    await toggle.click();
    await expect(panel).toBeHidden();
    await expect(toggle).toHaveAttribute('aria-expanded', 'false');
    await openCommandPaletteThroughModule(page);
  } else {
    await toggle.focus();
    await expect(toggle).toBeFocused();
    await page.keyboard.press('Enter');
    await expect(toggle).toHaveAttribute('aria-expanded', 'true');
    await expect(panel).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(panel).toBeHidden();
    await expect(toggle).toHaveAttribute('aria-expanded', 'false');
    await expect(toggle).toBeFocused();
    await page.keyboard.press('Control+K');
  }

  await expect(dialog).toHaveAttribute('open', '');
  await expect(dialog).toHaveAttribute('aria-modal', 'true');
  await expect(page.locator('#dialog-title')).toHaveText('Find a tool or an object.');
  const search = page.locator('#command-search');
  await expect(search).toHaveAttribute('aria-label', 'Search commands and objects');
  await expect(search).toBeVisible();
  if (!isTouchProject) await expect(search).toBeFocused();

  if (isTouchProject) {
    await dialog.locator('[data-action="close-dialog"]').click();
    await expect(dialog).not.toHaveAttribute('open', '');
    await openCommandPaletteThroughModule(page);
  } else {
    await page.keyboard.press('Escape');
    await expect(dialog).not.toHaveAttribute('open', '');
    await expect(toggle).toBeFocused();
    await page.keyboard.press('Control+K');
    await expect(search).toBeFocused();
  }

  await search.fill('Export deliverables');
  const exportCommand = page.locator('#command-results [data-command="export"]');
  await expect(exportCommand).toHaveCount(1);
  await expect(exportCommand).toContainText('Export deliverables');
  await expect(exportCommand.locator('svg')).toHaveCount(1);
  await dialog.locator('[data-action="close-dialog"]').click();
  await expect(dialog).not.toHaveAttribute('open', '');
  if (!isTouchProject) await expect(toggle).toBeFocused();

  await page.evaluate(() => globalThis.AtelierV14Shell.notifications.toast('V14 browser smoke'));
  await expect(page.locator('#toast')).toHaveText('V14 browser smoke');
  await expect(page.locator('#toast')).toHaveClass(/show/);

  await assertCoreHelpers(page);
  await assertModuleVersions(page);

  expect(pageErrors, `page errors: ${pageErrors.join('\n')}`).toEqual([]);
  expect(consoleErrors, `console errors: ${consoleErrors.join('\n')}`).toEqual([]);
});
