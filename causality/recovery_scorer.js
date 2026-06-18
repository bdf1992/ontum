/* recovery_scorer.js — the deterministic recovery-scorer (done-line 0105,
   outcome causality-story-benchmark). Pure, stdlib node, NO inference.

   It scores a RECOVERED mesh — what a reader (a model under test, later) read
   out of a phrase's text — against the phrase's TRUE mesh, and flags whether
   the recovery drew the phrase's `surface_trap` edge (the tempting-but-wrong
   reading). The phrase's mesh is the label; this measures distance from it.
   This is the grading spine of the round-trip: text → recovered mesh → score.

   Truth-discipline (the causality/ hard rule): this resolves and counts, it
   never mints. The §10 teeth live in recovery_scorer.test.js — the composite
   must SEPARATE a mechanism-reading from a grammar-reading of cat-sunbeam; a
   constant/fabricated scorer cannot, and the test proves it.

   A mesh (recovered or true) is { glyphs: [{word, facets:[...]}],
   relations: [{from, to, ...}] }, where from/to are 'word' or 'word.facet'
   refs — the same grammar as phrases.json. A true mesh (a phrase) may also
   carry surface_trap {type, edge:{from,to,label}, why}. */
(function (factory) {
  'use strict';
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof window !== 'undefined') window.CausalityScorer = api;
})(function () {
  'use strict';

  // The trap taxonomy — benchmark vocabulary, deliberately HERE and not in
  // canvas-system.js (that is render vocabulary). A phrase's surface_trap.type
  // must be one of these (phrases.test.js enforces it).
  const TRAP_TYPES = {
    'elided-mediator':
      'surface collapses A→M→B into a direct A→B; the mediating state is dropped',
    'misattributed-agency':
      'surface assigns the action or memory to the wrong glyph',
    'reversed-causality':
      'surface tempts the edge in the wrong direction (an un-inverted assumption)',
    'implicit-prior':
      'mechanism rides a stored state the surface omits (an omission — usually no trap edge)',
    'decorative-but-load-bearing':
      'an object the surface presents as flavour that the true mesh needs to carry an edge',
  };

  function facetPairs(mesh) {            // the set of "word.facet" a mesh declares
    const s = new Set();
    for (const g of (mesh.glyphs || [])) for (const f of (g.facets || [])) s.add(g.word + '.' + f);
    return s;
  }
  const edgeKey = (r) => (r.from || '') + '→' + (r.to || '');  // direction matters; label ignored for structure
  function edgeSet(mesh) {
    const s = new Set();
    for (const r of (mesh.relations || [])) s.add(edgeKey(r));
    return s;
  }

  function f1(recovered, truth) {        // F1 over two Sets (recovered vs truth)
    let tp = 0;
    for (const x of recovered) if (truth.has(x)) tp++;
    const precision = recovered.size ? tp / recovered.size : (truth.size ? 0 : 1);
    const recall = truth.size ? tp / truth.size : (recovered.size ? 0 : 1);
    const f = (precision + recall) ? 2 * precision * recall / (precision + recall) : 0;
    return { tp, precision, recall, f1: f };
  }

  // The penalty a trap costs the composite — one relation's worth of credit,
  // enough that taking the trap cannot net out as a good read.
  const TRAP_PENALTY = 0.5;
  const MECHANISM_RECALL = 0.75;  // "read the mechanism" = recovered most true edges AND avoided the trap

  function score(recovered, truth) {
    const facet = f1(facetPairs(recovered), facetPairs(truth));
    const relation = f1(edgeSet(recovered), edgeSet(truth));

    let trapEdge = null, trapHit = false;
    if (truth.surface_trap && truth.surface_trap.edge) {
      trapEdge = edgeKey(truth.surface_trap.edge);
      trapHit = edgeSet(recovered).has(trapEdge);
    }

    const base = (facet.f1 + relation.f1) / 2;
    const composite = Math.max(0, base - (trapHit ? TRAP_PENALTY : 0));
    const reads_mechanism = relation.recall >= MECHANISM_RECALL && !trapHit;

    return {
      facet, relation,
      trap: { defined: !!trapEdge, type: truth.surface_trap && truth.surface_trap.type, edge: trapEdge, hit: trapHit },
      base, composite, reads_mechanism,
    };
  }

  return { TRAP_TYPES, score, facetPairs, edgeSet, edgeKey, f1, TRAP_PENALTY, MECHANISM_RECALL };
});
