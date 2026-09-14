const VERSION = '14.0.0-dev.12';

function formatDimension(n, units = 'm') {
  if (units === 'ft-in') {
    const whole = Math.round(n / 0.0254 * 8);
    const feet = Math.floor(whole / 96);
    const inch = (whole - feet * 96) / 8;
    return `${feet}′ ${inch}″`;
  }
  const factors = { m: 1, ft: 3.280839895, mm: 1000, cm: 100, in: 39.37007874 };
  return `${(n * (factors[units] || 1)).toFixed(units === 'mm' ? 0 : 2)} ${units}`;
}

const existing = globalThis.AtelierV14Shell;
const shell = existing && typeof existing === 'object' ? existing : {};
globalThis.AtelierV14Shell = shell;
shell.units = Object.freeze({ version: VERSION, formatDimension });

window.dispatchEvent(new CustomEvent('atelier:v14:units-ready', {
  detail: { version: VERSION },
}));
