"""The deterministic half of Pivot: cube frame, populations, grader, scale.

Never calls a model. Reuses glyphs/knoll.py's cube — `ternary_cells`,
`cell_kind`, `verify_incidence_laws` — and never re-derives the lattice
(done-line 0031). A recovery is a placement of occupants onto addresses;
the grader checks it is a lawful tiling first and refuses it otherwise,
then scores how well meaning recovered position.
"""
import json
import os

from glyphs.knoll import ternary_cells, cell_kind, verify_incidence_laws

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S_FRAME_PATH = os.path.join(REPO_ROOT, "language", "s-frame-placements.json")

# The lawful census: a placement must tile the 27 cells exactly once each.
# (8 + 12 + 6 + 1 = 27 — the law that bites when a recovery refuses to fit.)
LAWFUL_CENSUS = {"corner": 8, "edge": 12, "face": 6, "center": 1}

SIGN_NAME = {-1: "neg", 0: "zero", 1: "pos"}


class RefusedToFit(Exception):
    """A recovery that is not a lawful tiling of the cube — the grader's
    refusal, the §10 gate doing its job."""


# --- the reference frame -----------------------------------------------------

def reference_frame():
    """coord -> kind, the ground truth the recoverer is graded against.
    Derived from knoll's cube, not re-stated here."""
    return {c: cell_kind(c) for c in ternary_cells()}


def chance_kind_match():
    """E[kind-match] for a uniformly random bijection — the theoretical
    floor a random-word population should land near. Σ n_k² / 27²."""
    counts = {}
    for c in ternary_cells():
        counts[cell_kind(c)] = counts.get(cell_kind(c), 0) + 1
    return sum(n * n for n in counts.values()) / (27 * 27)


# --- the three calibration populations ---------------------------------------
# Each is a *truth* placement: word -> coord. The harness hides the mapping,
# a cold agent recovers it, the grader compares kinds. Where the S-frame's
# score sits between the random floor and the surface ceiling is the number.

RANDOM_WORDS = [
    "river", "copper", "violin", "marble", "lantern", "cactus", "harbor",
    "pencil", "thunder", "almond", "ribbon", "glacier", "saddle", "ember",
    "walnut", "compass", "meadow", "kettle", "falcon", "pebble", "ladder",
    "orchard", "mitten", "anchor", "blossom", "trumpet", "willow",
]


def random_population():
    """Floor: 27 unrelated nouns on the cells in a fixed order. No relation
    between word and position, so recovery can only reach chance."""
    cells = ternary_cells()
    assert len(RANDOM_WORDS) == len(cells) == 27
    return {RANDOM_WORDS[i]: cells[i] for i in range(27)}


def surface_population():
    """Ceiling: the coord is transparent in the token (the cube's Pilish
    analog). A competent cold reader should recover it near-perfectly."""
    return {
        "x-%s_y-%s_z-%s" % (SIGN_NAME[x], SIGN_NAME[y], SIGN_NAME[z]): (x, y, z)
        for (x, y, z) in ternary_cells()
    }


def s_frame_population(path=S_FRAME_PATH):
    """The test object: the 27 S-words, PROPOSED / MODEL-GUESSED. Pivot
    measures against these placements, it does not mint them."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return {name: tuple(p["coord"]) for name, p in data["placements"].items()}


POPULATIONS = {
    "random": random_population,
    "s-frame": s_frame_population,
    "surface": surface_population,
}


# --- the grader (deterministic; refuses before it scores) --------------------

def assert_lawful_tiling(placement):
    """Refuse unless `placement` (key -> coord) tiles the 27 cells once each.
    Two occupants in one cell, a non-cell coord, or a left-empty cell each
    break the census — the recovery refuses to fit (§10)."""
    valid = set(ternary_cells())
    seen = {}
    for key, raw in placement.items():
        coord = tuple(raw)
        if coord not in valid:
            raise RefusedToFit("%r names a non-cell %r" % (key, coord))
        if coord in seen:
            raise RefusedToFit(
                "cell %r claimed twice: %r and %r" % (coord, seen[coord], key)
            )
        seen[coord] = key
    empty = valid - set(seen)
    if empty:
        raise RefusedToFit(
            "%d cell(s) left empty, e.g. %r" % (len(empty), sorted(empty)[:3])
        )
    census = {}
    for coord in seen:
        census[cell_kind(coord)] = census.get(cell_kind(coord), 0) + 1
    if census != LAWFUL_CENSUS:
        raise RefusedToFit("census %r != lawful %r" % (census, LAWFUL_CENSUS))


def grade(recovery, truth):
    """Score a recovery against a truth placement. Refuses first if the
    recovery is not a lawful tiling or does not cover the same occupants.

    Returns kind_match (the semantic metric — did meaning land the right
    *kind* of cell) and exact_match (did it land the exact coord, which is
    only well-posed once the axis convention is revealed)."""
    recovery = {k: tuple(v) for k, v in recovery.items()}
    truth = {k: tuple(v) for k, v in truth.items()}
    if set(recovery) != set(truth):
        missing = set(truth) - set(recovery)
        extra = set(recovery) - set(truth)
        raise RefusedToFit(
            "occupants differ: missing %r, extra %r"
            % (sorted(missing)[:3], sorted(extra)[:3])
        )
    assert_lawful_tiling(recovery)
    n = len(truth)
    kind_hits = sum(
        1 for w in truth if cell_kind(recovery[w]) == cell_kind(truth[w])
    )
    exact_hits = sum(1 for w in truth if recovery[w] == truth[w])
    return {
        "n": n,
        "kind_match": kind_hits / n,
        "exact_match": exact_hits / n,
    }


def place_on_scale(score, floor, ceiling):
    """Where a score sits between the random floor and the surface ceiling.
    0.0 = noise, 1.0 = obvious. Clamped; undefined if the controls collapse."""
    if ceiling <= floor:
        return None
    return max(0.0, min(1.0, (score - floor) / (ceiling - floor)))


# --- the cold-recoverer prompt (the harness builds it; a cold agent plays) ---

def recovery_prompt(occupants):
    """The bare container, the occupant list, the mapping hidden. Handed to
    a cold agent that has never read the placements. Order is the caller's;
    pass a shuffled list so position carries no hint."""
    cells = ternary_cells()
    kinds = {}
    for c in cells:
        kinds.setdefault(cell_kind(c), []).append(c)
    lines = [
        "You are given %d words and an empty 3-D sign-cube." % len(occupants),
        "",
        "The cube has 27 addresses: every (x, y, z) with each coordinate in",
        "{-1, 0, 1}. An address's kind is set by how many coordinates are 0:",
        "  0 zeros -> corner (8 of them)",
        "  1 zero  -> edge   (12)",
        "  2 zeros -> face   (6)",
        "  3 zeros -> center (1, the pivot at (0,0,0))",
        "",
        "Each word belongs at exactly one address; together they fill all 27.",
        "Place each word where its MEANING fits the address — a coordinate of",
        "-1 reads as interior/inward on that axis, +1 as exterior/outward, 0 as",
        "on-the-boundary. Assign every word a distinct address.",
        "",
        "Words:",
    ]
    lines += ["  - %s" % w for w in occupants]
    lines += [
        "",
        "Answer with JSON only: an object mapping each word to its [x, y, z].",
    ]
    return "\n".join(lines)


def verify_container():
    """The container's own incidence laws (Σ=125), via knoll — verified
    before any occupant is placed. Returns knoll's law summary."""
    return verify_incidence_laws()
