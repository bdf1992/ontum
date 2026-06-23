// geometry/seams.js — the discrete, pickable parts of the frame: the 6 FACE
// markers, 12 EDGE TORI, 8 CORNER TRIADS, and the NECK. Each is a small
// object positioned at its own coordinate (geometry local to the object's
// origin) so the renderer can move it freely — that is what lets them knoll.

import * as THREE from "three";
import { PALETTE, tipColor } from "../render/style.js";

const AXIS_VEC = [
  new THREE.Vector3(1, 0, 0),
  new THREE.Vector3(0, 1, 0),
  new THREE.Vector3(0, 0, 1),
];
const Z = new THREE.Vector3(0, 0, 1);
const Y = new THREE.Vector3(0, 1, 0);

// A face: the bounding-cube PLANE that caps a cone (the "another layer of
// topology" where concepts/code/systems get placed), with a PORTAL/THRESHOLD
// ring at its centre — the inlet where the open cone funnels through to the
// neck/gateway.
export function makeFacePlane(face, { size = 2, portalR = 0.3, tube = 0.022 } = {}) {
  const g = new THREE.Group();
  g.name = "face"; g.userData = face;
  const color = tipColor(face.axis, face.sign);
  const dir = new THREE.Vector3(...face.coord).normalize();
  const q = new THREE.Quaternion().setFromUnitVectors(Z, dir);
  // the cube face — the placement layer (kept very faint so the interior reads)
  const plane = new THREE.Mesh(
    new THREE.PlaneGeometry(size, size),
    new THREE.MeshStandardMaterial({ color, transparent: true, opacity: 0.05, side: THREE.DoubleSide, depthWrite: false })
  );
  // the portal / threshold — the opening of the cone through the face
  const portal = new THREE.Mesh(
    new THREE.TorusGeometry(portalR, tube, 10, 44),
    new THREE.MeshStandardMaterial({ color, metalness: 0.2, roughness: 0.4 })
  );
  plane.quaternion.copy(q); portal.quaternion.copy(q);
  g.add(plane, portal);
  g.position.copy(new THREE.Vector3(...face.coord));
  return g;
}

// A simple edge ring at the edge midpoint, axis along the edge — the plain
// 12-edge placeholder, kept while the tori↔cube mapping is still an open
// question (braid retracted 2026-06-23).
export function makeEdgeTorus(edge, { ringR = 0.15, tube = 0.02 } = {}) {
  const mesh = new THREE.Mesh(
    new THREE.TorusGeometry(ringR, tube, 10, 36),
    new THREE.MeshStandardMaterial({ color: PALETTE.edge, metalness: 0.1, roughness: 0.5, transparent: true, opacity: 0.9 })
  );
  mesh.quaternion.setFromUnitVectors(Z, AXIS_VEC[edge.dim]);
  mesh.position.set(edge.mid[0], edge.mid[1], edge.mid[2]);
  mesh.name = "edge"; mesh.userData = edge;
  return mesh;
}

// An edge: a BRAIDED / Möbius edge running the length of the cube edge — the
// intersection locus where two dual-cone volumes cross and bind against the
// planes. Rendered as `strands` tubes helically wound around the edge line
// with a half-twist (turns=1 → Möbius-ish). Geometry is built relative to the
// edge midpoint so the part can still knoll.
export function makeEdgeBraid(edge, { strands = 3, r = 0.07, tubeR = 0.018, turns = 1, N = 48 } = {}) {
  const g = new THREE.Group();
  g.name = "edge"; g.userData = edge;
  const A = new THREE.Vector3(...edge.a);
  const B = new THREE.Vector3(...edge.b);
  const mid = new THREE.Vector3(...edge.mid);
  const perp = [0, 1, 2].filter((d) => d !== edge.dim).map((d) => AXIS_VEC[d]);
  for (let s = 0; s < strands; s++) {
    const base = (2 * Math.PI * s) / strands;
    const pts = [];
    for (let i = 0; i <= N; i++) {
      const t = i / N;
      const phi = base + turns * Math.PI * t;          // half-twist over the edge
      const c = new THREE.Vector3().lerpVectors(A, B, t).sub(mid);
      c.add(perp[0].clone().multiplyScalar(Math.cos(phi) * r))
       .add(perp[1].clone().multiplyScalar(Math.sin(phi) * r));
      pts.push(c);
    }
    const geo = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), N, tubeR, 8, false);
    g.add(new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: PALETTE.edge, metalness: 0.2, roughness: 0.45 })));
  }
  g.position.copy(mid);
  return g;
}

// A corner: a triad — three short struts from the junction inward along each
// axis. Geometry is built at the LOCAL origin; the group sits at the corner.
export function makeCornerTriad(corner, { strut = 0.12, tube = 0.016 } = {}) {
  const g = new THREE.Group();
  g.name = "corner"; g.userData = corner;
  for (let dim = 0; dim < 3; dim++) {
    const dir = AXIS_VEC[dim].clone().multiplyScalar(-Math.sign(corner.coord[dim])); // inward
    const geo = new THREE.CylinderGeometry(tube, tube, strut, 8);
    geo.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(Y, dir));
    geo.translate(...dir.clone().multiplyScalar(strut / 2).toArray());
    g.add(new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: PALETTE.corner, metalness: 0.2, roughness: 0.45 })));
  }
  const node = new THREE.Mesh(
    new THREE.SphereGeometry(0.035, 16, 12),
    new THREE.MeshStandardMaterial({ color: PALETTE.corner, emissive: PALETTE.corner, emissiveIntensity: 0.3 })
  );
  g.add(node);
  g.position.set(...corner.coord);   // unit corner; the renderer pulls it in to the neck
  return g;
}

// The neck: a small central CUBE — its 6 faces are the neck faces, its 8
// corners carry the triads, and the bright dot at its centre is the
// polarity-inverting locus (the 7th meeting point).
export function makeNeck(neck, { r = 0.2 } = {}) {
  const g = new THREE.Group();
  g.name = "neck"; g.userData = neck;
  const box = new THREE.Mesh(
    new THREE.BoxGeometry(2 * r, 2 * r, 2 * r),
    new THREE.MeshStandardMaterial({ color: PALETTE.neck, transparent: true, opacity: 0.1, depthWrite: false })
  );
  const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(2 * r, 2 * r, 2 * r)),
    new THREE.LineBasicMaterial({ color: PALETTE.neck, transparent: true, opacity: 0.5 })
  );
  const locus = new THREE.Mesh(
    new THREE.SphereGeometry(0.04, 16, 12),
    new THREE.MeshStandardMaterial({ color: PALETTE.neck, emissive: PALETTE.neck, emissiveIntensity: 0.6 })
  );
  g.add(box, edges, locus);
  // the holes where each cone pierces the inner cube — the inward recurrence
  // of the portal/threshold (one level today; the full fractal is later).
  for (let dim = 0; dim < 3; dim++) {
    for (const sign of [-1, 1]) {
      const dir = AXIS_VEC[dim].clone().multiplyScalar(sign);
      const hole = new THREE.Mesh(
        new THREE.TorusGeometry(0.06, 0.012, 8, 32),
        new THREE.MeshStandardMaterial({ color: PALETTE.neck, metalness: 0.3, roughness: 0.4 })
      );
      hole.quaternion.setFromUnitVectors(Z, dir);
      hole.position.copy(dir.clone().multiplyScalar(r));
      g.add(hole);
    }
  }
  g.position.set(...neck.coord);
  return g;
}
