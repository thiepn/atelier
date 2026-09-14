const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.V14_SMOKE_URL || 'http://127.0.0.1:4173/';
const V14_RELEASE = '14.0.0-dev.15';
const V14_CACHE = `atelier-v14-dev-${V14_RELEASE}`;
const BASELINE_CACHE = 'atelier-space-studio-13.2.0';
const STALE_V14_CACHE = 'atelier-v14-dev-stale-probe';
const V14_CORE = [
  './v14/dev-status/dev-status.css',
  './v14/shell/notifications.js',
  './v14/shell/dialogs.js',
  './v14/shell/commands.js',
  './v14/shell/files.js',
  './v14/shell/icons.js',
  './v14/shell/text.js',
  './v14/shell/units.js',
  './v14/dev-status/dev-status.js',
];

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

async function serviceWorkerMessage(page, type) {
  return page.evaluate((messageType) => new Promise((resolve, reject) => {
    const controller = navigator.serviceWorker?.controller;
    if (!controller) {
      reject(new Error('No controlling service worker'));
      return;
    }
    const channel = new MessageChannel();
    const timer = setTimeout(() => reject(new Error(`Timed out waiting for service-worker ${messageType}`)), 5000);
    channel.port1.onmessage = (event) => {
      clearTimeout(timer);
      resolve(event.data);
    };
    controller.postMessage({ type: messageType }, [channel.port2]);
  }), type);
}

async function serviceWorkerStatus(page) {
  return serviceWorkerMessage(page, 'GET_STATUS');
}

test('generated V14 artifact uses an isolated offline shell and survives reload', async ({ page, context }) => {
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
  expect(onlineStatus.version).toBe(V14_RELEASE);
  expect(onlineStatus.cache).toBe(V14_CACHE);
  expect(onlineStatus.ready).toBe(true);
  expect(onlineStatus.missing).toEqual([]);
  for (const asset of V14_CORE) expect(onlineStatus.core).toContain(asset);

  const initialCaches = await page.evaluate(async ({ baseline, stale }) => {
    await caches.open(baseline);
    await caches.open(stale);
    return caches.keys();
  }, { baseline: BASELINE_CACHE, stale: STALE_V14_CACHE });
  expect(initialCaches).toContain(V14_CACHE);
  expect(initialCaches).toContain(BASELINE_CACHE);
  expect(initialCaches).toContain(STALE_V14_CACHE);

  const cleanup = await serviceWorkerMessage(page, 'CLEAR_STALE_CACHES');
  expect(cleanup.cache).toBe(V14_CACHE);
  expect(cleanup.deleted).toContain(STALE_V14_CACHE);
  expect(cleanup.deleted).not.toContain(BASELINE_CACHE);
  const cachesAfterCleanup = await page.evaluate(() => caches.keys());
  expect(cachesAfterCleanup).toContain(V14_CACHE);
  expect(cachesAfterCleanup).toContain(BASELINE_CACHE);
  expect(cachesAfterCleanup).not.toContain(STALE_V14_CACHE);

  const v14Resources = await page.evaluate(() => performance.getEntriesByType('resource')
    .map((entry) => entry.name)
    .filter((name) => name.includes('/v14/')));
  expect(v14Resources.length).toBeGreaterThanOrEqual(8);

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

    const shellState = await page.evaluate(() => ({
      versions: {
        icons: globalThis.AtelierV14Shell.icons.version,
        text: globalThis.AtelierV14Shell.text.version,
        units: globalThis.AtelierV14Shell.units.version,
      },
      dimensions: {
        metric: globalThis.AtelierV14Shell.units.formatDimension(2.5, 'm'),
        imperial: globalThis.AtelierV14Shell.units.formatDimension(0.3048, 'ft-in'),
      },
    }));
    expect(shellState).toEqual({
      versions: {
        icons: '14.0.0-dev.9',
        text: '14.0.0-dev.10',
        units: '14.0.0-dev.12',
      },
      dimensions: {
        metric: '2.50 m',
        imperial: '1′ 0″',
      },
    });

    const offlineStatus = await serviceWorkerStatus(page);
    expect(offlineStatus.version).toBe(V14_RELEASE);
    expect(offlineStatus.cache).toBe(V14_CACHE);
    expect(offlineStatus.ready).toBe(true);
    expect(offlineStatus.missing).toEqual([]);
    for (const asset of V14_CORE) expect(offlineStatus.core).toContain(asset);

    const offlineCaches = await page.evaluate(() => caches.keys());
    expect(offlineCaches).toContain(V14_CACHE);
    expect(offlineCaches).toContain(BASELINE_CACHE);
  } finally {
    await context.setOffline(false);
  }

  expect(pageErrors, `page errors: ${pageErrors.join('\n')}`).toEqual([]);
  expect(consoleErrors, `console errors: ${consoleErrors.join('\n')}`).toEqual([]);
});
