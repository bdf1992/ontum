/* canvas-system.js — Causality's canvas DESIGN SYSTEM (done-line 0103, iterations
   0001-0005). The single schema-driven source of tokens + primitives the canvas
   renders from: colors, node shapes, facet vocabulary, line types, easing,
   animation, physics, interaction, and an ASCII fallback. A new primitive ships
   as an ENTRY in a table here — never as bespoke render code (the agnosticism is
   the point; the same discipline as canvas.js SCHEMA and the Pattern Commons).

   Truth-discipline: this is a design vocabulary, not a second source of meaning.
   validate(spec) REFUSES any token/primitive absent from these tables — a
   fabricated or hand-rolled primitive fails (the §10 teeth in canvas-system.test.js).

   window.CausalitySystem = { TOKENS, validate, ascii } */
(function () {
'use strict';

// ── COLOR — semantic roles, the established cream/ink palette (look-and-feel) ──
const COLOR = {
  paper: '#f6f1e7', ink: '#2b2a33', dim: '#8d8678', faint: '#b8b1a2',
  positive: '#0e8a7b',   // teal — healthy / satisfies / flow
  strain: '#d4543f',     // rust — strain / interrupt / reject
  inference: '#7a5ba6',  // purple — thought / inference
  pulse: '#e8a13c',      // amber — a travelling pulse
  // the glyph/facet pigment ring (cycled deterministically by index)
  pigment: ['#0e8a7b', '#b8742c', '#7a5ba6', '#bf4a3e', '#3f7cb6', '#6b8f3c'],
};

// ── FACETS — the type-by-composition vocabulary (iterations 0004). Each facet:
//    glyph icon, ascii fallback, color role, and a one-line read. A glyph is a
//    BUNDLE of these; relations connect facets across glyphs. ──
const FACET = {
  actor:     { icon: '☖', ascii: '@', role: 'positive',  read: 'does — initiates action' },
  objective: { icon: '♡', ascii: '*', role: 'strain',    read: 'wants — a desired state' },
  source:    { icon: '≋', ascii: '^', role: 'pigment',   read: 'emits — a supply' },
  sink:      { icon: '▽', ascii: 'v', role: 'dim',       read: 'absorbs — a drain' },
  signal:    { icon: '!', ascii: '!', role: 'strain',    read: 'marks a change — fires' },
  state:     { icon: '○', ascii: 'o', role: 'pigment',   read: 'holds — a level' },
  place:     { icon: '▣', ascii: '#', role: 'pigment',   read: 'locates — a where' },
  action:    { icon: 'ƒ', ascii: 'f', role: 'positive',  read: 'transforms — computes' },
  memory:    { icon: '✎', ascii: '=', role: 'strain',    read: 'records — a trace' },
  time:      { icon: '◷', ascii: 't', role: 'inference', read: 'clocks — marks passing' },
  gate:      { icon: '⊟', ascii: '%', role: 'inference', read: 'admits or refuses' },
};

// ── NODE SHAPES — how a thing is drawn. holon = a glyph (composes facets);
//    facet = a small chip; membrane = a phrase boundary; card/readout reused. ──
const SHAPE = {
  holon:    { r: 36, fill: 0.12, label: 'caveat', composes: true },
  facet:    { r: 15, fill: 0.14, label: 'mono-sm', composes: false },
  membrane: { kind: 'blob', fill: 0.5, dash: true },
  card:     { w: 150, h: 96, kind: 'rect' },
  readout:  { w: 168, h: 70, kind: 'rect' },
};

// ── LINE TYPES — relation edge styles. dash null = solid; wobble = hand ink. ──
const LINE = {
  relation:       { dash: null,    width: 1.8, wobble: true,  arrow: true,  read: 'a directed relation' },
  feedback:       { dash: [7, 6],  width: 1.6, wobble: true,  arrow: true,  read: 'a loop / interrupt' },
  'cross-membrane': { dash: [2, 5], width: 1.4, wobble: true, arrow: false, read: 'a shared glyph between cells' },
  facet:          { dash: [3, 3],  width: 1.0, wobble: false, arrow: false, read: 'glyph → its facet' },
  proportional:   { dash: null,    width: 2.8, wobble: true,  arrow: true,  read: 'a continuous coupling' },
};

// ── EASING — named curves (t in 0..1 → eased) for animation + physics ──
const EASE = {
  linear:    t => t,
  easeInOut: t => t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
  easeOut:   t => 1 - Math.pow(1 - t, 3),
  spring:    t => 1 - Math.cos(t * Math.PI * 0.5) + Math.sin(t * Math.PI * 3) * 0.08 * (1 - t),
  breath:    t => 0.5 - 0.5 * Math.cos(t * Math.PI * 2),  // periodic, for membranes
};

// ── ANIMATION — named motions, each {ease, period(s)|once, amp} read by render ──
const ANIM = {
  wobble:        { ease: 'breath', period: 5.0,  amp: 0.6,  read: 'living-ink jitter, bound to energy' },
  'water-fill':  { ease: 'easeOut', period: null, amp: 1.0, read: 'a level rising to target' },
  'pulse-travel':{ ease: 'linear', period: null, amp: 1.0,  read: 'a message moving along an edge' },
  ring:          { ease: 'easeOut', once: 0.8,   amp: 1.0,  read: 'an activation ripple' },
  'membrane-breath': { ease: 'breath', period: 8.0, amp: 0.05, read: 'the cell wall, slowly' },
  'entrance-fade': { ease: 'easeInOut', once: 0.6, amp: 1.0, read: 'a node arriving' },
};

// ── PHYSICS — the field parameters (the analog substrate) ──
const PHYSICS = {
  drift: 0.05,        // return-to-baseline rate
  damping: 0.30,      // level → target lerp
  baseline: 0.5,
  'energy-coupling': 1.9,  // how system energy drives ink amplitude
  repulsion: 0,       // node spacing force (off until layout uses it)
};

// ── INTERACTION — gesture → act. The whole vocabulary of touch on the canvas ──
const INTERACT = {
  hover:        { act: 'reveal',   read: 'show metadata / tooltip, no commit' },
  click:        { act: 'select',   read: 'open the Lens on a glyph / relation / membrane' },
  'double-click': { act: 'add-or-zoom', read: 'new node on paper, or zoom a glyph open to its facets' },
  'drag-rim':   { act: 'wire',     read: 'draw a typed relation to another node' },
  'drag-body':  { act: 'move',     read: 'reposition a node' },
  'right-click':{ act: 'erase',    read: 'remove a node or edge' },
  pan:          { act: 'pan',      read: 'move the viewport' },
  lasso:        { act: 'select-many', read: 'enclose a region / form a membrane' },
  voice:        { act: 'speak',    read: 'dictate a phrase to compose' },
};

// ── LENS — what the inspector becomes per selection kind (the mockup's Lens) ──
const LENS = {
  glyph:    { shows: ['facets', 'connected-through'], read: 'a glyph and how it composes + connects' },
  relation: { shows: ['endpoints', 'explain', 'invert', 'stitch'], read: 'a facet-to-facet edge + its verbs' },
  membrane: { shows: ['counts', 'ask'], read: 'a phrase cell: glyphs/loops/edges + an inference query' },
};

// ── BUILD — construction-state (the game-dev "missing-texture" rule, done-line
//    0106). The oldest convention in the trade: an unfinished or placeholder asset
//    renders in a deliberately glaring magenta (the Source-engine purple/black
//    checker), so it can never be mistaken for finished or silently shipped. It is
//    ontum's mock-shame made visual on the canvas — a mock that moves fake work
//    cannot hide behind a clean surface. `real` renders normally; every flagged
//    state wears the magenta hazard so the state of construction is legible at a
//    glance. A new construction state ships as an ENTRY here, never bespoke code. ──
const BUILD = {
  real: { flag: false, color: null,      hatch: false, tag: null,   read: 'built and backed — renders in its own color' },
  mock: { flag: true,  color: '#ff2bd6', hatch: true,  tag: 'MOCK', read: 'a placeholder standing in for unbuilt structure — the missing-texture rule' },
  wip:  { flag: true,  color: '#ff2bd6', hatch: true,  tag: 'WIP',  read: 'declared but not finished — under construction' },
  todo: { flag: true,  color: '#ff2bd6', hatch: true,  tag: 'TODO', read: 'named, not yet started — a placeholder slot' },
};

// ── RELATION — type-by-composition for EDGES (iterations 0008). A relation is
//    NOT a hand-picked label: its type/label/inverse are GENERATED by the
//    composition of its endpoint facets + a valence, exactly as a glyph's type is
//    generated by its facets (0004), now extended from nodes to edges. A phrase
//    declares `(fromGlyph.facet, toGlyph.facet, valence)`; label + perspective are
//    DERIVED here, never authored. The key is `fromFacet|toFacet|valence`; valence
//    is the qualifier ('+' reinforcing, '-' opposing, or a named transform like
//    'fades'). Perspective is owned by the relation: "A blocks B" ≠ "B blocks A",
//    so each entry carries its `inverse` — the typed dual the flip generates. A
//    fabricated/hand-authored label has no home here: composeRelation REFUSES a
//    triple the table does not declare (the §10 teeth in canvas-system.test.js). ──
const RELATION = {
  // cat-sunbeam — the corrected chain (sunbeam feeds warmth; warmth satisfies the
  // cat's objective; shadow blocks warmth; the fading warmth wakes the cat)
  'source|state|+':     { type: 'feed',      label: 'feeds',       inverse: 'is fed by' },
  'state|objective|+':  { type: 'satisfy',   label: 'satisfies',   inverse: 'is satisfied by' },
  'signal|state|-':     { type: 'block',     label: 'blocks',      inverse: 'is blocked by' },
  'state|actor|fades':  { type: 'wake',      label: 'wakes',       inverse: 'is woken by' },
  // robot-plant
  'signal|actor|+':     { type: 'alert',     label: 'alerts',      inverse: 'is alerted by' },
  'actor|action|+':     { type: 'enact',     label: 'enacts',      inverse: 'is enacted by' },
  'state|state|+':      { type: 'raise',     label: 'raises',      inverse: 'is raised by' },
  'time|memory|+':      { type: 'review',    label: 'reviews',     inverse: 'is reviewed by' },
  // mouse-crumbs
  'actor|memory|+':     { type: 'record',    label: 'records',     inverse: 'is recorded by' },
  'state|objective|-':  { type: 'withhold',  label: 'withholds',   inverse: 'is withheld by' },
  'place|place|+':      { type: 'route',     label: 'leads to',    inverse: 'is reached from' },
  'memory|objective|+': { type: 'guide',     label: 'guides',      inverse: 'is guided by' },
  // owl-stars
  'actor|state|+':      { type: 'tend',      label: 'tends',       inverse: 'is tended by' },
  'state|signal|+':     { type: 'mark',      label: 'marks',       inverse: 'is marked by' },
  'signal|action|+':    { type: 'trigger',   label: 'triggers',    inverse: 'is triggered by' },
  'memory|signal|+':    { type: 'inform',    label: 'informs',     inverse: 'is informed by' },
  // caterpillar-leaf  (actor consuming a state — valence distinguishes it from 'tend')
  'actor|state|-':      { type: 'consume',   label: 'consumes',    inverse: 'is consumed by' },
  'source|objective|+': { type: 'draw',      label: 'draws',       inverse: 'is drawn by' },
  'objective|source|+': { type: 'seek',      label: 'seeks',       inverse: 'is sought by' },
  // bee-flower
  'source|memory|+':    { type: 'imprint',   label: 'imprints',    inverse: 'is imprinted by' },
  'memory|source|+':    { type: 'renew',     label: 'renews',      inverse: 'is renewed by' },
  // fox-berry
  'state|place|+':      { type: 'locate',    label: 'is at',       inverse: 'holds' },
  'memory|memory|-':    { type: 'forget',    label: 'is lost to',  inverse: 'loses track of' },
  // moth-light
  'actor|place|+':      { type: 'goto',      label: 'goes to',     inverse: 'is visited by' },
  'signal|source|-':    { type: 'dissolve',  label: 'dissolves',   inverse: 'is dissolved by' },
  'time|objective|-':   { type: 'expire',    label: 'ends',        inverse: 'is ended by' },
};

const relationKey = (fromFacet, toFacet, valence) => fromFacet + '|' + toFacet + '|' + valence;

// composeRelation(fromFacet, toFacet, valence) — the generator. Returns the typed
// relation { from, to, valence, type, label, inverse } or null if the triple is
// undeclared (the refusal: a label is NEVER hand-authored — add the composition to
// RELATION, do not invent a label at the call site). This is the only source of a
// relation's label; the renderer reads it, the corpus declares only the triple.
function composeRelation(fromFacet, toFacet, valence) {
  const e = RELATION[relationKey(fromFacet, toFacet, valence)];
  if (!e) return null;
  return { from: fromFacet, to: toFacet, valence, type: e.type, label: e.label, inverse: e.inverse };
}

// flipRelation(r) — the perspective flip as a GENERATIVE transform (0008): it does
// not reverse an arrow, it produces the typed DUAL (blocks ⟷ is-blocked-by) by
// swapping endpoints and exchanging label↔inverse. It is an involution by
// construction, so the law flip(flip(r)) deep-equals r (proven in the §10 test).
function flipRelation(r) {
  return { from: r.to, to: r.from, valence: r.valence, type: r.type, label: r.inverse, inverse: r.label };
}

const TOKENS = { COLOR, FACET, SHAPE, LINE, EASE, ANIM, PHYSICS, INTERACT, LENS, BUILD, RELATION };

// table name → the set of legal keys (EASE holds fns; the rest are data)
const TABLE = { color: COLOR, facet: FACET, shape: SHAPE, line: LINE, ease: EASE, anim: ANIM, physics: PHYSICS, interact: INTERACT, lens: LENS, build: BUILD, relation: RELATION };

// validate(table, key) — the §10 teeth: a primitive/token is legal ONLY if the
// table declares it. A fabricated or hand-rolled one is refused with a reason.
function validate(table, key) {
  const t = TABLE[table];
  if (!t) return { ok: false, reason: `unknown table "${table}" — tables: ${Object.keys(TABLE).join(', ')}` };
  if (table === 'color' && key === 'pigment') return { ok: true };
  if (!(key in t)) return { ok: false, reason: `"${key}" is not a declared ${table} token — add it to canvas-system.js, do not hand-roll it (the agnosticism is the point)` };
  return { ok: true };
}

// ascii(facet) — the no-graphics fallback glyph for a facet (ASCII-only render)
function ascii(facetKey) {
  const f = FACET[facetKey];
  return f ? f.ascii : '?';
}

if (typeof window !== 'undefined') window.CausalitySystem = { TOKENS, TABLE, validate, ascii, RELATION, relationKey, composeRelation, flipRelation };
if (typeof module !== 'undefined' && module.exports) module.exports = { TOKENS, TABLE, validate, ascii, RELATION, relationKey, composeRelation, flipRelation };
})();
