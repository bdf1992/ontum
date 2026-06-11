"""The seed: the minimal compressed element a generation expands.

bdo's inversion (2026-06-11): the cube state should be regenerable from a
small seed — `{3 axes, 1 anchor, 27 addresses}` — and the benchmark asks
whether independent generations *replicate* from it. The seed is the
thing you iterate toward minimal-still-replicable, so it lives as data,
not as prose baked into a prompt.

A seed names three independent semantic axes (each with its −1 / 0 / +1
reading), one anchor concept that orients the whole cube, and inherits
the 27-address topology from the cube. `generation_prompt` expands it into
the instruction a cold generator plays; the returned {term: coord} flows
straight into the measurement battery — where, because the vocabulary is
now *generated* and not given, `vocab ⊖ placement` finally has something
to say.

This module ships ONE documented seed (`SEED_S`) as a starting point; it
carries its axes explicitly so it does not inherit the S-frame's
contaminated 'sit/act/read' law (the framing confound report 0031 names).
Editing the axes or anchor is iterating the seed — a new experiment.
"""

SEED_S = {
    "id": "s.v1",
    "anchor": "the parts of a bounded system",
    "axes": [
        {"name": "location",   "neg": "interior",  "zero": "boundary",   "pos": "exterior"},
        {"name": "agency",     "neg": "receptive", "zero": "mediating",  "pos": "active"},
        {"name": "visibility", "neg": "hidden",    "zero": "surfacing",  "pos": "observed"},
    ],
}


def generation_prompt(seed):
    """Expand a seed into the cold generator's instruction. The model
    generates 27 single-word terms (one per address) plus a one-line
    definition each, and returns JSON {term: [x, y, z]}. Nothing about any
    other generation is revealed — convergence must come from the seed."""
    ax = seed["axes"]
    lines = [
        "Generate the 27 parts of a conceptual cube from a seed.",
        "",
        "Anchor concept: %s." % seed["anchor"],
        "",
        "The cube has 27 addresses: every (x, y, z) with each coordinate in",
        "{-1, 0, 1}. The three axes carry meaning:",
        "  x = %s:  -1 %s / 0 %s / +1 %s"
        % (ax[0]["name"], ax[0]["neg"], ax[0]["zero"], ax[0]["pos"]),
        "  y = %s:  -1 %s / 0 %s / +1 %s"
        % (ax[1]["name"], ax[1]["neg"], ax[1]["zero"], ax[1]["pos"]),
        "  z = %s:  -1 %s / 0 %s / +1 %s"
        % (ax[2]["name"], ax[2]["neg"], ax[2]["zero"], ax[2]["pos"]),
        "",
        "For EVERY one of the 27 addresses, invent the single word (a noun)",
        "whose meaning best fits that address's three coordinates, anchored",
        "to the concept above. Each address gets exactly one distinct word;",
        "together they fill all 27. Give each a one-line definition.",
        "",
        "Answer with JSON only: an object mapping each word you chose to its",
        "[x, y, z]. (Put the definitions in a separate JSON object 'defs' if",
        "you include them; the placement object must map word -> [x,y,z].)",
    ]
    return "\n".join(lines)


SEEDS = {SEED_S["id"]: SEED_S}
