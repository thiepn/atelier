import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const events = [];
globalThis.window = globalThis;
globalThis.CustomEvent = class CustomEvent {
  constructor(type, init = {}) { this.type = type; this.detail = init.detail; }
};
globalThis.dispatchEvent = (event) => { events.push(event); return true; };

const modulePath = resolve(process.argv[2] || 'src/v14/shell/text.js');
await import(pathToFileURL(modulePath).href + `?test=${Date.now()}`);

const service = globalThis.AtelierV14Shell?.text;
assert.ok(service, 'text service should register on AtelierV14Shell');
assert.equal(service.version, '14.0.0-dev.10');

assert.equal(service.escapeHtml(null), '');
assert.equal(service.escapeHtml(undefined), '');
assert.equal(service.escapeHtml(42), '42');
assert.equal(
  service.escapeHtml(`A&B <tag> "quoted" 'single'`),
  'A&amp;B &lt;tag&gt; &quot;quoted&quot; &#39;single&#39;'
);
assert.equal(
  service.escapeHtml('&lt;already&gt;'),
  '&amp;lt;already&amp;gt;',
  'escaping must preserve the legacy single-pass behavior rather than decoding entities'
);

assert.equal(service.escapeXml(null), '');
assert.equal(service.escapeXml(42), '42');
assert.equal(
  service.escapeXml(`A&B <tag> "quoted" 'single'`),
  'A&amp;B &lt;tag&gt; &quot;quoted&quot; &apos;single&apos;'
);

assert.equal(events.length, 1);
assert.equal(events[0].type, 'atelier:v14:text-ready');
assert.equal(events[0].detail.version, '14.0.0-dev.10');

console.log('V14_TEXT_BEHAVIOR_OK=true');
