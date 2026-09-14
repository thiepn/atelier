const VERSION = '14.0.0-dev.3';
const TOAST_MS = 4300;
let toastTimer = null;
let lastAnnouncement = '';

const get = (selector) => document.querySelector(selector);

function announce(message) {
  const text = String(message || '').trim();
  if (!text || text === lastAnnouncement) return false;
  lastAnnouncement = text;
  const element = get('#sr-announcer');
  if (!element) return false;
  element.textContent = '';
  requestAnimationFrame(() => {
    element.textContent = text;
  });
  return true;
}

function toast(message) {
  const element = get('#toast');
  if (!element) return false;
  element.textContent = message;
  element.classList.add('show');
  announce(message);
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => element.classList.remove('show'), TOAST_MS);
  return true;
}

function status(message, kind = '') {
  const element = get('#save-status');
  if (!element) return false;
  element.textContent = message;
  element.className = kind;
  if (kind === 'error') announce(message);
  return true;
}

const existing = globalThis.AtelierV14Shell;
const shell = existing && typeof existing === 'object' ? existing : {};
globalThis.AtelierV14Shell = shell;
shell.notifications = Object.freeze({ version: VERSION, announce, toast, status });

window.dispatchEvent(new CustomEvent('atelier:v14:notifications-ready', {
  detail: { version: VERSION },
}));
