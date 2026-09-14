const VERSION = '14.0.0-dev.10';

const HTML_ENTITIES = Object.freeze({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
});

const XML_ENTITIES = Object.freeze({
  '<': '&lt;',
  '>': '&gt;',
  '&': '&amp;',
  '"': '&quot;',
  "'": '&apos;',
});

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => HTML_ENTITIES[character]);
}

function escapeXml(value) {
  return String(value ?? '').replace(/[<>&"']/g, (character) => XML_ENTITIES[character]);
}

const existing = globalThis.AtelierV14Shell;
const shell = existing && typeof existing === 'object' ? existing : {};
globalThis.AtelierV14Shell = shell;
shell.text = Object.freeze({ version: VERSION, escapeHtml, escapeXml });

window.dispatchEvent(new CustomEvent('atelier:v14:text-ready', {
  detail: { version: VERSION },
}));
