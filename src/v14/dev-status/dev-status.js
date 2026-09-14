const ROOT_ID = 'atelier-v14-devtools';
const TOGGLE_ID = 'atelier-v14-devtools-toggle';
const PANEL_ID = 'atelier-v14-devtools-panel';

if (!document.getElementById(ROOT_ID)) {
  const root = document.createElement('div');
  root.id = ROOT_ID;

  const toggle = document.createElement('button');
  toggle.id = TOGGLE_ID;
  toggle.type = 'button';
  toggle.textContent = 'V14 DEV';
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-controls', PANEL_ID);
  toggle.title = 'Atelier V14 development diagnostics (Ctrl/Cmd+Shift+D)';

  const panel = document.createElement('section');
  panel.id = PANEL_ID;
  panel.hidden = true;
  panel.setAttribute('aria-labelledby', `${PANEL_ID}-title`);

  const title = document.createElement('h2');
  title.id = `${PANEL_ID}-title`;
  title.textContent = 'V14 development diagnostics';

  const note = document.createElement('p');
  note.className = 'v14-note';
  note.textContent = 'V14 development overlay on the locked Atelier 13.2.0 baseline.';

  const list = document.createElement('dl');
  const fields = new Map();
  for (const [key, label] of [
    ['network', 'Network'],
    ['display', 'Display mode'],
    ['serviceWorker', 'Service worker'],
    ['touch', 'Touch points'],
    ['viewport', 'Viewport'],
    ['baseline', 'Baseline'],
  ]) {
    const term = document.createElement('dt');
    term.textContent = label;
    const value = document.createElement('dd');
    value.dataset.v14Field = key;
    fields.set(key, value);
    list.append(term, value);
  }

  const warning = document.createElement('p');
  warning.className = 'v14-warning';
  warning.textContent = 'Development build — not V13.3.1 production certification.';

  panel.append(title, note, list, warning);
  root.append(toggle, panel);
  document.body.append(root);

  const displayMode = () => {
    if (window.matchMedia?.('(display-mode: standalone)').matches) return 'standalone';
    if (window.navigator.standalone) return 'standalone-ios';
    return 'browser';
  };

  const refresh = () => {
    fields.get('network').textContent = navigator.onLine ? 'online' : 'offline';
    fields.get('display').textContent = displayMode();
    fields.get('serviceWorker').textContent = navigator.serviceWorker?.controller ? 'controlled' : 'not controlled';
    fields.get('touch').textContent = String(navigator.maxTouchPoints || 0);
    fields.get('viewport').textContent = `${window.innerWidth} × ${window.innerHeight} @ ${window.devicePixelRatio || 1}x`;
    fields.get('baseline').textContent = 'Atelier 13.2.0';
  };

  const setOpen = (open) => {
    panel.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
    if (open) refresh();
  };

  toggle.addEventListener('click', () => setOpen(panel.hidden));
  window.addEventListener('online', refresh);
  window.addEventListener('offline', refresh);
  window.addEventListener('resize', refresh, { passive: true });
  navigator.serviceWorker?.addEventListener?.('controllerchange', refresh);
  document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key.toLowerCase() === 'd') {
      event.preventDefault();
      setOpen(!panel.hidden);
      if (!panel.hidden) toggle.focus();
    }
    if (event.key === 'Escape' && !panel.hidden) {
      setOpen(false);
      toggle.focus();
    }
  });

  refresh();
}
