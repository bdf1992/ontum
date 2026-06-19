/* compare.js — the comparator + synthesis (arc.aim). THIS IS THE BAKE-OFF over readings:
   the readers are the CHEFS, each mesh is a VARIANT, and the fold takes the best of all
   flavors. N independent variants of the same text are set side by side and folded into
   robust vs divergent — WITHOUT crowning any reader. The seed (phrases.json) is just one
   chef; a model is another; a human is another.
   - Robust  = a claim independent chefs AGREE on (consensus sources it — the free core).
   - Divergent = a claim a single chef makes (a distinctive FLAVOR, an open question — D-4).
   "Take the best of all flavors" = synthesize(): the robust core (no contest) PLUS the
   divergent flavors you deliberately ADOPT → the winner mesh. Adopting a flavor is an
   explicit judgment, never automatic — so the comparator crowns nothing and the synthesis
   stays the owner's choice. This is the answer to "the seed was not robustly sourced":
   truth is what survives multiple independent witnesses (the second-set-of-eyes / D-2),
   not one authored seed — and the winner is grown from the variants, not picked.
   Pure fold, no I/O. Node + browser. Reuses recovery_scorer's set primitives. */
(function (root, factory) {
  if (typeof module !== 'undefined' && module.exports) module.exports = factory(require('./recovery_scorer.js'));
  else root.CausalityCompare = factory(root.CausalityScorer);
})(typeof self !== 'undefined' ? self : this, function (S) {
  'use strict';
  const ROBUST_MIN = 2;   // a claim carried by >= this many readings is robustly sourced

  function tally(readings, extract) {
    const m = new Map();                                   // element -> [reader labels]
    for (const r of readings) for (const x of extract(r.mesh)) {
      if (!m.has(x)) m.set(x, []);
      m.get(x).push(r.label);
    }
    return m;
  }
  function split(m) {
    const robust = [], divergent = [];
    for (const [el, readers] of m) (readers.length >= ROBUST_MIN ? robust : divergent).push({ el, readers });
    const byEl = (a, b) => (a.el < b.el ? -1 : a.el > b.el ? 1 : 0);
    return { robust: robust.sort(byEl), divergent: divergent.sort(byEl) };
  }
  const inter = (a, b) => { let n = 0; for (const x of a) if (b.has(x)) n++; return n; };
  const jaccard = (a, b) => { const i = inter(a, b), u = a.size + b.size - i; return u ? i / u : 1; };

  // compareReadings(readings, {trapEdge}) — readings: [{label, kind?, mesh}]
  function compareReadings(readings, opts) {
    opts = opts || {};
    const facets = split(tally(readings, S.facetPairs));
    const edges = split(tally(readings, (m) => S.edgeSet(m)));
    let trap = null;
    if (opts.trapEdge) {
      const takenBy = readings.filter((r) => S.edgeSet(r.mesh).has(opts.trapEdge)).map((r) => r.label);
      trap = { edge: opts.trapEdge, takenBy };               // crown nothing: just who took it
    }
    const pairwise = [];                                     // symmetric agreement, NOT vs a privileged truth
    for (let i = 0; i < readings.length; i++) for (let j = i + 1; j < readings.length; j++) {
      const A = readings[i], B = readings[j];
      pairwise.push({
        a: A.label, b: B.label,
        facetAgreement: jaccard(S.facetPairs(A.mesh), S.facetPairs(B.mesh)),
        edgeAgreement: jaccard(S.edgeSet(A.mesh), S.edgeSet(B.mesh)),
      });
    }
    return {
      readers: readings.map((r) => ({ label: r.label, kind: r.kind || '', facetCount: S.facetPairs(r.mesh).size, edgeCount: S.edgeSet(r.mesh).size })),
      facets, edges, trap, pairwise,
      note: 'No reading is crowned. Robust = carried by >= ' + ROBUST_MIN + ' independent chefs (consensus sources the claim); divergent = a single chef\'s flavor (an open question for the owner, D-4).',
    };
  }

  // synthesize(comparison, {adopt}) — TAKE THE BEST OF ALL FLAVORS. The winner mesh is the
  // robust core (consensus, free) PLUS the divergent flavors named in `adopt` (an explicit
  // judgment). Default adopt = [] -> the safe consensus core alone. The winner is GROWN from
  // the variants, never one chef picked whole.
  function synthesize(comparison, opts) {
    opts = opts || {};
    const adopt = new Set(opts.adopt || []);
    const facetEls = comparison.facets.robust.map((x) => x.el)
      .concat(comparison.facets.divergent.filter((x) => adopt.has(x.el)).map((x) => x.el));
    const edgeEls = comparison.edges.robust.map((x) => x.el)
      .concat(comparison.edges.divergent.filter((x) => adopt.has(x.el)).map((x) => x.el));
    const glyphs = {};
    for (const fp of facetEls) {
      const dot = fp.indexOf('.'); const w = fp.slice(0, dot), f = fp.slice(dot + 1);
      (glyphs[w] = glyphs[w] || { word: w, facets: [] });
      if (f && glyphs[w].facets.indexOf(f) < 0) glyphs[w].facets.push(f);
    }
    const relations = edgeEls.map((e) => { const p = e.split('→'); return { from: p[0], to: p[1] }; });
    return {
      glyphs: Object.values(glyphs), relations,
      provenance: { robustElements: comparison.facets.robust.length + comparison.edges.robust.length, adoptedFlavors: adopt.size },
    };
  }

  return { compareReadings, synthesize, ROBUST_MIN };
});
