/* authoring.js — the Interface-as-AI front door (done-line 0083): natural language
   → a schema-valid graph. You describe a node/site/graph; local inference generates
   a graph-spec in the toJSON shape; this module VALIDATES it against the SCHEMA
   before anything renders — a valid spec instantiates, an invalid one is refused
   with a legible reason (§10 teeth: no slop reaches the canvas).

   Browser: window.CausalityAuthoring (uses window.Causality + the inference bridge).
   Node:   module.exports (validateSpec / buildPrompt) for the deterministic test. */
(function () {
'use strict';
const C = (typeof window !== 'undefined' && window.Causality) || (typeof require !== 'undefined' && require('./canvas.js'));

// structural keys a node carries beyond its typed config fields
const STRUCTURAL = new Set(['id', 'x', 'y', 'type', 'hue', 'label', 'setline', 'card', 'boundTo']);

function allowedKeys(type) {
  const ks = new Set(STRUCTURAL);
  for (const f of C.fieldsFor(type)) ks.add(f.key.split('.')[0]);   // dotted (gate.mode) -> top-level (gate)
  return ks;
}

// validate a generated spec against the schema. returns {ok, errors[]}
function validateSpec(spec) {
  const errors = [];
  if (!spec || typeof spec !== 'object') return { ok: false, errors: ['spec is not an object'] };
  if (!Array.isArray(spec.nodes)) return { ok: false, errors: ['spec.nodes must be an array'] };
  const ids = new Set();
  spec.nodes.forEach((n, i) => {
    const at = `node[${i}]${n && n.label ? ' "' + n.label + '"' : ''}`;
    if (!n || typeof n !== 'object') { errors.push(`${at}: not an object`); return; }
    if (!C.TYPES.includes(n.type)) { errors.push(`${at}: unknown type "${n.type}" (valid: ${C.TYPES.join(', ')})`); return; }
    if (n.id != null) { if (ids.has(n.id)) errors.push(`${at}: duplicate id ${n.id}`); ids.add(n.id); }
    const allowed = allowedKeys(n.type);
    for (const k of Object.keys(n)) if (!allowed.has(k)) errors.push(`${at}: field "${k}" is not in the schema for type ${n.type}`);
  });
  for (const [i, l] of (spec.links || []).entries()) {
    const at = `link[${i}]`;
    if (!l || l.a == null || l.b == null) { errors.push(`${at}: missing a/b`); continue; }
    const A = spec.nodes.find(n => n.id === l.a), B = spec.nodes.find(n => n.id === l.b);
    if (!A) errors.push(`${at}: dangling — no node with id ${l.a}`);
    if (!B) errors.push(`${at}: dangling — no node with id ${l.b}`);
    if (A && B && !C.assignable(C.PORTS[A.type][1], C.PORTS[B.type][0]))
      errors.push(`${at}: incompatible ports ${C.PORTS[A.type][1]} ⇏ ${C.PORTS[B.type][0]} (${A.type}→${B.type})`);
  }
  return { ok: errors.length === 0, errors };
}

// the prompt the model generates against — the schema IS the contract
function buildPrompt(description) {
  const shape = C.TYPES.map(t => {
    const fields = (C.SCHEMA[t] || []).map(f => f.key.split('.')[0]).filter((v, i, a) => a.indexOf(v) === i);
    return `  ${t}: ${fields.length ? fields.join(', ') : '(no extra config)'}`;
  }).join('\n');
  return [
    'You generate a graph for a typed pulse-routing canvas. Output ONLY a single JSON object, no prose, no code fence.',
    'Shape: { "nodes": [ { "id": <int>, "type": <type>, "label": <string>, "x": <int>, "y": <int>, ...config } ], "links": [ { "a": <fromId>, "b": <toId>, "sign": 1, "kind": "impulse" } ] }',
    `Valid node types and their config fields:\n${shape}`,
    'Rules: every link a/b must be an existing node id; ids are integers; spread nodes across x in [80,1100], y in [80,600]; use only the listed types and fields.',
    `Describe the graph for this request:\n"""${description}"""`,
  ].join('\n\n');
}

// pull the first JSON object out of a model response (tolerates stray prose/fences)
function extractJSON(text) {
  if (typeof text !== 'string') return null;
  const a = text.indexOf('{'), b = text.lastIndexOf('}');
  if (a < 0 || b <= a) return null;
  try { return JSON.parse(text.slice(a, b + 1)); } catch (e) { return null; }
}

// the live flow (browser): describe -> inference -> validate -> instantiate.
// returns a promise of {ok, errors, spec}. On ok, the graph is rendered on S.
async function generate(S, description, opts = {}) {
  const bridge = opts.bridge || (typeof window !== 'undefined' && window.CAUSALITY_BRIDGE) || 'http://localhost:8378/infer';
  const body = JSON.stringify({ prompt: buildPrompt(description), backend: opts.backend || 'ollama', model: opts.model || null, timeout: 120 });
  let j;
  try { const r = await fetch(bridge, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body }); j = await r.json(); }
  catch (e) { return { ok: false, errors: ['inference bridge unreachable: ' + (e.message || e)] }; }
  if (j.error) return { ok: false, errors: ['inference error: ' + j.error] };
  const spec = extractJSON(j.result);
  if (!spec) return { ok: false, errors: ['model did not return valid JSON'], raw: j.result };
  const v = validateSpec(spec);
  if (!v.ok) return { ok: false, errors: v.errors, spec };       // refused — nothing renders (no slop)
  S.fromJSON(spec);                                              // valid draft -> instantiate + render
  return { ok: true, errors: [], spec };
}

const API = { validateSpec, buildPrompt, extractJSON, generate };
if (typeof window !== 'undefined') window.CausalityAuthoring = API;
if (typeof module !== 'undefined' && module.exports) module.exports = API;
})();
