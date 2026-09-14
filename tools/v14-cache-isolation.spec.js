const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.V14_SMOKE_URL || 'http://127.0.0.1:4173/';
const BASELINE_CACHE = 'atelier-space-studio-13.2.0';
const POISON_MARKER = 'BASELINE_CACHE_POISON_USED';

async function waitForShell(page) {
  await page.waitForFunction(() => Boolean(globalThis.AtelierV14Shell?.units), null, { timeout: 15_000 });
}

async function waitForController(page) {
  await page.evaluate(async () => navigator.serviceWorker.ready);
  if (!(await page.evaluate(() => Boolean(navigator.serviceWorker.controller)))) {
    await page.reload({ waitUntil: 'networkidle' });
    await waitForShell(page);
  }
  await page.waitForFunction(() => Boolean(navigator.serviceWorker?.controller));
}

test('V14 worker never reads a matching response from the production cache namespace', async ({ page, context }) => {
  const pageErrors = [];
  const consoleErrors = [];
  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });

  const base = new URL(BASE_URL);
  await page.goto(new URL('icon-192.png?cache-isolation-seed=1', base).href, { waitUntil: 'load' });
  await page.evaluate(async ({ baselineCache, unitsUrl, marker }) => {
    const cache = await caches.open(baselineCache);
    await cache.put(unitsUrl, new Response(`throw new Error(${JSON.stringify(marker)});`, {
      headers: { 'Content-Type': 'text/javascript' },
    }));
  }, {
    baselineCache: BASELINE_CACHE,
    unitsUrl: new URL('v14/shell/units.js', base).href,
    marker: POISON_MARKER,
  });

  await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  await waitForShell(page);
  expect(await page.evaluate(() => globalThis.AtelierV14Shell.units.formatDimension(1, 'ft-in'))).toBe('3′ 3.375″');
  await waitForController(page);

  const workerSource = await page.evaluate(async () => fetch('./sw.js', { cache: 'no-store' }).then(response => response.text()));
  expect(workerSource).not.toContain('caches.match(');
  expect(workerSource).toContain('cache.match(event.request)');

  await context.setOffline(true);
  try {
    await page.reload({ waitUntil: 'domcontentloaded', timeout: 30_000 });
    await waitForShell(page);
    expect(await page.evaluate(() => globalThis.AtelierV14Shell.units.formatDimension(1, 'ft-in'))).toBe('3′ 3.375″');
  } finally {
    await context.setOffline(false);
  }

  expect(pageErrors.some(error => error.includes(POISON_MARKER))).toBe(false);
  expect(consoleErrors.some(error => error.includes(POISON_MARKER))).toBe(false);
});
