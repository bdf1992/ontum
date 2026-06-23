// render/scene.js — assembles a Three.js scene from a CNEX frame and drives
// the two views: the SPATIAL frame (bicones + parts in place) and the KNOLL
// (the 27 discrete parts laid flat, sorted by kind). Knows about pixels;
// reads the frame the model handed it and never re-derives topology.

import * as THREE from "three";
import { OrbitControls } from "../vendor/OrbitControls.js";
import { PALETTE, tipColor } from "./style.js";
import { makeBicone } from "../geometry/bicone.js";
import { makeFacePlane, makeEdgeTorus, makeCornerTriad, makeNeck } from "../geometry/seams.js";

const CAM0 = new THREE.Vector3(2.6, 2.0, 3.2);

export function createScene(canvas, frame) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(PALETTE.bg);

  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.copy(CAM0);

  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;

  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const key = new THREE.DirectionalLight(0xffffff, 0.85);
  key.position.set(-3, 5, 4);
  scene.add(key);

  // --- the spatial-only scaffold: the three double-cones ------------------
  const biconeGroup = new THREE.Group();
  for (const b of frame.bicones) biconeGroup.add(makeBicone(b));
  scene.add(biconeGroup);

  // --- the 27 discrete parts (faces, edges, corners, neck) ---------------
  const parts = [];      // { obj, kind, home, knoll } — positions live HERE,
                         // not on userData (the frozen model object).
  function track(obj, kind) {
    parts.push({ obj, kind, home: obj.position.clone(), knoll: obj.position.clone() });
    scene.add(obj);
  }
  for (const f of frame.faces) track(makeFacePlane(f), "face");
  // edge rings retracted (2026-06-23): the 12 "edges" may instead be the
  // openings at each end of the horns — the 6 face portals + 6 gateway holes
  // already = 12. Restore this line to bring the cube-edge loops back.
  // for (const e of frame.edges) track(makeEdgeTorus(e), "edge");
  // the triads are the corners of the NECK (not the external ±1 axis): pull
  // each unit corner in to the neck cube's corner.
  const NECK_R = 0.2;
  for (const c of frame.corners) {
    const m = makeCornerTriad(c);
    m.position.multiplyScalar(NECK_R);
    track(m, "corner");
  }
  track(makeNeck(frame.neck, { r: NECK_R }), "neck");

  // --- knoll layout: rows by kind, sorted ---------------------------------
  const ROW_Y = { face: 2.4, edge: 0.9, corner: -0.9, neck: -2.4 };
  const STEP = { face: 1.0, edge: 0.62, corner: 0.8, neck: 0.8 };
  const byKind = {};
  for (const p of parts) (byKind[p.kind] ||= []).push(p);
  for (const [kind, arr] of Object.entries(byKind)) {
    arr.forEach((p, i) => {
      p.knoll = new THREE.Vector3((i - (arr.length - 1) / 2) * STEP[kind], ROW_Y[kind], 0);
    });
  }

  // --- view mode ----------------------------------------------------------
  let knollTarget = 0, knollT = 0;
  function setMode(mode) { knollTarget = mode === "knoll" ? 1 : 0; }
  function resetView() { camera.position.copy(CAM0); controls.target.set(0, 0, 0); controls.update(); }

  function resize() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (canvas.width !== w || canvas.height !== h) {
      renderer.setSize(w, h, false);
      camera.aspect = w / h; camera.updateProjectionMatrix();
    }
  }
  window.addEventListener("resize", resize);

  function start(onFrame) {
    renderer.setAnimationLoop(() => {
      resize();
      controls.update();
      knollT += (knollTarget - knollT) * 0.12;
      const e = knollT * knollT * (3 - 2 * knollT);      // smoothstep
      for (const p of parts) p.obj.position.lerpVectors(p.home, p.knoll, e);
      biconeGroup.visible = e < 0.5;
      if (onFrame) onFrame();
      renderer.render(scene, camera);
    });
  }

  return { renderer, scene, camera, controls, parts, start, setMode, resetView };
}
