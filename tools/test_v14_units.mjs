import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const events = [];
globalThis.window = globalThis;
globalThis.CustomEvent = class CustomEvent {
  constructor(type, init = {}) { this.type = type; this.detail = init.detail; }
};
globalThis.dispatchEvent = (event) => { events.push(event); return true; };

const modulePath = resolve(process.argv[2] || 'src/v14/shell/units.js');
await import(pathToFileURL(modulePath).href + `?test=${Date.now()}`);

const service = globalThis.AtelierV14Shell?.units;
assert.ok(service, 'units service should register on AtelierV14Shell');
assert.equal(service.version, '14.0.0-dev.12');

assert.equal(service.formatDimension(1.234, 'm'), '1.23 m');
assert.equal(service.formatDimension(1, 'ft'), '3.28 ft');
assert.equal(service.formatDimension(1, 'in'), '39.37 in');
assert.equal(service.formatDimension(1.2, 'cm'), '120.00 cm');
assert.equal(service.formatDimension(1.2345, 'mm'), '1235 mm');
assert.equal(service.formatDimension(0.3048, 'ft-in'), '1′ 0″');
assert.equal(service.formatDimension(1, 'ft-in'), '3′ 3.375″');
assert.equal(service.formatDimension(2, 'yards'), '2.00 yards');
assert.equal(service.formatDimension(1.234), '1.23 m');

assert.equal(events.length, 1);
assert.equal(events[0].type, 'atelier:v14:units-ready');
assert.equal(events[0].detail.version, '14.0.0-dev.12');

console.log('V14_UNITS_BEHAVIOR_OK=true');
