const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.V14_SMOKE_URL || 'http://127.0.0.1:4173/';

async function waitForV14Shell(page) {
  await page.waitForFunction(() => Boolean(
    globalThis.AtelierV14Shell?.notifications &&
    globalThis.AtelierV14Shell?.dialogs &&
    globalThis.AtelierV14Shell?.commands &&
    globalThis.AtelierV14Shell?.files &&
    globalThis.AtelierV14Shell?.icons &&
    globalThis.AtelierV14Shell?.text
  ));
}

async function normalizeDialog(page) {
  const dialog = page.locator('#dialog');
  if (await dialog.evaluate((element) => element.open)) {
    const closeButton = dialog.locator('[data-action="close-dialog"]');
    if (await closeButton.count()) await closeButton.click();
    else await dialog.evaluate((element) => element.close());
    await expect(dialog).not.toHaveAttribute('open', '');
  }
}

async function waitForControlledServiceWorker(page) {
  await page.evaluate(async () => {
    if (!('serviceWorker' in navigator)) throw new Error('Service workers unavailable');
    await navigator.serviceWorker.ready;
  });
  if (!(await page.evaluate(() => Boolean(navigator.serviceWorker.controller)))) {
    await page.reload({ waitUntil: 'networkidle' });
    await waitForV14Shell(page);
  }
  await page.waitForFunction(() => Boolean(navigator.serviceWorker?.controller));
}

async function serviceWorkerStatus(page) {
  return page.evaluate(() => new Promise((resolve, reject) => {
    const controller = navigator.serviceWorker?.controller;
    if (!controller) {
      reject(new Error('No controlling service worker'));
      return;
    }
    const channel = new MessageChannel();
    const timer = setTimeout(() => reject(new Error('Timed out waiting for service-worker status')), 5000);
    channel.port1.onmessage = (event) => {
      clearTimeout(timer);
      resolve(event.data);
    };
    controller.postMessage({ type: 'GET_STATUS' }, [channel.port2]);
  }));
}

test('generated V14 artifact survives a controlled offline reload', async ({ page, context }) => {
  const pageErrors = [];
  const consoleErrors = [];
  page.on('pageerror', (error) => pageErrors.push(String(error)));
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });

  await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  await waitForV14Shell(page);
  await normalizeDialog(page);
  await waitForControlledServiceWorker(page);

  const onlineStatus = await serviceWorkerStatus(page);
  expect(onlineStatus.type).toBe('ATELIER_SW_STATUS');
  expect(onlineStatus.version).toBe('13.2.0');
  expect(onlineStatus.cache).toBe('atelier-space-studio-13.2.0');
  expect(onlineStatus.ready).toBe(true);
  expect(onlineStatus.missing).toEqual([]);

  const v14Resources = await page.evaluate(() => performance.getEntriesByType('resource')
    .map((entry) => entry.name)
    .filter((name) => name.includes('/v14/')));
  expect(v14Resources.length).toBeGreaterThanOrEqual(7);

  await context.setOffline(true);
  try {
    await page.reload({ waitUntil: 'domcontentloaded', timeout: 30_000 });
    await waitForV14Shell(page);
    await normalizeDialog(page);

    expect(await page.evaluate(() => navigator.onLine)).toBe(false);
    expect(await page.evaluate(() => Boolean(navigator.serviceWorker?.controller))).toBe(true);
    await expect(page.locator('#app')).toBeVisible();
    await expect(page.locator('#atelier-v14-devtools-toggle')).toHaveText('V14 DEV');

    const toggle = page.locator('#atelier-v14-devtools-toggle');
    await toggle.click();
    await expect(page.locator('[data-v14-field="network"]')).toHaveText('offline');
    await expect(page.locator('[data-v14-field="serviceWorker"]')).toHaveText('controlled');
    await expect(page.locator('[data-v14-field="baseline"]')).toHaveText('Atelier 13.2.0');

    const shellVersions = await page.evaluate(() => ({
      icons: globalThis.AtelierV14Shell.icons.version,
      text: globalThis.AtelierV14Shell.text.version,
    }));
    expect(shellVersions).toEqual({ icons: '14.0.0-dev.9', text: '14.0.0-dev.10' });

    const offlineStatus = await serviceWorkerStatus(page);
    expect(offlineStatus.ready).toBe(true);
    expect(offlineStatus.missing).toEqual([]);
  } finally {
    await context.setOffline(false);
  }

  expect(pageErrors, `page errors: ${pageErrors.join('\n')}`).toEqual([]);
  expect(consoleErrors, `console errors: ${consoleErrors.join('\n')}`).toEqual([]);
});
