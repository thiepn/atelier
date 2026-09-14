const VERSION = '14.0.0-dev.4';
const OBJECT_LIMIT = 24;
const EMPTY_STATE = '<p class="empty-state">No matching commands or objects.</p>';

function normalizeAdapter(adapter = {}) {
  const { icon, esc, commands, catalog } = adapter;
  if (typeof icon !== 'function' || typeof esc !== 'function' || !Array.isArray(commands) || !catalog) return null;
  return { ...adapter, icon, esc, commands, catalog };
}

function render(query, adapter = {}) {
  const normalized = normalizeAdapter(adapter);
  const results = document.querySelector('#command-results');
  if (!normalized || !results) return false;

  const { icon, esc, commands, catalog } = normalized;
  const q = String(query ?? '').toLowerCase().trim();
  const commandMatches = commands.filter(([, label]) => String(label).toLowerCase().includes(q));
  const objectMatches = Object.values(catalog)
    .filter((asset) => q && (`${asset.name} ${asset.category} ${asset.model} ${asset.option || ''} ${asset.tags || ''}`).toLowerCase().includes(q))
    .slice(0, OBJECT_LIMIT);

  const commandHtml = commandMatches.map(([action, label, iconName]) =>
    `<button class="command-item" data-command="${action}">${icon(iconName, 18)}<span>${esc(label)}</span><small>COMMAND</small></button>`
  ).join('');
  const objectHtml = objectMatches.map((asset) =>
    `<button class="command-item" data-command-place="${asset.id}">${icon('plus', 18)}<span>${esc(asset.name)}</span><small>${esc(asset.category)}</small></button>`
  ).join('');

  results.innerHTML = commandHtml + objectHtml || EMPTY_STATE;
  return { query: q, commandCount: commandMatches.length, objectCount: objectMatches.length };
}

function open(adapter = {}) {
  const normalized = normalizeAdapter(adapter);
  if (!normalized || typeof normalized.openDialog !== 'function') return false;

  normalized.openDialog(
    'Find a tool or an object.',
    `<div class="search-field">${normalized.icon('search')}<input id="command-search" type="search" placeholder="Try “sofa”, “export”, or “repeat”…" autocomplete="off" aria-label="Search commands and objects"></div><div class="command-results" id="command-results"></div>`
  );
  if (render('', normalized) === false) return false;
  setTimeout(() => document.querySelector('#command-search')?.focus(), 10);
  return true;
}

const existing = globalThis.AtelierV14Shell;
const shell = existing && typeof existing === 'object' ? existing : {};
globalThis.AtelierV14Shell = shell;
shell.commands = Object.freeze({ version: VERSION, open, render });

window.dispatchEvent(new CustomEvent('atelier:v14:commands-ready', {
  detail: { version: VERSION },
}));
