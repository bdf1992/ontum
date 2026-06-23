// model/cube-topology.js — the cube read as a CONAL-AXIAL frame, not XYZ.
//
// bdo's correction (2026-06-22): the core is NOT six independent face-cones.
// It is THREE DOUBLE-CONES (bicones) — one per axis (region/flow/reach) —
// that all share ONE central locus: the NECK, where polarity inverts
// (the -1 cone meets the +1 cone tip-to-tip at the setpoint 0).
//
//   • 3 double-cones  -> 6 outer tips  = the 6 FACES (typed surfaces)
//   • + the shared neck                = the 7th meeting point
//   • 8 corners                        = TRIADS (one landmark from each axis)
//   • 12 edges                         = chiral SEAMS (rendered as tori)
//
// So the "7 meeting points" = 6 faces + 1 neck. Euler still holds on the
// cube hull (V-E+F = 8-12+6 = 2); the neck is interior, the generator.
//
// Pure: no DOM, no Three.js. Coordinates are integer lattice points in
// {-1,0,+1}^3. This module is node-testable (the §10 teeth).

import { AXIS_LIST, landmarkOf } from "./axis.js";

const key = (c) => c.join(",");
const nonzero = (c) => c.filter((v) => v !== 0).length;

// ---- the neck: the interior generator where all three bicones cross -------
export const NECK = Object.freeze({
  kind: "neck",
  coord: [0, 0, 0],
  inverts: true,          // polarity flips through this locus
  note: "the locus where polarity inverts; shared apex of all 3 double-cones",
});

// ---- the 6 faces: the outer tips of the 3 double-cones --------------------
// One positive and one negative tip per axis. The face IS the cone's mouth.
export const FACES = Object.freeze(
  AXIS_LIST.flatMap((axis) =>
    [-1, 1].map((sign) => {
      const coord = [0, 0, 0];
      coord[axis.dim] = sign;
      return Object.freeze({
        kind: "face",
        coord,
        axis: axis.key,
        sign,
        landmark: sign < 0 ? axis.neg : axis.pos,
        note: `tip of the ${axis.key} double-cone`,
      });
    })
  )
);

// ---- the 8 corners: triads (one landmark from each of the three axes) -----
export const CORNERS = Object.freeze(
  [-1, 1].flatMap((x) =>
    [-1, 1].flatMap((y) =>
      [-1, 1].map((z) => {
        const coord = [x, y, z];
        return Object.freeze({
          kind: "corner",
          coord,
          triad: AXIS_LIST.map((axis) => landmarkOf(axis, coord[axis.dim])),
          note: "triadic junction — three surfaces meet",
        });
      })
    )
  )
);

// ---- the 12 edges: chiral seams between adjacent faces (drawn as tori) ----
// An edge is a pair of corners differing in exactly one coordinate; its
// direction is that one free axis (the torus' ring axis).
export const EDGES = Object.freeze(
  (() => {
    const out = [];
    for (let i = 0; i < CORNERS.length; i++) {
      for (let j = i + 1; j < CORNERS.length; j++) {
        const a = CORNERS[i].coord, b = CORNERS[j].coord;
        const diff = [0, 1, 2].filter((d) => a[d] !== b[d]);
        if (diff.length !== 1) continue;
        const dim = diff[0];
        const mid = [0, 1, 2].map((d) => (a[d] + b[d]) / 2);
        out.push(Object.freeze({
          kind: "edge",
          a: a.slice(), b: b.slice(),
          mid, dim,                       // dim = the torus ring axis
          note: "chiral seam between two faces",
        }));
      }
    }
    return out;
  })()
);

// ---- the 3 double-cones: the generators ----------------------------------
// Each bicone owns its two face tips and shares the neck.
export const BICONES = Object.freeze(
  AXIS_LIST.map((axis) =>
    Object.freeze({
      kind: "bicone",
      axis: axis.key,
      dim: axis.dim,
      neck: NECK.coord,
      negTip: FACES.find((f) => f.axis === axis.key && f.sign === -1).coord,
      posTip: FACES.find((f) => f.axis === axis.key && f.sign === 1).coord,
      note: `${axis.neg} cone | neck | ${axis.pos} cone`,
    })
  )
);

// The seven meeting points = six faces + the neck.
export const MEETING_POINTS = Object.freeze([...FACES, NECK]);

// One assembled frame, for the renderer and the tests to read from.
export function buildFrame() {
  return {
    neck: NECK,
    bicones: BICONES,
    faces: FACES,
    corners: CORNERS,
    edges: EDGES,
    meetingPoints: MEETING_POINTS,
  };
}

// ---- invariants the tests assert (the teeth) -----------------------------
// Re-derived here so a test failure points at the law it broke, not a magic
// number buried in a render call.
export const INVARIANTS = Object.freeze({
  bicones: 3,
  faces: 6,
  corners: 8,
  edges: 12,
  meetingPoints: 7,        // 6 faces + 1 neck — bdo's "7 meeting point"
  euler: 2,                // V - E + F on the cube hull
});

export function checkInvariants(frame = buildFrame()) {
  const fails = [];
  const want = (name, got, exp) => { if (got !== exp) fails.push(`${name}: got ${got}, want ${exp}`); };
  want("bicones", frame.bicones.length, INVARIANTS.bicones);
  want("faces", frame.faces.length, INVARIANTS.faces);
  want("corners", frame.corners.length, INVARIANTS.corners);
  want("edges", frame.edges.length, INVARIANTS.edges);
  want("meetingPoints", frame.meetingPoints.length, INVARIANTS.meetingPoints);
  want("euler", frame.corners.length - frame.edges.length + frame.faces.length, INVARIANTS.euler);
  // every face tip is owned by exactly one bicone
  for (const f of frame.faces) {
    const owners = frame.bicones.filter((b) => b.axis === f.axis);
    want(`face ${key(f.coord)} owner-count`, owners.length, 1);
  }
  // the neck is the shared apex: it is interior (all zero), and inverts
  want("neck interior", nonzero(frame.neck.coord), 0);
  return { ok: fails.length === 0, fails };
}
