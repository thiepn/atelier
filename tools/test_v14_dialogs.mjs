import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const events = [];
const rafQueue = [];
const origin = { focusCalls: [], focus(options) { this.focusCalls.push(options); } };
const preferred = { focusCalls: [], focus(options) { this.focusCalls.push(options); } };
const classValues = new Set();
const dialog = {
  open: false,
  attributes: {},
  showCount: 0,
  closeCount: 0,
  classList: {
    toggle(name, enabled) { enabled ? classValues.add(name) : classValues.delete(name); },
  },
  setAttribute(name, value) { this.attributes[name] = value; },
  showModal() { this.open = true; this.showCount += 1; },
  close() { this.open = false; this.closeCount += 1; },
  querySelector() { return preferred; },
};
const title = { textContent: '' };
const kicker = { textContent: '' };
const content = { innerHTML: '' };

globalThis.document = {
  activeElement: origin,
  querySelector(selector) {
    if (selector === '#dialog') return dialog;
    if (selector === '#dialog-title') return title;
    if (selector === '#dialog-kicker') return kicker;
    if (selector === '#dialog-content') return content;
    return null;
  },
};
globalThis.window = globalThis;
globalThis.requestAnimationFrame = (callback) => { rafQueue.push(callback); return rafQueue.length; };
globalThis.CustomEvent = class CustomEvent {
  constructor(type, init = {}) { this.type = type; this.detail = init.detail; }
};
globalThis.dispatchEvent = (event) => { events.push(event); return true; };

const modulePath = resolve(process.argv[2] || 'src/v14/shell/dialogs.js');
await import(pathToFileURL(modulePath).href + `?test=${Date.now()}`);

const service = globalThis.AtelierV14Shell?.dialogs;
assert.ok(service, 'dialog service should register on AtelierV14Shell');
assert.equal(service.version, '14.0.0-dev.6');

let modalReturn = null;
let closeContextCount = 0;
const openAdapter = {
  closeContextMenu: () => { closeContextCount += 1; },
  setModalReturn: (value) => { modalReturn = value; },
};

assert.equal(service.open('Export', '<p>Body</p>', { wide: true, kicker: 'TOOLS' }, openAdapter), true);
assert.equal(closeContextCount, 1);
assert.equal(modalReturn, origin);
assert.equal(title.textContent, 'Export');
assert.equal(kicker.textContent, 'TOOLS');
assert.equal(content.innerHTML, '<p>Body</p>');
assert.equal(classValues.has('wide'), true);
assert.equal(dialog.attributes['aria-modal'], 'true');
assert.equal(dialog.open, true);
assert.equal(dialog.showCount, 1);
assert.equal(preferred.focusCalls.length, 0);
rafQueue.shift()();
assert.deepEqual(preferred.focusCalls[0], { preventScroll: true });

let clearedConfirm = 0;
const closeAdapter = {
  getModalReturn: () => modalReturn,
  setModalReturn: (value) => { modalReturn = value; },
  clearConfirmCallback: () => { clearedConfirm += 1; },
};
assert.equal(service.close(closeAdapter), true);
assert.equal(dialog.open, false);
assert.equal(dialog.closeCount, 1);
assert.equal(clearedConfirm, 1);
assert.equal(modalReturn, null);
assert.equal(origin.focusCalls.length, 0);
rafQueue.shift()();
assert.deepEqual(origin.focusCalls[0], { preventScroll: true });

let confirmCallback = null;
let opened = null;
const callback = () => 'confirmed';
const confirmAdapter = {
  setConfirmCallback: (value) => { confirmCallback = value; },
  openDialog: (dialogTitle, html) => { opened = { dialogTitle, html }; },
  esc: (value) => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;'),
};
assert.equal(service.confirm('Delete?', '<unsafe>', callback, 'Delete <now>', confirmAdapter), true);
assert.equal(confirmCallback, callback);
assert.equal(opened.dialogTitle, 'Delete?');
assert.match(opened.html, /&lt;unsafe&gt;/);
assert.match(opened.html, /Delete &lt;now&gt;/);
assert.match(opened.html, /data-action="close-dialog"/);
assert.match(opened.html, /data-action="confirm"/);

assert.equal(service.open('x', 'y', {}, {}), false, 'missing open adapters should signal legacy fallback');
assert.equal(service.close({}), false, 'missing close adapters should signal legacy fallback');
assert.equal(service.confirm('x', 'y', callback, 'Continue', {}), false, 'missing confirm adapters should signal legacy fallback');

assert.equal(events.length, 1);
assert.equal(events[0].type, 'atelier:v14:dialogs-ready');
assert.equal(events[0].detail.version, '14.0.0-dev.6');

console.log('V14_DIALOGS_BEHAVIOR_OK=true');
