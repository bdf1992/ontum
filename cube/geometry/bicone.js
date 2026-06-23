// geometry/bicone.js — a DOUBLE-CONE (one CNEX axis).
//
// Two cones meeting tip-to-tip at the neck (origin): apex at center, wide
// mouth at each ±tip. The mouth IS the face (the typed surface); the neck is
// the polarity-inverting apex shared with the other two bicones.
//
// Returns a THREE.Group positioned at the origin, oriented along the axis dim.

import * as THREE from "three";
import { tipColor, PALETTE } from "../render/style.js";

const AXIS_VEC = [
  new THREE.Vector3(1, 0, 0),
  new THREE.Vector3(0, 1, 0),
  new THREE.Vector3(0, 0, 1),
];

// One cone with its APEX at the origin and its base centred at `tip`.
function halfCone(dim, sign, color, { reach = 1, mouth = 0.3, segments = 48 } = {}) {
  // ConeGeometry: apex at +height/2, base at -height/2, along +Y by default.
  const geo = new THREE.ConeGeometry(mouth, reach, segments, 1, true);
  // move so the apex sits at the origin, base out along +Y at distance `reach`
  geo.translate(0, -reach / 2, 0);
  geo.rotateX(Math.PI);                 // apex now at origin, base along +Y...
  // align +Y to the target axis*sign
  const target = AXIS_VEC[dim].clone().multiplyScalar(sign);
  const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), target);
  geo.applyQuaternion(q);

  const mat = new THREE.MeshStandardMaterial({
    color, transparent: true, opacity: 0.11, side: THREE.DoubleSide,
    metalness: 0.0, roughness: 0.65, depthWrite: false,
  });
  // the face marker (geometry/seams.js) provides the mouth ring, so the cone
  // is just the translucent field here — no ring, to avoid z-fighting.
  return new THREE.Mesh(geo, mat);
}

export function makeBicone(bicone, opts = {}) {
  const g = new THREE.Group();
  g.name = `bicone:${bicone.axis}`;
  g.userData = bicone;
  g.add(halfCone(bicone.dim, -1, tipColor(bicone.axis, -1), opts));
  g.add(halfCone(bicone.dim, +1, tipColor(bicone.axis, +1), opts));
  // the spine: a thin line through both cones, the readout axis
  const spine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([
      AXIS_VEC[bicone.dim].clone().multiplyScalar(-(opts.reach ?? 1)),
      AXIS_VEC[bicone.dim].clone().multiplyScalar(opts.reach ?? 1),
    ]),
    new THREE.LineBasicMaterial({ color: PALETTE.dim, transparent: true, opacity: 0.5 })
  );
  g.add(spine);
  return g;
}
