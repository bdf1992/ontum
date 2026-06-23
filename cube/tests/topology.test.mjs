// tests/topology.test.mjs — the §10 teeth for the CNEX frame.
// Run: node --test cube/tests/   (from the repo root)
//
// The model layer is pure (no Three.js, no DOM), so it runs straight under
// node. These tests assert bdo's structure — 3 double-cones, 7 meeting
// points — AND prove the check is not vacuous: a broken frame is caught.

import { test } from "node:test";
import assert from "node:assert/strict";
import {
  buildFrame, checkInvariants, INVARIANTS,
  FACES, CORNERS, EDGES, BICONES, MEETING_POINTS, NECK,
} from "../model/cube-topology.js";

test("the frame satisfies its invariants", () => {
  const res = checkInvariants();
  assert.ok(res.ok, "invariants failed: " + res.fails.join("; "));
});

test("3 double-cones, 6 face tips, 8 triads, 12 seams", () => {
  assert.equal(BICONES.length, 3);
  assert.equal(FACES.length, 6);
  assert.equal(CORNERS.length, 8);
  assert.equal(EDGES.length, 12);
});

test("7 meeting points = 6 faces + the neck (bdo's count)", () => {
  assert.equal(MEETING_POINTS.length, 7);
  assert.equal(INVARIANTS.meetingPoints, 7);
  assert.ok(MEETING_POINTS.includes(NECK));
});

test("the neck is interior and inverts polarity", () => {
  assert.deepEqual(NECK.coord, [0, 0, 0]);
  assert.equal(NECK.inverts, true);
});

test("each face tip is owned by exactly one bicone, sharing the neck", () => {
  for (const f of FACES) {
    const owners = BICONES.filter((b) => b.axis === f.axis);
    assert.equal(owners.length, 1, `face ${f.coord} should have one owning bicone`);
    assert.deepEqual(owners[0].neck, NECK.coord, "every bicone shares the neck");
  }
});

test("every corner is a distinct triad of three landmarks", () => {
  const seen = new Set();
  for (const c of CORNERS) {
    assert.equal(c.triad.length, 3);
    seen.add(c.triad.join("|"));
  }
  assert.equal(seen.size, 8, "all eight triads are distinct");
});

test("Euler holds on the cube hull", () => {
  assert.equal(CORNERS.length - EDGES.length + FACES.length, 2);
});

// --- non-vacuous: the check must FAIL on a broken frame (the §10 test) ---
test("checkInvariants rejects a frame missing a bicone", () => {
  const frame = buildFrame();
  frame.bicones = frame.bicones.slice(0, 2); // drop one double-cone
  const res = checkInvariants(frame);
  assert.equal(res.ok, false, "a 2-bicone frame must be refused");
});

test("checkInvariants rejects a frame with a 6th... wrong meeting-point count", () => {
  const frame = buildFrame();
  frame.meetingPoints = frame.meetingPoints.slice(0, 6); // drop the neck
  const res = checkInvariants(frame);
  assert.equal(res.ok, false, "6 meeting points (no neck) must be refused");
});
