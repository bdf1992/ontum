/* text_to_system.js — the generative-instruction harness (arc.aim, the M2 inference
   layer). Raw text -> local inference -> a VALIDATED mesh -> scored against the
   held-out benchmark seed. The executable rendering of text-to-system.md: it injects
   the live vocabulary from canvas-system.js so the prompt never drifts from the
   single source. The seed mesh is NEVER an input to generation (anti-poison): the
   meaning is designed from the text, not lifted from the answer key. Node + browser. */
(function (root, factory) {
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = factory(require('./canvas-system.js'), require('./recovery_scorer.js'));
  } else {
    root.CausalityTextToSystem = factory(root.CausalitySystem, root.CausalityScorer);
  }
})(typeof self !== 'undefined' ? self : this, function (SYS, SCORER) {
  'use strict';
  const FACET = (SYS && (SYS.TOKENS ? SYS.TOKENS.FACET : SYS.FACET)) || {};
  const RELATION = (SYS && SYS.RELATION) || {};
  const composeRelation = SYS && SYS.composeRelation;

  // buildMeshPrompt(text) — the operative prompt, with the live FACET + RELATION
  // vocabulary injected. It takes ONLY the raw text; there is no parameter for the
  // seed, so it cannot be poisoned with the answer (the anti-poison guarantee).
  function buildMeshPrompt(text) {
    const facets = Object.keys(FACET).map(k => k + ' (' + FACET[k].read + ')').join('; ');
    const triples = Object.keys(RELATION).map(k => {
      const p = k.split('|'); return p[0] + '|' + p[1] + '|' + p[2] + ' = "' + RELATION[k].label + '"';
    }).join('; ');
    return [
      'You design the causal mechanism a phrase describes, as a typed graph. Output ONLY one JSON object, no prose, no code fence.',
      'Shape: { "glyphs": [ { "word": <a word from the text>, "facets": [<facet>...] } ], "relations": [ { "from": "<word>.<facet>", "to": "<word>.<facet>", "valence": "+" | "-" | <named transform> } ] }',
      'Facets name what a word DOES in the mechanism (not its part of speech): ' + facets + '.',
      'Relations: ONLY these declared composition triples are legal (fromFacet|toFacet|valence): ' + triples + '. If no triple fits a connection you want, leave it out — never invent a triple or a label.',
      'Rules: every glyph word must appear in the text; build the real causal chain AND its feedback; do not collapse a mediator (route through the mediating state, not a shortcut).',
      'The phrase:\n"""' + text + '"""',
    ].join('\n\n');
  }

  // pull the first JSON object out of a model reply (tolerant of stray prose/fences)
  function extractJSON(t) {
    if (typeof t !== 'string') return null;
    const a = t.indexOf('{'), b = t.lastIndexOf('}');
    if (a < 0 || b <= a) return null;
    try { return JSON.parse(t.slice(a, b + 1)); } catch (e) { return null; }
  }

  // validateMesh — the teeth (text-to-system.md). Refuses hallucinated words,
  // unknown facets, edges over facets a glyph does not carry, and undeclared triples
  // (composeRelation is the single authority on a legal edge). Refusal is honest
  // output; the harness renders nothing on a refusal (the authoring.js no-slop rule).
  function validateMesh(mesh, text) {
    const errors = [];
    if (!mesh || !Array.isArray(mesh.glyphs)) return { ok: false, errors: ['no glyphs[]'] };
    const lc = String(text || '').toLowerCase();
    const carried = {};                                  // word(lc) -> Set(facet)
    for (const g of mesh.glyphs) {
      if (!g || !g.word) { errors.push('a glyph has no word'); continue; }
      const w = String(g.word).toLowerCase();
      if (lc.indexOf(w) < 0) errors.push('glyph "' + g.word + '" is not in the text (hallucinated)');
      const fs = Array.isArray(g.facets) ? g.facets : [];
      for (const f of fs) if (!FACET[f]) errors.push('glyph "' + g.word + '" has unknown facet "' + f + '"');
      carried[w] = new Set(fs.filter(f => FACET[f]));
    }
    for (const r of (mesh.relations || [])) {
      const fp = String(r.from || '').split('.'), tp = String(r.to || '').split('.');
      const fw = (fp[0] || '').toLowerCase(), ff = fp[1], tw = (tp[0] || '').toLowerCase(), tf = tp[1];
      if (!carried[fw] || !carried[fw].has(ff)) errors.push('relation from "' + r.from + '" — no glyph carries that facet');
      if (!carried[tw] || !carried[tw].has(tf)) errors.push('relation to "' + r.to + '" — no glyph carries that facet');
      if (composeRelation && !composeRelation(ff, tf, r.valence))
        errors.push('relation ' + ff + '|' + tf + '|' + r.valence + ' is not a declared composition (invented edge)');
    }
    return { ok: errors.length === 0, errors };
  }

  // recover(text) — text -> inference -> validated mesh. The seed is not in scope.
  async function recover(text, opts) {
    opts = opts || {};
    const bridge = opts.bridge || (typeof window !== 'undefined' && window.CAUSALITY_BRIDGE) || 'http://localhost:8378/infer';
    const body = JSON.stringify({ prompt: buildMeshPrompt(text), backend: opts.backend || 'ollama', model: opts.model || null, timeout: opts.timeout || 120 });
    let j;
    try {
      const r = await fetch(bridge, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body });
      j = await r.json();
    } catch (e) { return { ok: false, errors: ['inference bridge unreachable: ' + (e.message || e)] }; }
    if (j && j.error) return { ok: false, errors: ['inference error: ' + j.error] };
    const mesh = extractJSON(j && j.result);
    if (!mesh) return { ok: false, errors: ['model did not return valid JSON'], raw: j && j.result };
    const v = validateMesh(mesh, text);
    if (!v.ok) return { ok: false, errors: v.errors, mesh };       // refused — no slop
    return { ok: true, errors: [], mesh };
  }

  // grade(recovered, truth) — score against the held-out seed (the oracle, AFTER
  // generation, never an input to it).
  function grade(recovered, truth) {
    if (!SCORER || !SCORER.score) return null;
    return SCORER.score(recovered, truth);
  }

  // truthFromPhrase — extract a phrases.json phrase's held-out mesh, for SCORING only.
  function truthFromPhrase(p) {
    return {
      glyphs: (p.glyphs || []).map(g => ({ word: g.word, facets: g.facets || [] })),
      relations: (p.relations || []).map(r => ({ from: r.from, to: r.to })),
      surface_trap: p.surface_trap || null,
    };
  }

  return { buildMeshPrompt, validateMesh, extractJSON, recover, grade, truthFromPhrase };
});
