import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const events = [];
const appended = [];
const createdUrls = [];
const revokedUrls = [];
let timer = null;

const nativeURL = globalThis.URL;
class TestURL extends nativeURL {}
TestURL.createObjectURL = (blob) => {
  createdUrls.push(blob);
  return `blob:test-${createdUrls.length}`;
};
TestURL.revokeObjectURL = (url) => revokedUrls.push(url);
globalThis.URL = TestURL;

globalThis.document = {
  body: {
    appendChild(node) { appended.push(node); },
  },
  createElement(tag) {
    assert.equal(tag, 'a');
    return {
      href: '',
      download: '',
      clicked: false,
      removed: false,
      click() { this.clicked = true; },
      remove() { this.removed = true; },
    };
  },
};
globalThis.window = globalThis;
globalThis.setTimeout = (callback, ms) => { timer = { callback, ms }; return 1; };
globalThis.CustomEvent = class CustomEvent {
  constructor(type, init = {}) { this.type = type; this.detail = init.detail; }
};
globalThis.dispatchEvent = (event) => { events.push(event); return true; };

const modulePath = resolve(process.argv[2] || 'src/v14/shell/files.js');
await import(pathToFileURL(modulePath).href + `?test=${Date.now()}`);

const service = globalThis.AtelierV14Shell?.files;
assert.ok(service, 'file service should register on AtelierV14Shell');
assert.equal(service.version, '14.0.0-dev.5');

assert.equal(service.safeName('Living Room Plan'), 'living-room-plan');
assert.equal(service.safeName('Café / Plan'), 'cafe-plan');
assert.equal(service.safeName('   '), 'atelier-project');
assert.equal(service.safeName('A'.repeat(100)), 'a'.repeat(80));
assert.equal(service.safeName('___'), '___', 'legacy underscore behavior should remain unchanged');

assert.equal(service.download('hello', 'plan.txt', 'text/plain'), true);
assert.equal(createdUrls.length, 1);
assert.ok(createdUrls[0] instanceof Blob);
assert.equal(createdUrls[0].type, 'text/plain');
assert.equal(appended.length, 1);
assert.equal(appended[0].href, 'blob:test-1');
assert.equal(appended[0].download, 'plan.txt');
assert.equal(appended[0].clicked, true);
assert.equal(appended[0].removed, true);
assert.equal(timer.ms, 1000);
assert.deepEqual(revokedUrls, []);
timer.callback();
assert.deepEqual(revokedUrls, ['blob:test-1']);

const existingBlob = new Blob(['existing'], { type: 'application/json' });
service.download(existingBlob, 'backup.json');
assert.equal(createdUrls[1], existingBlob, 'existing Blob instances should be reused');
assert.equal(appended[1].download, 'backup.json');

assert.equal(events.length, 1);
assert.equal(events[0].type, 'atelier:v14:files-ready');
assert.equal(events[0].detail.version, '14.0.0-dev.5');

console.log('V14_FILES_BEHAVIOR_OK=true');
