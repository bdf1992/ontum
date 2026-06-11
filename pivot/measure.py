"""The measurement battery: tensions over N generations, not one number.

The cube is graded (every cell carries its closure/star fan), so the
measurement is graded too — per piece, per grade, many metrics held
against each other. A run yields a *dataset*; the gaps between metrics
are the findings (bdo, chat 2026-06-11):

  WHY-detectors (diagnose the disagreement)
    orientation_slack = kind ⊖ exact      same kind of cell, wrong corner
                                          -> the gap is axis convention
    convention_slack  = aligned ⊖ raw     same cube, rotated
                                          -> the gap is orientation, not meaning
    (vocabulary ⊖ placement)              which link is weak: the words or
                                          where they land

  WHERE-detectors (localize it)
    per_grade        corner/edge/face/center — where structure holds
    by_distance      consensus vs axes-from-the-pivot — the seed's reach

Deterministic; never calls a model. Each generation is validated as a
lawful tiling first (refused otherwise — instrument.assert_lawful_tiling).
A generation is {term: coord}; generations may carry different vocabularies,
so placement metrics run on the *shared* terms and a separate vocabulary
metric measures the set overlap. Definition-convergence (the semantic
layer) is a named hole here — it needs an embedding or a judge and is not
the deterministic spine.
"""
import itertools
from collections import Counter

from glyphs.knoll import cell_kind, ternary_cells
from pivot.instrument import assert_lawful_tiling


def _mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def _modal_fraction(xs):
    """Fraction sharing the most common value — the consensus strength."""
    xs = list(xs)
    if not xs:
        return None
    return Counter(xs).most_common(1)[0][1] / len(xs)


# --- the cube's own symmetries (for convention_slack) ------------------------

def cube_symmetries():
    """The 48 signed axis-permutations that map {-1,0,1}³ onto itself
    (the octahedral group): permute the 3 axes (6) × flip each sign (8).
    Every one preserves cell-kind — zeros count is invariant."""
    return [
        (perm, signs)
        for perm in itertools.permutations((0, 1, 2))
        for signs in itertools.product((-1, 1), repeat=3)
    ]


def apply_symmetry(coord, sym):
    perm, signs = sym
    return tuple(signs[i] * coord[perm[i]] for i in range(3))


# --- the battery -------------------------------------------------------------

def _shared_terms(generations):
    counts = Counter()
    for g in generations:
        counts.update(g.keys())
    return {t for t, n in counts.items() if n >= 2}


def vocabulary_convergence(generations):
    """Set-level: do independent generations even pick the same terms?"""
    sets = [set(g) for g in generations]
    jac = []
    for a, b in itertools.combinations(sets, 2):
        union = a | b
        jac.append(len(a & b) / len(union) if union else 1.0)
    counts = Counter()
    for s in sets:
        counts.update(s)
    half = (len(generations) + 1) // 2
    consensus = [t for t, n in counts.items() if n >= half]
    return {
        "mean_pairwise_jaccard": _mean(jac),
        "consensus_vocab_size": len(consensus),
    }


def placement_convergence(generations):
    """On the shared vocabulary: do the same terms land in the same place?
    exact (the coord) and kind (the cell-kind); their gap is orientation."""
    shared = _shared_terms(generations)
    exact, kind = [], []
    for t in shared:
        coords = [tuple(g[t]) for g in generations if t in g]
        exact.append(_modal_fraction(coords))
        kind.append(_modal_fraction([cell_kind(c) for c in coords]))
    return {"exact": _mean(exact), "kind": _mean(kind), "n_terms": len(shared)}


def pairwise_alignment(generations):
    """Per pair, on shared terms: raw agreement, and agreement after the
    best of the 48 cube symmetries is applied to one side. If aligned ≫ raw,
    the two cubes are the same cube rotated — the scatter was convention."""
    syms = cube_symmetries()
    raw, aligned = [], []
    for ga, gb in itertools.combinations(generations, 2):
        common = set(ga) & set(gb)
        if not common:
            continue
        a = {t: tuple(ga[t]) for t in common}
        b = {t: tuple(gb[t]) for t in common}
        raw.append(sum(a[t] == b[t] for t in common) / len(common))
        best = max(
            sum(apply_symmetry(b[t], s) == a[t] for t in common)
            for s in syms
        )
        aligned.append(best / len(common))
    return {"raw": _mean(raw), "best_aligned": _mean(aligned)}


def per_grade(generations):
    """Per-cell term consensus, broken down by cell-kind — where structure
    holds. Maybe the extremes (corners) converge while mid-grades scatter."""
    inv = [{tuple(c): t for t, c in g.items()} for g in generations]
    buckets = {}
    for c in ternary_cells():
        occ = [d[c] for d in inv if c in d]
        if len(occ) < 2:
            continue
        buckets.setdefault(cell_kind(c), []).append(_modal_fraction(occ))
    return {k: _mean(v) for k, v in buckets.items()}


def consensus_by_distance(generations, anchor=(0, 0, 0)):
    """Per-cell consensus vs axes-differing from the anchor (default the
    pivot) — does agreement decay with distance from the seed?"""
    inv = [{tuple(c): t for t, c in g.items()} for g in generations]
    buckets = {}
    for c in ternary_cells():
        occ = [d[c] for d in inv if c in d]
        if len(occ) < 2:
            continue
        dist = sum(1 for k in range(3) if c[k] != anchor[k])
        buckets.setdefault(dist, []).append(_modal_fraction(occ))
    return {d: _mean(v) for d, v in sorted(buckets.items())}


def measure(generations, anchor=(0, 0, 0)):
    """The whole battery over N generations. Refuses any generation that is
    not a lawful tiling before measuring. Returns the readings AND the
    tensions between them — the gaps are the point."""
    if len(generations) < 2:
        raise ValueError("convergence needs >= 2 generations, got %d"
                         % len(generations))
    for g in generations:
        assert_lawful_tiling(g)
    vocab = vocabulary_convergence(generations)
    place = placement_convergence(generations)
    pair = pairwise_alignment(generations)
    grade = per_grade(generations)
    dist = consensus_by_distance(generations, anchor)

    def _gap(a, b):
        return None if a is None or b is None else a - b

    return {
        "n": len(generations),
        "vocabulary": vocab,
        "placement": place,
        "pairwise": pair,
        "per_grade": grade,
        "by_distance": dist,
        "tensions": {
            "orientation_slack": _gap(place["kind"], place["exact"]),
            "convention_slack": _gap(pair["best_aligned"], pair["raw"]),
            "vocab_minus_placement": _gap(
                vocab["mean_pairwise_jaccard"], place["exact"]
            ),
        },
    }


def rows(battery, seed_id):
    """Flatten one battery into dataset rows — (seed, scope, grade, metric,
    value) — so runs accumulate into a set, not a point."""
    out = []

    def add(scope, grade, metric, value):
        out.append({"seed": seed_id, "scope": scope, "grade": grade,
                    "metric": metric, "value": value})

    for k, v in battery["vocabulary"].items():
        add("global", None, "vocab.%s" % k, v)
    for k, v in battery["placement"].items():
        add("shared", None, "placement.%s" % k, v)
    for k, v in battery["pairwise"].items():
        add("pairwise", None, "pairwise.%s" % k, v)
    for grade, v in battery["per_grade"].items():
        add("per-grade", grade, "consensus", v)
    for dist, v in battery["by_distance"].items():
        add("by-distance", dist, "consensus", v)
    for k, v in battery["tensions"].items():
        add("tension", None, k, v)
    return out
