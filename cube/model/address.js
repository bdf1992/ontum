// model/address.js — a CNEX coordinate address.
//
// Two readings of the same state (README Primitives 8 & 10):
//   • the lattice address  (R, F, H)   — signed position on the three axes
//   • the cone-field state (d, θ, r)    — distance along the spine, angle
//                                         around the cone, radial contribution
//
// A line gives only d ∈ [-1,+1]; a cone-field resolves in a surface/volume,
// so the angle and radius carry information the line throws away.
//
// Pure: no DOM, no Three.js. Node-testable.

import { AXES, inBound, landmarkOf } from "./axis.js";

// (R, F, H) -> the named triad it reads as, within a frame.
export function readAddress({ region = 0, flow = 0, reach = 0 } = {}) {
  return {
    region: landmarkOf(AXES.region, region),
    flow: landmarkOf(AXES.flow, flow),
    reach: landmarkOf(AXES.reach, reach),
    valid: inBound(region) && inBound(flow) && inBound(reach),
  };
}

// A cone-field state. d is the signed spine distance; θ the angular facet
// around the cone (also bounded/signed here); r the radial contribution.
export function coneState({ d = 0, theta = 0, r = 0 } = {}) {
  return { d, theta, r };
}

// State fold (README Primitive 7): a coordinate is a snapshot; the deltas are
// the history; the fold resolves the history into the current state. Channels
// are never netted across each other — each axis folds on its own.
export function foldDeltas(deltas, base = { d: 0, theta: 0, r: 0 }) {
  return deltas.reduce(
    (s, Δ) => ({
      d: s.d + (Δ.delta_distance ?? Δ.d ?? 0),
      theta: s.theta + (Δ.delta_angle ?? Δ.theta ?? 0),
      r: s.r + (Δ.delta_radius ?? Δ.r ?? 0),
    }),
    { ...base }
  );
}
