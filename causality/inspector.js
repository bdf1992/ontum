/* inspector.js — the schema-driven per-element config panel, factored out so the
   full canvas (canvas.html) and the component gallery (demos.html) mount the SAME
   inspector — one source, never two that drift (done-line 0082; the Pattern
   Commons "one component, reused" discipline).

   window.CausalityInspector.mount(S, panelEl) wires S.onselect to render the panel
   for the selected node/route; editing a field writes through the schema
   (C.setPath) and fires S.onchange. Returns { render } so a caller can refresh. */
(function () {
'use strict';

function parseVal(kind, raw) {
  if (kind === 'number') return raw === '' ? null : parseFloat(raw);
  if (kind === 'bool') return !!raw;
  if (kind === 'ref') return raw === '' ? null : parseInt(raw, 10);
  if (kind === 'csv') return raw.split(',').map(s => s.trim()).filter(Boolean);
  return raw === '' ? null : raw;   // text / textarea / select
}

function mount(S, panel) {
  const C = window.Causality;

  function fieldRow(target, f, holo) {
    const cur = C.getPath(target, f.key);
    const id = 'f_' + f.key.replace(/\W/g, '_') + '_' + (target.id != null ? target.id : 'e');
    const wrap = document.createElement('div'); wrap.className = 'fld' + (holo ? ' holo' : '');
    const lab = document.createElement('label'); lab.textContent = f.label; lab.htmlFor = id; wrap.appendChild(lab);
    let inp;
    if (f.kind === 'textarea') { inp = document.createElement('textarea'); inp.value = cur == null ? '' : cur; }
    else if (f.kind === 'bool') { inp = document.createElement('input'); inp.type = 'checkbox'; inp.checked = !!cur; }
    else if (f.kind === 'select') { inp = document.createElement('select'); const opts = typeof f.opts === 'function' ? f.opts() : (f.opts || []);
      for (const o of opts) { const op = document.createElement('option'); op.value = o; op.textContent = o; if (String(cur) === String(o)) op.selected = true; inp.appendChild(op); } }
    else { inp = document.createElement('input'); inp.type = f.kind === 'number' ? 'number' : 'text';
      inp.value = cur == null ? '' : (Array.isArray(cur) ? cur.join(', ') : cur); if (f.kind === 'csv') inp.placeholder = 'comma,separated'; }
    inp.id = id;
    const commit = () => { const raw = f.kind === 'bool' ? inp.checked : inp.value; C.setPath(target, f.key, parseVal(f.kind, raw)); S.onchange && S.onchange(S); };
    inp.addEventListener(f.kind === 'bool' || f.kind === 'select' ? 'change' : 'input', commit);
    wrap.appendChild(inp); return wrap;
  }

  function render(sel) {
    panel.innerHTML = '';
    if (!sel) { panel.classList.remove('on'); return; }
    panel.classList.add('on');
    if (sel.kind === 'edge') {
      const e = sel.ref; const A = S.byId(e.a), B = S.byId(e.b);
      const h = document.createElement('h4'); h.textContent = 'route'; panel.appendChild(h);
      const k = document.createElement('div'); k.className = 'kind'; k.textContent = (A ? A.label : e.a) + ' → ' + (B ? B.label : e.b); panel.appendChild(k);
      for (const f of C.EDGE_SCHEMA) panel.appendChild(fieldRow(e, f, false));
      const acts = document.createElement('div'); acts.className = 'acts';
      const del = document.createElement('button'); del.className = 'del'; del.textContent = 'erase route';
      del.onclick = () => { S.links = S.links.filter(l => l !== e); S.select(null); S.onchange && S.onchange(S); };
      acts.appendChild(del); panel.appendChild(acts); return;
    }
    const n = sel.ref;
    const h = document.createElement('h4'); h.textContent = n.type + ' node'; panel.appendChild(h);
    const k = document.createElement('div'); k.className = 'kind'; k.textContent = '#' + n.id + ' · ' + C.GLYPH[n.type] + ' ' + n.label; panel.appendChild(k);
    const typed = (C.SCHEMA[n.type] || []);
    const common = C.fieldsFor(n.type).filter(f => !C.HOLONIC.includes(f) && !typed.includes(f));
    for (const f of common) panel.appendChild(fieldRow(n, f, false));
    if (typed.length) { const g = document.createElement('div'); g.className = 'grp'; g.textContent = n.type + ' config'; panel.appendChild(g); for (const f of typed) panel.appendChild(fieldRow(n, f, false)); }
    const g2 = document.createElement('div'); g2.className = 'grp'; g2.textContent = 'holonic · strata + anima'; panel.appendChild(g2);
    for (const f of C.HOLONIC) panel.appendChild(fieldRow(n, f, true));
    const acts = document.createElement('div'); acts.className = 'acts';
    const poke = document.createElement('button'); poke.textContent = '▷ poke'; poke.onclick = () => S.pulseNode(n);
    const del = document.createElement('button'); del.className = 'del'; del.textContent = 'erase';
    del.onclick = () => { S.links = S.links.filter(l => l.a !== n.id && l.b !== n.id); S.nodes = S.nodes.filter(m => m !== n); S.select(null); S.onchange && S.onchange(S); };
    acts.appendChild(poke); acts.appendChild(del); panel.appendChild(acts);
  }

  S.onselect = (sel) => render(sel);
  return { render };
}

if (typeof window !== 'undefined') window.CausalityInspector = { mount, parseVal };
})();
