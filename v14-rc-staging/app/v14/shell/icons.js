const VERSION = '14.0.0-dev.9';

function render(name, size = 18, registry) {
  if (!registry || typeof registry !== 'object') return false;
  const path = registry[name] || registry.cube;
  if (typeof path !== 'string' || !path) return false;
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${path}"/></svg>`;
}

const existing = globalThis.AtelierV14Shell;
const shell = existing && typeof existing === 'object' ? existing : {};
globalThis.AtelierV14Shell = shell;
shell.icons = Object.freeze({ version: VERSION, render });

window.dispatchEvent(new CustomEvent('atelier:v14:icons-ready', {
  detail: { version: VERSION },
}));
