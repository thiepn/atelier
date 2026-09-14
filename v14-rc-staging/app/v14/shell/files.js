const VERSION = '14.0.0-dev.5';
const DEFAULT_TYPE = 'application/octet-stream';
const REVOKE_DELAY_MS = 1000;

function download(data, name, type = DEFAULT_TYPE) {
  if (typeof Blob !== 'function' || typeof URL?.createObjectURL !== 'function' || typeof document?.createElement !== 'function') return false;

  const blob = data instanceof Blob ? data : new Blob([data], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = name;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), REVOKE_DELAY_MS);
  return true;
}

function safeName(name) {
  return (name.normalize('NFKD')
    .replace(/[^a-z0-9_-]/gi, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80) || 'atelier-project')
    .toLowerCase();
}

const existing = globalThis.AtelierV14Shell;
const shell = existing && typeof existing === 'object' ? existing : {};
globalThis.AtelierV14Shell = shell;
shell.files = Object.freeze({ version: VERSION, download, safeName });

window.dispatchEvent(new CustomEvent('atelier:v14:files-ready', {
  detail: { version: VERSION },
}));
