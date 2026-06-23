// interaction/inspect.js — raycaster pick. Hover/click an element (face cone,
// edge torus, corner triad, neck) and surface what it is. Reads the primitive
// glossary fetched at runtime; never inlines it.

import * as THREE from "three";

export function attachInspector({ canvas, camera, scene, panel }, glossary) {
  const ray = new THREE.Raycaster();
  const ndc = new THREE.Vector2();

  function pickAt(ev) {
    const rect = canvas.getBoundingClientRect();
    ndc.x = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
    ndc.y = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
    ray.setFromCamera(ndc, camera);
    const hits = ray.intersectObjects(scene.children, true);
    for (const h of hits) {
      let o = h.object;
      while (o && !o.userData?.kind) o = o.parent;
      if (o?.userData?.kind) return o.userData;
    }
    return null;
  }

  function show(data) {
    if (!data) { panel.classList.remove("show"); return; }
    const g = glossary?.[data.kind] || {};
    const lines = [];
    lines.push(`<h2>${(g.title || data.kind).toUpperCase()}</h2>`);
    if (g.blurb) lines.push(`<p>${g.blurb}</p>`);
    if (data.axis) lines.push(`<p class="kv"><span>axis</span><span>${data.axis}</span></p>`);
    if (data.landmark) lines.push(`<p class="kv"><span>landmark</span><span>${data.landmark}</span></p>`);
    if (data.triad) lines.push(`<p class="kv"><span>triad</span><span>${data.triad.join(" · ")}</span></p>`);
    if (data.coord) lines.push(`<p class="src">coord (${data.coord.join(", ")})</p>`);
    if (data.note) lines.push(`<p class="src">${data.note}</p>`);
    panel.innerHTML = lines.join("");
    panel.classList.add("show");
  }

  canvas.addEventListener("click", (ev) => show(pickAt(ev)));
  return { pickAt, show };
}
