import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

class ClassList {
  constructor() { this.values = new Set(); }
  add(value) { this.values.add(value); }
  remove(value) { this.values.delete(value); }
  contains(value) { return this.values.has(value); }
}

const elements = {
  '#toast': { textContent: '', classList: new ClassList() },
  '#save-status': { textContent: '', className: '' },
  '#sr-announcer': { textContent: '' },
};
const events = [];
let timeoutCallback = null;
let clearedTimer = null;

globalThis.document = {
  querySelector(selector) { return elements[selector] || null; },
};
globalThis.window = globalThis;
globalThis.requestAnimationFrame = (callback) => { callback(); return 1; };
globalThis.setTimeout = (callback, ms) => { timeoutCallback = { callback, ms }; return 99; };
globalThis.clearTimeout = (id) => { clearedTimer = id; };
globalThis.CustomEvent = class CustomEvent {
  constructor(type, init = {}) { this.type = type; this.detail = init.detail; }
};
globalThis.dispatchEvent = (event) => { events.push(event); return true; };

const modulePath = resolve(process.argv[2] || 'src/v14/shell/notifications.js');
await import(pathToFileURL(modulePath).href + `?test=${Date.now()}`);

const service = globalThis.AtelierV14Shell?.notifications;
assert.ok(service, 'notification service should register on AtelierV14Shell');
assert.equal(service.version, '14.0.0-dev.3');

assert.equal(service.announce('Selection changed'), true);
assert.equal(elements['#sr-announcer'].textContent, 'Selection changed');
assert.equal(service.announce('Selection changed'), false, 'duplicate announcement should be suppressed');

assert.equal(service.toast('Saved'), true);
assert.equal(elements['#toast'].textContent, 'Saved');
assert.equal(elements['#toast'].classList.contains('show'), true);
assert.equal(elements['#sr-announcer'].textContent, 'Saved');
assert.equal(timeoutCallback.ms, 4300);
timeoutCallback.callback();
assert.equal(elements['#toast'].classList.contains('show'), false);

service.toast('First');
service.toast('Second');
assert.equal(clearedTimer, 99, 'subsequent toast should clear the previous timer');
assert.equal(elements['#toast'].textContent, 'Second');

assert.equal(service.status('Saving…'), true);
assert.equal(elements['#save-status'].textContent, 'Saving…');
assert.equal(elements['#save-status'].className, '');
assert.equal(service.status('Backup needed', 'error'), true);
assert.equal(elements['#save-status'].className, 'error');
assert.equal(elements['#sr-announcer'].textContent, 'Backup needed');

assert.equal(events.length, 1);
assert.equal(events[0].type, 'atelier:v14:notifications-ready');
assert.equal(events[0].detail.version, '14.0.0-dev.3');

console.log('V14_NOTIFICATIONS_BEHAVIOR_OK=true');
