/* exp-naturalist.js — the naturalist chef's sibling (turn 2).
 *
 * Two things the HTML controller leans on:
 *   1) Naturalist.parseRepo()  — the SYSTEM I named by free-roaming the repo:
 *      ontum's own root CLAUDE.md is a "composition surface" that @-imports nine
 *      module environments, and each module's CLAUDE.md carries a one-line THESIS
 *      (the text after its "— ") plus [file](file) links. We FETCH and PARSE those
 *      real files at runtime, so the mesh is GENERATED from the directory — the
 *      edges are real (@-imports, defines), never hand-authored. This is the
 *      slider's high end: a big nucleus (the repo's thesis) growing into a living
 *      module mesh by the same grammar that grows "The cat naps."
 *   2) creature()             — the figurative ink-icon library (the naturalist
 *      signature). Every glyph gets a creature, derived from its kind/word/ext.
 *
 * Pure, defensive, no deps. Drawing reuses the page's 2d context; the engine still
 * draws nodes/water/edges/pulses — we only bloom a little hand-ink creature above.
 */
(function () {
  const TAU = Math.PI * 2;

  // ───────────────────────── the repo parser (live) ─────────────────────────
  // base = the served repo root (this file lives in causality/, so '..').
  const BASE = '../';
  async function getText(path) {
    try { const r = await fetch(BASE + path); if (!r.ok) return null; return await r.text(); }
    catch (e) { return null; }
  }
  const firstPara = (md, afterIdx) => {
    const s = md.slice(afterIdx);
    const m = s.match(/\n\s*\n([^\n][\s\S]*?)(\n\s*\n|$)/);
    return m ? m[1].replace(/\s+/g, ' ').trim() : '';
  };
  // a module's thesis = the phrase after "— " in its top "# dir/ — thesis" heading.
  function parseHeading(md) {
    const h = (md.match(/^#\s+(.+)$/m) || [])[1] || '';
    const parts = h.split(/\s+[—–-]\s+/);
    return { label: (parts[0] || '').replace(/\/$/, '').trim(), thesis: (parts[1] || '').trim() };
  }
  // the concrete units a module names: [file](target) links ending in a code ext,
  // else backtick-wrapped dir/file names (real tokens from the file, never invented).
  function parseUnits(md, cap) {
    const out = [], seen = new Set();
    const reLink = /\[([^\]]+)\]\(([^)]+)\)/g; let m;
    while ((m = reLink.exec(md)) && out.length < cap) {
      const t = m[2].split('/').pop();
      if (/\.(py|js|json|html|md)$/i.test(t) && !seen.has(t)) { seen.add(t); out.push(t); }
    }
    if (!out.length) {
      const reTick = /`([\w.\-]+\/?)`/g;
      while ((m = reTick.exec(md)) && out.length < cap) {
        const t = m[1];
        if (/[\/.]/.test(t) && !seen.has(t)) { seen.add(t); out.push(t); }
      }
    }
    return out;
  }

  async function parseRepo() {
    const root = await getText('CLAUDE.md');
    if (!root) return { ok: false };
    // the @-imports — the composition surface, in declared order.
    const dirs = [];
    const reImp = /^@([^\s]+)\/CLAUDE\.md/gm; let m;
    while ((m = reImp.exec(root))) dirs.push(m[1]);
    // the repo nucleus's own thesis.
    const wIdx = root.indexOf('## What this repo is');
    const rootThesis = wIdx >= 0 ? firstPara(root, wIdx) : (parseHeading(root).thesis || 'an AI-native loop substrate');
    // modules deliberately NOT on the surface (root names them: tests/, pivot/).
    const unimported = [];
    const reTick = /`([a-z][\w\-]*)\/`/g;
    while ((m = reTick.exec(root))) { const d = m[1]; if (!dirs.includes(d) && !unimported.includes(d)) unimported.push(d); }
    // fetch every imported module's CLAUDE.md and fold its thesis + units.
    const mods = await Promise.all(dirs.map(async (dir) => {
      const md = await getText(dir + '/CLAUDE.md');
      if (!md) return { dir, label: dir, thesis: '', desc: '', units: [], ok: false };
      const h = parseHeading(md);
      const hIdx = md.search(/^#\s+/m);
      return {
        dir, label: h.label || dir, thesis: h.thesis || '',
        desc: firstPara(md, hIdx >= 0 ? hIdx : 0),
        units: parseUnits(md, 4), ok: true,
      };
    }));
    return { ok: true, rootLabel: 'ontum', rootThesis, modules: mods, unimported: unimported.slice(0, 3) };
  }

  // ───────────────────── the figurative ink-icon library ─────────────────────
  // every creature is a few hand strokes; small + defensive. col = the glyph hue.
  function stroke(cx, pts, col, w, close) {
    cx.strokeStyle = col; cx.lineWidth = w; cx.lineCap = 'round'; cx.lineJoin = 'round';
    cx.beginPath(); pts.forEach((p, i) => i ? cx.lineTo(p[0], p[1]) : cx.moveTo(p[0], p[1])); if (close) cx.closePath(); cx.stroke();
  }
  function ring(cx, x, y, r, col, w) { cx.strokeStyle = col; cx.lineWidth = w || 1.6; cx.beginPath(); cx.arc(x, y, r, 0, TAU); cx.stroke(); }
  function rays(cx, x, y, r0, r1, n, col, w) { for (let i = 0; i < n; i++) { const a = i / n * TAU; stroke(cx, [[x + Math.cos(a) * r0, y + Math.sin(a) * r0], [x + Math.cos(a) * r1, y + Math.sin(a) * r1]], col, w || 1.2); } }

  function creature(cx, key, x, y, s, col) {
    cx.save(); cx.strokeStyle = col; cx.fillStyle = col; cx.lineCap = 'round'; cx.lineJoin = 'round';
    switch (key) {
      case 'cat':
        stroke(cx, [[x - s * .6, y - s * .2], [x - s * .85, y - s * .95], [x - s * .18, y - s * .45]], col, 1.6);
        stroke(cx, [[x + s * .6, y - s * .2], [x + s * .85, y - s * .95], [x + s * .18, y - s * .45]], col, 1.6);
        ring(cx, x, y, s * .62, col, 1.6);
        stroke(cx, [[x - s * .15, y + s * .05], [x - s * .95, y - s * .12]], col, 1); stroke(cx, [[x - s * .15, y + s * .12], [x - s * .95, y + s * .18]], col, 1);
        stroke(cx, [[x + s * .15, y + s * .05], [x + s * .95, y - s * .12]], col, 1); stroke(cx, [[x + s * .15, y + s * .12], [x + s * .95, y + s * .18]], col, 1);
        break;
      case 'sun': ring(cx, x, y, s * .5, col, 1.6); rays(cx, x, y, s * .66, s, 8, col, 1.3); break;
      case 'cloud': cx.beginPath(); cx.arc(x - s * .45, y + s * .1, s * .4, 0, TAU); cx.arc(x + s * .05, y - s * .18, s * .5, 0, TAU); cx.arc(x + s * .55, y + s * .1, s * .42, 0, TAU); cx.stroke(); break;
      case 'spark': rays(cx, x, y, s * .45, s * .85, 6, col, 1.1); cx.beginPath(); cx.arc(x, y, s * .3, 0, TAU); cx.fillStyle = col + '55'; cx.fill(); break;
      case 'eye': // glyphs — a seeing rune
        stroke(cx, [[x - s, y], [x - s * .4, y - s * .55], [x + s * .4, y - s * .55], [x + s, y], [x + s * .4, y + s * .55], [x - s * .4, y + s * .55]], col, 1.5, true);
        cx.beginPath(); cx.arc(x, y, s * .28, 0, TAU); cx.fillStyle = col; cx.fill(); break;
      case 'leaf': // language — a speaking leaf
        cx.beginPath(); cx.moveTo(x, y - s); cx.quadraticCurveTo(x + s * .8, y, x, y + s); cx.quadraticCurveTo(x - s * .8, y, x, y - s); cx.stroke();
        stroke(cx, [[x, y - s * .7], [x, y + s * .7]], col, 1); break;
      case 'sprout': // .ai-native — the records, a seedling
        stroke(cx, [[x, y + s], [x, y - s * .2]], col, 1.5);
        cx.beginPath(); cx.moveTo(x, y - s * .1); cx.quadraticCurveTo(x - s * .8, y - s * .3, x - s * .9, y - s); cx.quadraticCurveTo(x - s * .2, y - s * .6, x, y - s * .1); cx.stroke();
        cx.beginPath(); cx.moveTo(x, y - s * .25); cx.quadraticCurveTo(x + s * .8, y - s * .5, x + s * .9, y - s * 1.05); cx.quadraticCurveTo(x + s * .2, y - s * .7, x, y - s * .25); cx.stroke(); break;
      case 'boat': // exports — the envoy, a paper boat
        stroke(cx, [[x - s, y + s * .3], [x + s, y + s * .3], [x + s * .6, y + s * .8], [x - s * .6, y + s * .8]], col, 1.5, true);
        stroke(cx, [[x, y + s * .3], [x, y - s], [x + s * .7, y + s * .1], [x, y + s * .1]], col, 1.4); break;
      case 'compass': // causality — the witness
        ring(cx, x, y, s * .8, col, 1.5);
        stroke(cx, [[x, y], [x + s * .4, y - s * .55], [x + s * .12, y - s * .12]], col, 1.4, true);
        stroke(cx, [[x, y], [x - s * .4, y + s * .55], [x - s * .12, y + s * .12]], col, 1.4, true); break;
      case 'star': // outcomes — the north star
        { const pts = []; for (let i = 0; i < 10; i++) { const a = -TAU / 4 + i / 10 * TAU, r = i % 2 ? s * .4 : s; pts.push([x + Math.cos(a) * r, y + Math.sin(a) * r]); } stroke(cx, pts, col, 1.4, true); } break;
      case 'key': // .claude — the harness key
        ring(cx, x, y - s * .35, s * .42, col, 1.5);
        stroke(cx, [[x, y + s * .05], [x, y + s]], col, 1.5); stroke(cx, [[x, y + s * .6], [x + s * .4, y + s * .6]], col, 1.4); stroke(cx, [[x, y + s * .85], [x + s * .3, y + s * .85]], col, 1.4); break;
      case 'gate': // fence — the firm denial
        stroke(cx, [[x - s, y - s * .2], [x + s, y - s * .2]], col, 1.5); stroke(cx, [[x - s, y + s * .5], [x + s, y + s * .5]], col, 1.5);
        for (let i = -1; i <= 1; i++) stroke(cx, [[x + i * s * .7, y - s * .7], [x + i * s * .7, y + s]], col, 1.4); break;
      case 'knot': // loop — the substrate, a loop knot
        cx.beginPath(); cx.arc(x - s * .35, y, s * .55, -0.4, TAU - 0.4); cx.stroke();
        cx.beginPath(); cx.arc(x + s * .35, y, s * .55, Math.PI - 0.4, Math.PI + TAU - 0.4); cx.stroke(); break;
      case 'cog': // a .py unit
        ring(cx, x, y, s * .5, col, 1.4); rays(cx, x, y, s * .5, s * .85, 7, col, 1.2);
        cx.beginPath(); cx.arc(x, y, s * .2, 0, TAU); cx.fillStyle = col; cx.fill(); break;
      case 'grid': // a .json unit
        ring(cx, x, y, 0, col, 0);
        stroke(cx, [[x - s * .7, y - s * .7], [x + s * .7, y - s * .7], [x + s * .7, y + s * .7], [x - s * .7, y + s * .7]], col, 1.3, true);
        stroke(cx, [[x, y - s * .7], [x, y + s * .7]], col, 1); stroke(cx, [[x - s * .7, y], [x + s * .7, y]], col, 1); break;
      case 'frame': // a .html unit
        stroke(cx, [[x - s * .8, y - s * .6], [x + s * .8, y - s * .6], [x + s * .8, y + s * .6], [x - s * .8, y + s * .6]], col, 1.3, true);
        stroke(cx, [[x - s * .8, y - s * .25], [x + s * .8, y - s * .25]], col, 1); break;
      case 'owl': // owl-stars — the watcher
        ring(cx, x, y, s * .7, col, 1.5);
        stroke(cx, [[x - s * .55, y - s * .55], [x - s * .25, y - s * .9], [x - s * .1, y - s * .5]], col, 1.4);
        stroke(cx, [[x + s * .55, y - s * .55], [x + s * .25, y - s * .9], [x + s * .1, y - s * .5]], col, 1.4);
        cx.beginPath(); cx.arc(x - s * .28, y - s * .05, s * .18, 0, TAU); cx.arc(x + s * .28, y - s * .05, s * .18, 0, TAU); cx.stroke();
        stroke(cx, [[x - s * .12, y + s * .15], [x, y + s * .32], [x + s * .12, y + s * .15]], col, 1.2, true); break;
      case 'mouse': // mouse-crumbs — the path-maker
        cx.beginPath(); cx.arc(x, y + s * .15, s * .55, 0, TAU); cx.stroke();
        cx.beginPath(); cx.arc(x - s * .5, y - s * .45, s * .32, 0, TAU); cx.arc(x + s * .5, y - s * .45, s * .32, 0, TAU); cx.stroke();
        cx.beginPath(); cx.moveTo(x + s * .5, y + s * .35); cx.quadraticCurveTo(x + s * 1.1, y + s * .5, x + s * .9, y - s * .2); cx.stroke(); break;
      case 'robot': // robot-plant — the little tender
        stroke(cx, [[x - s * .55, y - s * .55], [x + s * .55, y - s * .55], [x + s * .55, y + s * .5], [x - s * .55, y + s * .5]], col, 1.5, true);
        cx.beginPath(); cx.arc(x - s * .22, y - s * .12, s * .12, 0, TAU); cx.arc(x + s * .22, y - s * .12, s * .12, 0, TAU); cx.fillStyle = col; cx.fill();
        stroke(cx, [[x, y - s * .55], [x, y - s]], col, 1.2); cx.beginPath(); cx.arc(x, y - s, s * .12, 0, TAU); cx.fillStyle = col; cx.fill(); break;
      case 'drop': // water — a falling drop
        cx.beginPath(); cx.moveTo(x, y - s); cx.quadraticCurveTo(x + s * .7, y + s * .3, x, y + s * .7); cx.quadraticCurveTo(x - s * .7, y + s * .3, x, y - s); cx.stroke(); break;
      case 'bug': // caterpillar / bee / moth — a little segmented friend
        for (let i = -1; i <= 1; i++) { cx.beginPath(); cx.arc(x + i * s * .42, y, s * .3, 0, TAU); cx.stroke(); }
        stroke(cx, [[x - s * .9, y - s * .55], [x - s * .65, y - s * .15]], col, 1.1); stroke(cx, [[x - s * .55, y - s * .6], [x - s * .4, y - s * .18]], col, 1.1); break;
      case 'fox': // fox-berry — the cacher
        ring(cx, x, y, s * .55, col, 1.5);
        stroke(cx, [[x - s * .5, y - s * .35], [x - s * .8, y - s], [x - s * .15, y - s * .6]], col, 1.4);
        stroke(cx, [[x + s * .5, y - s * .35], [x + s * .8, y - s], [x + s * .15, y - s * .6]], col, 1.4);
        stroke(cx, [[x, y + s * .2], [x, y + s * .55]], col, 1.2); break;
      case 'flower': // bee-flower — the source
        for (let i = 0; i < 6; i++) { const a = i / 6 * TAU; cx.beginPath(); cx.ellipse(x + Math.cos(a) * s * .5, y + Math.sin(a) * s * .5, s * .3, s * .18, a, 0, TAU); cx.stroke(); }
        cx.beginPath(); cx.arc(x, y, s * .22, 0, TAU); cx.fillStyle = col; cx.fill(); break;
      default: // a small hand rune — the honest fallback
        cx.beginPath(); cx.moveTo(x - s * .5, y + s * .5); cx.quadraticCurveTo(x, y - s, x + s * .5, y + s * .5); cx.stroke();
        cx.beginPath(); cx.arc(x, y + s * .2, s * .18, 0, TAU); cx.fillStyle = col; cx.fill();
    }
    cx.restore();
  }

  // ─────────────── corpus: a creature for any glyph word (the joy) ───────────────
  // prefer the glyph's own declared icon; else map a known character; else a rune.
  const WORD_CREATURE = {
    cat: 'cat', owl: 'owl', mouse: 'mouse', robot: 'robot', fox: 'fox',
    bee: 'bug', moth: 'bug', caterpillar: 'bug', sun: 'sun', sunbeam: 'sun',
    flower: 'flower', leaf: 'leaf', leaves: 'leaf', water: 'drop', crumb: 'sprout',
    shadow: 'cloud', light: 'spark', warmth: 'spark', star: 'star', stars: 'star',
  };
  const wordCreature = (word, icon) => (icon && icon !== 'null') ? icon : (WORD_CREATURE[(word || '').toLowerCase()] || 'rune');
  // the membrane creature for a whole phrase = its first glyph that maps to a character.
  function phraseCreature(phrase) {
    for (const g of (phrase.glyphs || [])) { const k = wordCreature(g.word, g.icon); if (k !== 'rune') return { key: k, word: g.word }; }
    const g0 = (phrase.glyphs || [])[0]; return { key: 'rune', word: g0 ? g0.word : phrase.id };
  }

  // ───────── the recovery the SCORER measures (done-line 0105) ─────────
  // From a phrase (the TRUTH mesh = the label), derive TWO recovered meshes a
  // reader could produce, so recovery_scorer.js can SCORE them against the truth:
  //   • mechanism — the careful reading: the true relations, mediator intact.
  //   • careless  — the tempting misreading: the phrase's surface_trap edge drawn,
  //                 deterministically, by collapsing / reversing / adding per the
  //                 trap's real structure (never invented — derived from the mesh).
  // The scorer (real, imported) then turns these into a measured composite +
  // reads_mechanism flag — the benchmark teeth, moved by the gesture, not drawn.
  const glyphOf = (ref) => (ref || '').split('.')[0];
  function recoverReadings(phrase) {
    const glyphs = (phrase.glyphs || []).map(g => ({ word: g.word, facets: (g.facets || []).slice() }));
    const truth = (phrase.relations || []).map(r => ({ from: r.from, to: r.to, label: r.label }));
    const mechanism = { glyphs, relations: truth.slice() };
    const trap = phrase.surface_trap;
    if (!trap || !trap.edge) return { mechanism, careless: mechanism, hasTrap: false };
    const tf = trap.edge.from, tt = trap.edge.to, gf = glyphOf(tf), gt = glyphOf(tt);
    let rels;
    // 1) elided-mediator: a true 2-hop path gf→M→gt the trap collapses → drop it.
    let path = null;
    for (const g of glyphs) { const M = g.word; if (M === gf || M === gt) continue;
      const e1 = truth.find(r => glyphOf(r.from) === gf && glyphOf(r.to) === M);
      const e2 = truth.find(r => glyphOf(r.from) === M && glyphOf(r.to) === gt);
      if (e1 && e2) { path = [e1, e2]; break; } }
    if (path) rels = truth.filter(r => r !== path[0] && r !== path[1]);
    else { // 2) reversed: a true gt→gf the reader flips → drop the true one.
      const rev = truth.find(r => glyphOf(r.from) === gt && glyphOf(r.to) === gf);
      rels = rev ? truth.filter(r => r !== rev) : truth.slice(); // 3) else: just add the wrong edge.
    }
    rels = rels.concat([{ from: tf, to: tt, label: trap.edge.label }]);
    return { mechanism, careless: { glyphs, relations: rels }, hasTrap: true };
  }

  // corpus links from phrases.json (declared seed structure, stitched by shared glyph).
  function corpusLinks(data) {
    return (data.links || []).map(l => ({ a: l.a, b: l.b, via: l.via, aGlyph: l.aGlyph, bGlyph: l.bGlyph }));
  }

  // derive a creature for every glyph (room want: "a creature for every glyph").
  const MOD_ICON = { loop: 'knot', glyphs: 'eye', language: 'leaf', '.ai-native': 'sprout', exports: 'boat', causality: 'compass', outcomes: 'star', '.claude': 'key', fence: 'gate' };
  const fileIcon = name => { const e = (name.split('.').pop() || '').toLowerCase();
    return e === 'py' ? 'cog' : e === 'json' ? 'grid' : e === 'html' ? 'frame' : e === 'md' ? 'leaf' : e === 'js' ? 'spark' : 'rune'; };

  window.Naturalist = { parseRepo, creature, MOD_ICON, fileIcon, wordCreature, phraseCreature, recoverReadings, corpusLinks };
})();
