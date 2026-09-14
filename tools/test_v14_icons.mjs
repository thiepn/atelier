import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const events = [];
globalThis.window = globalThis;
globalThis.CustomEvent = class CustomEvent {
  constructor(type, init = {}) { this.type = type; this.detail = init.detail; }
};
globalThis.dispatchEvent = (event) => { events.push(event); return true; };

const modulePath = resolve(process.argv[2] || 'src/v14/shell/icons.js');
await import(pathToFileURL(modulePath).href + `?test=${Date.now()}`);

const service = globalThis.AtelierV14Shell?.icons;
assert.ok(service, 'icon service should register on AtelierV14Shell');
assert.equal(service.version, '14.0.0-dev.9');

const registry = {
  cube: 'M3 3h18v18H3z',
  search: 'M11 4a7 7 0 1 0 0 14a7 7 0 0 0 0-14m5 12l5 5',
};

assert.equal(
  service.render('search', 18, registry),
  '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 4a7 7 0 1 0 0 14a7 7 0 0 0 0-14m5 12l5 5"/></svg>'
);
assert.equal(
  service.render('missing', 24, registry),
  '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 3h18v18H3z"/></svg>',
  'unknown icons should retain the legacy cube fallback'
);
assert.equal(service.render('search', 18, null), false);
assert.equal(service.render('search', 18, {}), false);
assert.equal(service.render('missing', 18, { cube: '' }), false);

assert.equal(events.length, 1);
assert.equal(events[0].type, 'atelier:v14:icons-ready');
assert.equal(events[0].detail.version, '14.0.0-dev.9');

console.log('V14_ICONS_BEHAVIOR_OK=true');
