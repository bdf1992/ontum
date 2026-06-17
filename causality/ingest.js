/* ingest.js — done-line 0096: the Causality canvas ingests REAL Ontum evidence.

   A pure, deterministic adapter from the COMMITTED term-economy projection
   (causality/examples/ontum-terms.projection.json, produced byte-deterministically
   by `term_economy.py project --write`) into the canvas's own graph shape — the
   exact object `canvas.js` S.fromJSON consumes. No network, no fold re-built here:
   this READS term_economy's committed output and keeps Causality a projection,
   never a second source of truth (the directory's one hard rule).

   The mapping (CZ3 of outcomes/causality-outcome-pressure.probes.json):
     - each real TERM        -> a `source` node, label = the term, data = its class
                                (source's `data` field is in the SCHEMA, so the class
                                 survives a toJSON/fromJSON round-trip)
     - each real EVIDENCE file -> a `sink` node, label = the file path
     - each RESOLVED evidence_edge -> a link term-node -> evidence-node

   The teeth (§10): an evidence_edge whose `from` term is NOT among the
   projection's terms cannot be drawn — drawing it would invent a node the
   projection never named. Such an edge is REFUSED (counted, reported), never
   silently turned into a dangling node. Two locally-fine records (a term list
   and an edge) refuse to fit, and the adapter notices.

   Runs under node (require) and the browser (window.CausalityIngest). */
'use strict';

// stable, deterministic node ids derived from the projection's own ids, so a
// re-ingest of the same committed bytes yields the same graph (replayable).
const SOURCE_HUES = ['#d98a3d', '#3d8ad9', '#8a3dd9', '#3dd98a', '#d93d8a'];

function projectionToGraph(projection) {
  if (!projection || !Array.isArray(projection.terms)) {
    return { ok: false, reason: 'not a projection: missing terms[]', graph: null, refusals: [] };
  }
  const terms = projection.terms;
  const edges = Array.isArray(projection.evidence_edges) ? projection.evidence_edges : [];

  const nodes = [];
  const links = [];
  const refusals = [];

  // id assignment: deterministic, dense, term nodes first then evidence nodes,
  // in the projection's own order (the projection is already sorted/stable).
  const idOf = new Map();          // projection id (term:x / evidence:y) -> canvas node id
  let next = 1;
  const place = (n, col) => { const cols = 6, gap = 180;
    n.x = 120 + (col % cols) * gap; n.y = 120 + Math.floor(col / cols) * gap; return n; };

  // term nodes — each carries its REAL class in `data` (a source-schema field)
  terms.forEach((t, i) => {
    if (t == null || t.id == null) { refusals.push({ kind: 'malformed-term', at: i }); return; }
    const id = next++;
    idOf.set(t.id, id);
    nodes.push(place({
      id, type: 'source', label: String(t.term != null ? t.term : t.id),
      data: String(t.class != null ? t.class : 'unclassified'),
      hue: SOURCE_HUES[i % SOURCE_HUES.length], autorun: false,
    }, i));
  });

  // evidence nodes — derived from the edges' `to` targets (evidence:<file>)
  const evIndex = new Map();       // projection evidence id -> column counter
  let evCol = 0;
  for (const e of edges) {
    const to = e && e.to;
    if (to == null || idOf.has(to)) continue;
    if (!String(to).startsWith('evidence:')) continue;
    const id = next++;
    idOf.set(to, id);
    const file = String(to).slice('evidence:'.length);
    nodes.push(place({ id, type: 'sink', label: file, hue: '#8895a6' }, terms.length + (evCol++)));
    evIndex.set(to, id);
  }

  // links — only edges whose BOTH ends resolved to real nodes; a `from` term the
  // projection never listed is the refusal the test has teeth for.
  for (const e of edges) {
    if (!e || e.from == null || e.to == null) { refusals.push({ kind: 'malformed-edge', edge: e && e.id }); continue; }
    const a = idOf.get(e.from), b = idOf.get(e.to);
    if (a == null) { refusals.push({ kind: 'dangling-term', edge: e.id, term: e.from }); continue; }
    if (b == null) { refusals.push({ kind: 'dangling-evidence', edge: e.id, target: e.to }); continue; }
    links.push({ a, b, sign: 1, kind: 'impulse', gain: 1, delay: 1 });
  }

  return {
    ok: true,
    reason: null,
    refusals,
    counts: { terms: terms.length, evidence: nodes.length - terms.length, links: links.length, refused: refusals.length },
    graph: { version: 1, baseline: 0.5, nextId: next, nodes, links },
  };
}

if (typeof module !== 'undefined' && module.exports) module.exports = { projectionToGraph };
if (typeof window !== 'undefined') window.CausalityIngest = { projectionToGraph };
