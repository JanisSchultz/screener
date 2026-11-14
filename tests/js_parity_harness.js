/* JavaScriptCore harness (osascript -l JavaScript): runs the real dashboard script against a stub DOM and
   reports the runtime JS-vs-Python parity self-check for every company. Usage:
   osascript -l JavaScript tests/js_parity_harness.js /path/to/main.js /path/to/data.json */
ObjC.import('Foundation');
function readFile(p) { return $.NSString.stringWithContentsOfFileEncodingError(p, $.NSUTF8StringEncoding, null).js; }
function run(argv) {
  const src = readFile(argv[0]);
  const json = readFile(argv[1]);
  const handler = {
    get: (t, p) => {
      if (p === Symbol.toPrimitive) return () => '';
      if (p === 'length') return 0;
      if (p === 'style' || p === 'dataset') return {};
      if (p === 'classList') return { add() {}, remove() {}, toggle() {}, contains() { return false; } };
      return U;
    },
    apply: () => U,
    set: () => true,
  };
  const U = new Proxy(function () {}, handler);
  const elements = {};
  const el = (id) => {
    if (!elements[id]) {
      const base = { id, style: {}, dataset: {}, textContent: '', innerHTML: '', value: '', className: '', options: [], children: [],
        classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
        addEventListener() {}, setAttribute() {}, getAttribute() { return null; }, appendChild() {}, querySelectorAll() { return []; },
        querySelector() { return U; }, focus() {}, scrollIntoView() {}, closest() { return U; } };
      elements[id] = new Proxy(base, {
        get: (t, p) => (p in t ? t[p] : U),
        set: (t, p, v) => { t[p] = v; return true; },
      });
    }
    return elements[id];
  };
  const doc = {
    getElementById: (id) => id === 'screener-raw-data' ? { textContent: json } : el(id),
    querySelectorAll: () => [], querySelector: () => U, addEventListener() {}, createElement: () => el('_tmp' + Math.random()),
    body: U, documentElement: U,
  };
  const warnings = [];
  const fakeConsole = { log() {}, error(m) { warnings.push('ERROR ' + m); }, warn(m) { warnings.push(String(m)); } };
  const harness = `
    let __n = 0, __errs = [];
    for (const __c of SCREENER_DATA.companies) {
      if (!(__c.par_mult && __c.price && __c.peak_eps)) continue;
      try { selectedCompanyId = __c.id; initValuationSandbox(__c); __n++; }
      catch (e) { __errs.push(__c.id + ': ' + e); }
    }
    return { tested: __n, errors: __errs };
  `;
  const fn = new Function('document', 'window', 'console', 'localStorage', 'navigator', 'setTimeout', 'alert', 'prompt', 'location', 'history',
    src + '\n' + harness);
  const win = { addEventListener() {}, location: U, innerWidth: 1400, matchMedia: () => ({ matches: false, addEventListener() {} }) };
  const res = fn(doc, win, fakeConsole, { getItem() { return null; }, setItem() {} }, U, (f) => 0, () => {}, () => {}, U, U);
  const drift = warnings.filter((w) => w.indexOf('[parity]') === 0);
  return JSON.stringify({ tested: res.tested, runtime_errors: res.errors.slice(0, 10), n_errors: res.errors.length,
    parity_drift: drift.length, drift_examples: drift.slice(0, 10), other_console: warnings.filter((w) => w.indexOf('[parity]') !== 0).slice(0, 5) });
}
