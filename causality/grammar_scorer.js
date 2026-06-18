/* grammar_scorer.js — the deterministic grammar / well-formedness gate
   (done-line story-grammar-wellformedness, outcome causality-story-benchmark).
   Pure, stdlib node, NO
   inference. The recovery-scorer asks "did the reader recover the true mesh?";
   THIS asks "is the story even coherent?" — so nonsense ("sunlight napped on the
   cat until the shadow ate the plant", bdo 2026-06-17) is refused at generation
   and never handed to graders. Type-by-composition gives the grammar for free.

   Two layers, two kinds of nonsense:
   - STRUCTURAL: every relation's facet pair must be LICENSED. A `source` may emit
     into a `state` but may NOT drive an `actor` directly — the mediating state
     must intervene (the SAME rule the elided-mediator trap tests). So
     "sunlight(source) → cat(actor)" is structurally malformed.
   - LEXICAL: a relation whose label verb is KNOWN (SUBJECT_FACET) must have a
     subject glyph carrying that verb's required facet. "shadow ate the plant" is
     structurally fine (signal→state) but "ate" needs an `actor`, and shadow
     {signal,time} has none. An UNKNOWN verb returns `unknown` — an honest gap
     (the loop/tags.py classify() discipline), never a false pass or fail.

   Truth-discipline: this resolves and counts, it never mints. The §10 teeth live
   in grammar_scorer.test.js — the nonsense is flagged, every real phrase is
   well-formed, and a constant scorer fails. */
(function (factory) {
  'use strict';
  const api = factory(require('./recovery_scorer.js'));
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof window !== 'undefined') window.CausalityGrammar = api;
})(function (R) {
  'use strict';

  // LICENSED facet→facet edges — the causal grammar, ONE declared table. Built
  // to cover every edge the real portfolio draws while keeping the mediator rule:
  // `source` does NOT reach `actor` (a supply drives an actor only THROUGH a
  // state). The test refuses any change that false-flags a real phrase or that
  // licenses source→actor.
  const LICENSED = {
    actor:     ['action', 'state', 'source', 'sink', 'memory', 'place'],
    objective: ['actor', 'action', 'source'],
    source:    ['state', 'objective', 'sink', 'memory'],   // emits / satisfies / is-remembered — NOT actor
    sink:      ['state'],
    signal:    ['actor', 'action', 'state', 'signal', 'source'],
    state:     ['actor', 'objective', 'signal', 'state', 'memory', 'place'],
    action:    ['state', 'source', 'sink', 'place'],
    memory:    ['actor', 'objective', 'signal', 'state', 'source', 'memory'],
    time:      ['state', 'signal', 'source', 'objective', 'memory'],
    place:     ['place', 'state'],
    gate:      ['state', 'action', 'signal'],
  };

  // SUBJECT_FACET — the facet a verb requires of its SUBJECT (the from-glyph).
  // Necessarily partial: an unknown verb is reported as `unknown`, never judged
  // (the honest-gap discipline). Conservative on purpose — only verbs whose
  // subject-facet is unambiguous, verified not to false-flag the corpus.
  const SUBJECT_FACET = {
    // actor verbs — an animate doer
    nap: 'actor', naps: 'actor', napped: 'actor', sleep: 'actor', sleeps: 'actor',
    rest: 'actor', rests: 'actor', eat: 'actor', eats: 'actor', ate: 'actor',
    drink: 'actor', drinks: 'actor', ask: 'actor', asks: 'actor', drop: 'actor',
    drops: 'actor', bury: 'actor', buries: 'actor', count: 'actor', counts: 'actor',
    water: 'actor', waters: 'actor', follow: 'actor', follows: 'actor', visit: 'actor', visits: 'actor',
    // source verbs — a supply emitting
    emit: 'source', emits: 'source', shine: 'source', shines: 'source',
    warm: 'source', warms: 'source', feed: 'source', feeds: 'source',
    offer: 'source', offers: 'source',
    // signal verbs — a marker firing
    fire: 'signal', fires: 'signal', alert: 'signal', alerts: 'signal',
    trigger: 'signal', triggers: 'signal', block: 'signal', blocks: 'signal',
    // memory verbs — a trace
    remember: 'memory', remembers: 'memory', record: 'memory', records: 'memory',
    forget: 'memory', forgets: 'memory',
    // objective verbs — a want
    want: 'objective', wants: 'objective',
  };

  function glyphFacets(mesh) {            // word -> Set(facets)
    const m = {};
    for (const g of (mesh.glyphs || [])) m[g.word] = new Set(g.facets || []);
    return m;
  }
  const firstVerb = (label) => {         // the leading word, lowercased, letters only
    const w = String(label || '').trim().toLowerCase().match(/[a-z]+/);
    return w ? w[0] : null;
  };

  function grammar(mesh) {
    const gl = glyphFacets(mesh);
    const structural = [], lexical = [], unknownVerbs = [];
    const rels = mesh.relations || [];
    for (const r of rels) {
      const [fw, ff] = String(r.from || '').split('.');
      const [, tf] = String(r.to || '').split('.');
      // STRUCTURAL — only judgeable when both endpoints name a facet
      if (ff && tf && !(LICENSED[ff] || []).includes(tf)) {
        structural.push({ edge: R.edgeKey(r), why: `${ff}↛${tf} (a ${ff} cannot reach a ${tf} directly)` });
      }
      // LEXICAL — only when the verb is known
      const v = firstVerb(r.label);
      if (v) {
        const req = SUBJECT_FACET[v];
        if (req === undefined) {
          if (!unknownVerbs.includes(v)) unknownVerbs.push(v);
        } else if (!(gl[fw] || new Set()).has(req)) {
          lexical.push({ edge: R.edgeKey(r), verb: v, why: `"${v}" needs a ${req} subject; ${fw} has {${[...(gl[fw] || [])].join(', ')}}` });
        }
      }
    }
    const violations = structural.length + lexical.length;
    return {
      wellFormed: violations === 0,
      score: rels.length ? Math.max(0, (rels.length - violations) / rels.length) : 1,
      structural, lexical, unknownVerbs, total: rels.length,
    };
  }

  return { LICENSED, SUBJECT_FACET, grammar, glyphFacets, firstVerb };
});
