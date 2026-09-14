const VERSION = '14.0.0-dev.6';
const DEFAULT_KICKER = 'ATELIER SPACE STUDIO';
const PREFERRED_FOCUS = '[autofocus],#command-search,input:not([type=hidden]):not([disabled]),select:not([disabled]),textarea:not([disabled]),.dialog-content button:not([disabled])';

function open(title, html, { wide = false, kicker = DEFAULT_KICKER } = {}, adapter = {}) {
  if (typeof adapter.closeContextMenu !== 'function' || typeof adapter.setModalReturn !== 'function') return false;
  const dialog = document.querySelector('#dialog');
  const titleElement = document.querySelector('#dialog-title');
  const kickerElement = document.querySelector('#dialog-kicker');
  const contentElement = document.querySelector('#dialog-content');
  if (!dialog || !titleElement || !kickerElement || !contentElement || typeof dialog.showModal !== 'function') return false;

  adapter.closeContextMenu();
  adapter.setModalReturn(document.activeElement);
  titleElement.textContent = title;
  kickerElement.textContent = kicker;
  contentElement.innerHTML = html;
  dialog.classList.toggle('wide', wide);
  dialog.setAttribute('aria-modal', 'true');
  if (!dialog.open) dialog.showModal();
  requestAnimationFrame(() => {
    const preferred = dialog.querySelector(PREFERRED_FOCUS);
    preferred?.focus?.({ preventScroll: true });
  });
  return true;
}

function close(adapter = {}) {
  if (typeof adapter.getModalReturn !== 'function' || typeof adapter.setModalReturn !== 'function' || typeof adapter.clearConfirmCallback !== 'function') return false;
  const dialog = document.querySelector('#dialog');
  if (!dialog || typeof dialog.close !== 'function') return false;

  if (dialog.open) dialog.close();
  adapter.clearConfirmCallback();
  const target = adapter.getModalReturn();
  adapter.setModalReturn(null);
  requestAnimationFrame(() => target?.focus?.({ preventScroll: true }));
  return true;
}

function confirm(title, message, callback, label = 'Continue', adapter = {}) {
  if (typeof adapter.setConfirmCallback !== 'function' || typeof adapter.openDialog !== 'function' || typeof adapter.esc !== 'function') return false;
  adapter.setConfirmCallback(callback);
  adapter.openDialog(
    title,
    `<p class="dialog-intro">${adapter.esc(message)}</p><div class="dialog-actions"><button class="btn" data-action="close-dialog">Cancel</button><button class="btn primary" data-action="confirm">${adapter.esc(label)}</button></div>`
  );
  return true;
}

const existing = globalThis.AtelierV14Shell;
const shell = existing && typeof existing === 'object' ? existing : {};
globalThis.AtelierV14Shell = shell;
shell.dialogs = Object.freeze({ version: VERSION, open, close, confirm });

window.dispatchEvent(new CustomEvent('atelier:v14:dialogs-ready', {
  detail: { version: VERSION },
}));
