import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const results = { innerHTML: '' };
const search = { focused: false, focus() { this.focused = true; } };
const events = [];
let timer = null;
let opened = null;

globalThis.document = {
  querySelector(selector) {
    if (selector === '#command-results') return results;
    if (selector === '#command-search') return search;
    return null;
  },
};
globalThis.window = globalThis;
globalThis.setTimeout = (callback, ms) => { timer = { callback, ms }; return 1; };
globalThis.CustomEvent = class CustomEvent {
  constructor(type, init = {}) { this.type = type; this.detail = init.detail; }
};
globalThis.dispatchEvent = (event) => { events.push(event); return true; };

const modulePath = resolve(process.argv[2] || 'src/v14/shell/commands.js');
await import(pathToFileURL(modulePath).href + `?test=${Date.now()}`);

const service = globalThis.AtelierV14Shell?.commands;
assert.ok(service, 'command service should register on AtelierV14Shell');
assert.equal(service.version, '14.0.0-dev.4');

const commands = [
  ['export', 'Export deliverables', 'download'],
  ['help', 'Controls and shortcuts', 'help'],
  ['save', 'Save project in this browser', 'save'],
];
const catalog = Object.fromEntries(Array.from({ length: 30 }, (_, index) => {
  const id = `sofa-${index + 1}`;
  return [id, { id, name: `Sofa ${index + 1}`, category: 'Seating', model: 'sofa', option: '', tags: 'living room' }];
}));
const adapter = {
  commands,
  catalog,
  icon: (name, size) => `[${name}:${size || 'default'}]`,
  esc: (value) => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;'),
  openDialog: (title, html) => { opened = { title, html }; },
};

let outcome = service.render('export', adapter);
assert.deepEqual(outcome, { query: 'export', commandCount: 1, objectCount: 0 });
assert.match(results.innerHTML, /data-command="export"/);
assert.doesNotMatch(results.innerHTML, /data-command="help"/);

outcome = service.render('sofa', adapter);
assert.equal(outcome.commandCount, 0);
assert.equal(outcome.objectCount, 24, 'catalog search should preserve the legacy 24-object cap');
assert.equal((results.innerHTML.match(/data-command-place=/g) || []).length, 24);
assert.match(results.innerHTML, /data-command-place="sofa-1"/);
assert.doesNotMatch(results.innerHTML, /data-command-place="sofa-25"/);

outcome = service.render('no-such-command-or-object', adapter);
assert.deepEqual(outcome, { query: 'no-such-command-or-object', commandCount: 0, objectCount: 0 });
assert.equal(results.innerHTML, '<p class="empty-state">No matching commands or objects.</p>');

results.innerHTML = '';
assert.equal(service.open(adapter), true);
assert.equal(opened.title, 'Find a tool or an object.');
assert.match(opened.html, /id="command-search"/);
assert.match(opened.html, /id="command-results"/);
assert.equal((results.innerHTML.match(/data-command=/g) || []).length, commands.length, 'opening the palette should render every command');
assert.equal((results.innerHTML.match(/data-command-place=/g) || []).length, 0, 'empty query should not render catalog objects');
assert.equal(timer.ms, 10);
assert.equal(search.focused, false);
timer.callback();
assert.equal(search.focused, true);

assert.equal(service.render('x', { ...adapter, icon: null }), false, 'missing adapter dependencies should fail back to legacy code');
assert.equal(events.length, 1);
assert.equal(events[0].type, 'atelier:v14:commands-ready');
assert.equal(events[0].detail.version, '14.0.0-dev.4');

console.log('V14_COMMANDS_BEHAVIOR_OK=true');
