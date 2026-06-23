// main.js — the wiring. model -> geometry -> render -> interaction. This is
// the only module that touches all layers; each layer below stays unaware of
// the ones above it.

import { buildFrame, checkInvariants } from "./model/cube-topology.js";
import { createScene } from "./render/scene.js";
import { attachInspector } from "./interaction/inspect.js";

const frame = buildFrame();

// dogfood the teeth in the console — the same invariants the node test asserts
const inv = checkInvariants(frame);
if (!inv.ok) console.warn("[cnex] invariants failed:", inv.fails);
else console.info("[cnex] frame ok — 3 bicones · 6 faces · 8 triads · 12 seams · 7 meeting points");

const canvas = document.getElementById("c");
const panel = document.getElementById("inspect");
const view = createScene(canvas, frame);

// load the primitive glossary at runtime (never inlined)
let glossary = {};
try {
  glossary = await (await fetch("./data/primitives.json")).json();
} catch (e) {
  console.warn("[cnex] glossary not loaded (serve over http):", e.message);
}

attachInspector({ canvas, camera: view.camera, scene: view.scene, panel }, glossary);

// controls
document.getElementById("bKnoll").addEventListener("click", (ev) => {
  view.setMode(ev.currentTarget.classList.toggle("on") ? "knoll" : "spatial");
});
document.getElementById("bReset").addEventListener("click", () => view.resetView());

// deep-link: open #knoll to start in the flat-lay view
if (location.hash === "#knoll") {
  view.setMode("knoll");
  document.getElementById("bKnoll").classList.add("on");
}

view.start();
