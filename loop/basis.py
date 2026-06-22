"""basis.py — the pressure-relative basis instrument (v0, a checker, not a substrate).

The report's five primaries (APPEND · FOLD · HASH-IDENTITY · CITE · VERDICT) are not
*the* basis. They are one quantization of the transition space under one pressure
(work-medium accountability) — ontum's "RGB". Like colour, the basis has no correct
cardinality: B&W(1), grayscale(2), RGB(3), CMYK(4), PANTONE(n) are spanning sets over
the same spectrum, each fitted to a different pressure. This instrument makes that
mechanical.

The shaper (one load-bearing definition):
  - a REFUSAL is a DISCRIMINATION — a distinction a slot can reject on.
  - a PRESSURE is the SET of discriminations the medium must be able to preserve.
From that, the gamut law is computable:
  - COVERAGE: every required discrimination is enforced (by a slot, or by a stated
    reducible-composition of slots present).
  - GRIP: no slot is poetry (enforces nothing) and none is wholly redundant under P.

A basis move (SPLIT / MERGE / ADD / DROP) is legal only if it preserves coverage and
grip. That is what stops "flexible" from meaning "arbitrary": it is the colour-gamut
constraint — you may not merge two live discriminations (a gamut hole) nor split into a
child that discriminates nothing (poetry).

This module reads nothing from the live loop and mints no records. It is a thinking
instrument and the kernel of CTA-2's skill (the self-demote-POSTURE test below is
literally a basis move).
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple


# ── the three nouns ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Discrimination:
    """A distinction the medium may need to preserve. `reducible_to` names the slot
    roles whose joint presence already enforces it by composition; None = irreducible
    (it needs a slot of its own or it is lost)."""
    tag: str
    reducible_to: Optional[frozenset] = None


@dataclass(frozen=True)
class Slot:
    """A primary: a role + the discriminations it can refuse on. A slot that enforces
    nothing is poetry and is refused at shaping (CITE turned on the basis itself)."""
    role: str
    enforces: frozenset  # discrimination tags


@dataclass(frozen=True)
class Pressure:
    """The dial. A pressure is the set of discriminations the medium must preserve."""
    name: str
    required: Tuple[Discrimination, ...]

    @property
    def tags(self) -> frozenset:
        return frozenset(d.tag for d in self.required)


@dataclass(frozen=True)
class Move:
    """The result of attempting a basis edit or a cut."""
    op: str
    ok: bool
    reason: str
    basis: Optional[frozenset] = None  # the resulting basis if ok
    out: Optional[tuple] = None        # (slot, reality) for a cut


Basis = frozenset  # of Slot


# ── the gamut law ────────────────────────────────────────────────────────────

def roles(basis: Basis) -> frozenset:
    return frozenset(s.role for s in basis)


def covered(basis: Basis, d: Discrimination) -> bool:
    """A discrimination is covered if a slot enforces its tag directly, or if it is
    reducible and the composition that enforces it is present."""
    if any(d.tag in s.enforces for s in basis):
        return True
    if d.reducible_to is not None and d.reducible_to <= roles(basis):
        return True
    return False


def gamut_check(basis: Basis, p: Pressure) -> Tuple[bool, list]:
    """Coverage + grip. Returns (ok, violations)."""
    v = []
    # coverage: every required discrimination is preserved
    for d in p.required:
        if not covered(basis, d):
            v.append(f"UNCOVERED  {d.tag} — a discrimination {p.name} requires is lost")
    # grip 1: no poetry slot
    for s in basis:
        if not s.enforces:
            v.append(f"POETRY     {s.role} — enforces no discrimination")
    # grip 2: no wholly-redundant slot (its required tags all survive its removal)
    for s in basis:
        if not s.enforces:
            continue
        req_here = s.enforces & p.tags
        if not req_here:
            v.append(f"DEAD       {s.role} — enforces nothing {p.name} requires")
            continue
        smaller = basis - {s}
        if all(covered(smaller, d) for d in p.required if d.tag in req_here):
            v.append(f"REDUNDANT  {s.role} — its required refusals survive without it")
    return (len(v) == 0, v)


def fits(basis: Basis, p: Pressure) -> bool:
    return gamut_check(basis, p)[0]


# ── the four generative operators ────────────────────────────────────────────

def split(basis: Basis, role: str, children: Tuple[Slot, ...], p: Pressure) -> Move:
    """A role bifurcates when P distinguishes sub-roles it conflated.
    Legal iff every child carries a live refusal (no poetry) and coverage holds."""
    parent = _get(basis, role)
    if parent is None:
        return Move("SPLIT", False, f"no slot {role!r} to split")
    for c in children:
        if not c.enforces:
            return Move("SPLIT", False, f"illegal: child {c.role!r} enforces nothing — "
                                        f"a split child must keep a refusal (CITE-on-basis)")
    nb = (basis - {parent}) | set(children)
    ok, viol = gamut_check(nb, p)
    if not ok:
        return Move("SPLIT", False, "illegal: " + "; ".join(viol))
    return Move("SPLIT", True, f"{role} → {', '.join(c.role for c in children)}", nb)


def merge(basis: Basis, role1: str, role2: str, into: str, p: Pressure) -> Move:
    """Two roles fuse when P cannot tell them apart. Illegal if each carries a distinct
    live refusal — fusing them punches a gamut hole (a discrimination silently lost)."""
    s1, s2 = _get(basis, role1), _get(basis, role2)
    if s1 is None or s2 is None:
        return Move("MERGE", False, f"missing slot(s): {role1!r}/{role2!r}")
    a, b = s1.enforces & p.tags, s2.enforces & p.tags
    if (a - b) and (b - a):
        return Move("MERGE", False,
                    f"illegal: {role1} and {role2} carry distinct live refusals "
                    f"({sorted(a - b)} vs {sorted(b - a)}) — merging punches a gamut hole")
    merged = Slot(into, s1.enforces | s2.enforces)
    nb = (basis - {s1, s2}) | {merged}
    ok, viol = gamut_check(nb, p)
    if not ok:
        return Move("MERGE", False, "illegal: " + "; ".join(viol))
    return Move("MERGE", True, f"{role1} + {role2} → {into}", nb)


def add(basis: Basis, slot: Slot, p: Pressure) -> Move:
    """A new role when the medium has a discrimination the basis cannot express.
    Legal iff the slot carries a refusal AND that refusal is required-and-irreducible
    (not already covered)."""
    if not slot.enforces:
        return Move("ADD", False, f"illegal: {slot.role!r} enforces nothing")
    newly = [d for d in p.required
             if d.tag in slot.enforces and not covered(basis, d)]
    if not newly:
        return Move("ADD", False,
                    f"illegal: {slot.role} adds no discrimination {p.name} needs that "
                    f"is not already covered — redundant")
    nb = basis | {slot}
    return Move("ADD", True, f"+{slot.role} (earns {sorted(d.tag for d in newly)})", nb)


def drop(basis: Basis, role: str, p: Pressure) -> Move:
    """A role goes trivial when its refusal can never fire under P. Legal iff removing
    it preserves coverage (it was redundant or dead)."""
    s = _get(basis, role)
    if s is None:
        return Move("DROP", False, f"no slot {role!r} to drop")
    nb = basis - {s}
    if not all(covered(nb, d) for d in p.required):
        lost = [d.tag for d in p.required if not covered(nb, d)]
        return Move("DROP", False,
                    f"illegal: dropping {role} loses {lost} — a live discrimination")
    return Move("DROP", True, f"−{role} (its refusal never fires under {p.name})", nb)


def _get(basis: Basis, role: str) -> Optional[Slot]:
    for s in basis:
        if s.role == role:
            return s
    return None


# ── grounding: the corpus's discriminations ──────────────────────────────────
# Each maps to a verified refusal-tooth from the report.

DURABILITY = Discrimination("durability")                 # APPEND: torn write never happened
DERIVATION = Discrimination("derivation")                 # FOLD: state re-derived, never cached
IDENTITY   = Discrimination("identity")                   # HASH: same (node,hash) is no-op
BACKING    = Discrimination("backing")                    # CITE: unresolved citation refused
JUDGMENT   = Discrimination("judgment")                   # VERDICT: bounded, announcer may not judge

# AUTHORITY ("who may decide") is reducible under accountability: read the governance
# admission (FOLD over an APPENDed record) and let VERDICT check the actor. So it needs
# no slot of its own — it is covered by composition.
AUTHORITY  = Discrimination("authority", reducible_to=frozenset({"FOLD", "APPEND", "VERDICT"}))

# OWNER_SELF_ADMIT_FORBIDDEN (act_fence.py:21, D-4): a self-admit of an owner gesture is
# FORBIDDEN, full stop — irreducible to backing/judgment/authority. It needs its own slot.
OWNER_FORBIDDEN = Discrimination("owner_self_admit_forbidden", reducible_to=None)


def work_basis() -> Basis:
    return frozenset({
        Slot("APPEND",        frozenset({"durability"})),
        Slot("FOLD",          frozenset({"derivation"})),
        Slot("HASH-IDENTITY", frozenset({"identity"})),
        Slot("CITE",          frozenset({"backing"})),
        Slot("VERDICT",       frozenset({"judgment"})),
    })


ACCOUNTABILITY = Pressure("accountability",
                          (DURABILITY, DERIVATION, IDENTITY, BACKING, JUDGMENT, AUTHORITY))
GOVERNANCE     = Pressure("governance",
                          (DURABILITY, DERIVATION, IDENTITY, BACKING, JUDGMENT,
                           AUTHORITY, OWNER_FORBIDDEN))


# ── §10 self-test: admit the real moves, refuse the fakes ─────────────────────

def _show(m: Move):
    mark = "ADMIT " if m.ok else "REFUSE"
    print(f"  [{mark}] {m.op:5}  {m.reason}")
    return m


def demo():
    print("the five-primary work basis, under accountability pressure")
    wb = work_basis()
    ok, viol = gamut_check(wb, ACCOUNTABILITY)
    print(f"  fits(work, accountability) = {ok}"
          + ("" if ok else "  " + "; ".join(viol)))
    print("  (AUTHORITY is covered by FOLD∘APPEND∘VERDICT — no POSTURE slot needed)\n")

    print("1. POSTURE demotion — a legal DROP under accountability")
    with_posture = wb | {Slot("POSTURE", frozenset({"authority"}))}
    _show(drop(with_posture, "POSTURE", ACCOUNTABILITY))
    print("   (matches the report: POSTURE = FOLD over APPENDed admissions, reducible)\n")

    print("2. POSTURE re-emergence — a legal ADD under governance pressure")
    posture_gov = Slot("POSTURE", frozenset({"owner_self_admit_forbidden"}))
    _show(add(wb, posture_gov, GOVERNANCE))
    print("   (it re-earns a distinct, irreducible refusal: D-4, act_fence.py:21)\n")

    print("3. fabricated SPLIT — refused (a child that discriminates nothing)")
    _show(split(wb, "VERDICT",
                (Slot("VERDICT'", frozenset({"judgment"})),
                 Slot("FLAVOUR",  frozenset())), ACCOUNTABILITY))
    print()

    print("4. fabricated MERGE — refused (two distinct live refusals = gamut hole)")
    _show(merge(wb, "CITE", "VERDICT", "CITEDICT", ACCOUNTABILITY))
    print()

    print("5. legal MERGE — two slots not distinguished by the pressure")
    # build a basis where a redundant duplicate of FOLD exists, then merge it in
    dup = wb | {Slot("FOLD2", frozenset({"derivation"}))}
    _show(merge(dup, "FOLD", "FOLD2", "FOLD", ACCOUNTABILITY))


# ── the membrane: the seam lifted from "between stages" to "between a reality
#    and its basis". ⊘ is the prior it cuts into; the cut is its atomic act. ────

@dataclass(frozen=True)
class Reality:
    """A frame of axes, each opened (uncut, 0) or decided (cut, ±). The all-open frame
    is ⊘ — the pure prior, letterless, the wildcard center (glyphs/viewer.html:192).
    A reality has no slots until the membrane cuts axes in it."""
    name: str
    opened: frozenset
    decided: frozenset = frozenset()


def pure_prior(name: str, axes) -> Reality:
    """⊘ for a named reality: every axis open, nothing decided."""
    return Reality(name, frozenset(axes), frozenset())


def cut(reality: Reality, axis: str, p: Pressure, refusal: str) -> Move:
    """The membrane's atomic act — the seam, generalized. Decide one opened axis under a
    pressure, emitting a slot: VERDICT (decide the axis) durably collapsed by APPEND
    (0 → ±), at a seam. Gated by the gamut law on the act of slotting (CITE+VERDICT
    turned on the cut itself):
      - the axis must be open (you cannot re-cut a decided axis — HASH idempotence);
      - the cut must carry a refusal (a slot that discriminates nothing is poetry);
      - the refusal must be one the pressure requires (no gratuitous cuts)."""
    if axis not in reality.opened:
        return Move("CUT", False, f"{axis!r} is not open in {reality.name} — already cut or absent")
    if not refusal:
        return Move("CUT", False, f"poetry cut: deciding {axis!r} would distinguish nothing — refused")
    if refusal not in p.tags:
        return Move("CUT", False, f"gratuitous cut: {p.name} does not require {refusal!r}")
    slot = Slot(axis, frozenset({refusal}))
    nr = Reality(reality.name, reality.opened - {axis}, reality.decided | {axis})
    return Move("CUT", True,
                f"{reality.name}: cut {axis} ⟶ slot[{refusal}]  (now dim {len(nr.opened)})",
                out=(slot, nr))


def membrane_demo():
    print("\n" + "=" * 70)
    print("the membrane: one organ, two pressures — the seam between a reality and its basis")
    print("=" * 70 + "\n")

    print("WORK reality, under accountability pressure — the pipeline seam is one cut")
    work = pure_prior("work", {"durability", "judgment"})
    _show(cut(work, "judgment", ACCOUNTABILITY, "judgment"))
    print("   (the value-gate seam: VERDICT decides the 'has-value' axis at a seam)\n")

    print("MEANING reality — currently all-⊘ (the hollow center): the membrane has not")
    print("yet cut a single meaning-axis. CTA-1 is its FIRST stroke.")
    meaning = pure_prior("meaning", {"relate", "predict", "score"})
    print(f"   before: opened={sorted(meaning.opened)}  decided={sorted(meaning.decided)}\n")

    MEANING = Pressure("meaning", (Discrimination("relate"),
                                   Discrimination("predict"),
                                   Discrimination("score")))

    print("CTA-1 — the membrane's first cut under MEANING pressure")
    m = _show(cut(meaning, "relate", MEANING, "relate"))
    if m.ok:
        slot, meaning = m.out
        print(f"   after:  opened={sorted(meaning.opened)}  decided={sorted(meaning.decided)}")
        print("   (one decided axis = one meaning-slot = the reality begins to be inhabitable)\n")

    print("refused: a poetry cut (an axis that discriminates nothing)")
    _show(cut(meaning, "predict", MEANING, ""))
    print()
    print("refused: a gratuitous cut (right axis, wrong pressure — accountability has no 'score')")
    _show(cut(meaning, "score", ACCOUNTABILITY, "score"))


if __name__ == "__main__":
    demo()
    membrane_demo()
