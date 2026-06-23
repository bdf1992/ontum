// model/axis.js — a signed, bounded topological axis.
//
// Per the CNEX README (Primitive 8): an axis is NOT three categories. It is
// a continuous line on [-1, +1] with a neutral setpoint at 0 and two signed
// directions. Labels are landmarks; the axis between them is continuous.
//
// Pure: no DOM, no Three.js. This module is node-testable (the §10 teeth).

export const SETPOINT = 0;
export const BOUND = Object.freeze({ min: -1, max: 1 });

// The three independent axes of a CNEX address. Each becomes one double-cone.
//   negative landmark  ·  setpoint (neck)  ·  positive landmark
export const AXES = Object.freeze({
  region: { key: "region", dim: 0, neg: "internal", mid: "bound",  pos: "external" },
  flow:   { key: "flow",   dim: 1, neg: "ingress",  mid: "flux",   pos: "egress"   },
  reach:  { key: "reach",  dim: 2, neg: "local",    mid: "frame",  pos: "global"   },
});

export const AXIS_LIST = Object.freeze([AXES.region, AXES.flow, AXES.reach]);

// Is a value inside the (possibly shrunk) bound?
export function inBound(v, bound = BOUND) {
  return v >= bound.min && v <= bound.max;
}

// Signed drift from a setpoint: >0 toward the positive landmark, <0 toward
// the negative one, 0 at the setpoint.
export function drift(v, setpoint = SETPOINT) {
  return v - setpoint;
}

// The landmark a value reads as, by sign. The midpoint is the neck.
export function landmarkOf(axis, v, eps = 1e-9) {
  if (Math.abs(v) <= eps) return axis.mid;
  return v < 0 ? axis.neg : axis.pos;
}
