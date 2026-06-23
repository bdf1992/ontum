// render/style.js — the palette and material factory. The ONLY place that
// knows hex codes. Ported from the source viewer's :root, extended per axis.

export const PALETTE = {
  bg:     0x0b0e14,
  ink:    0xd7dce6,
  dim:    0x8a93a6,
  neck:   0xffffff,   // the polarity-inverting locus, brightest
  // one hue per axis (the three double-cones)
  region: 0x59c2ff,   // R — blue
  flow:   0x27b54e,   // F — green
  reach:  0xb18cff,   // H — violet
  // structural roles
  face:   0xb18cff,
  edge:   0x3fd9c9,   // tori seams — teal
  corner: 0xffb454,   // triads — amber
};

export const AXIS_COLOR = {
  region: PALETTE.region,
  flow: PALETTE.flow,
  reach: PALETTE.reach,
};

// negative tips read cooler / dimmer than positive — sign is visible.
export function tipColor(axisKey, sign) {
  const base = AXIS_COLOR[axisKey];
  return sign < 0 ? shade(base, 0.62) : base;
}

export function shade(hex, k) {
  const r = Math.min(255, Math.round(((hex >> 16) & 255) * k));
  const g = Math.min(255, Math.round(((hex >> 8) & 255) * k));
  const b = Math.min(255, Math.round((hex & 255) * k));
  return (r << 16) | (g << 8) | b;
}
