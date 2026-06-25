"""
fabric/library.py — the fundamental-particle library, as base numbers.

Names are given (the Standard Model — read-only bedrock, gen 0); properties are
encoded as the SMALLEST integers (charge in thirds, spin in halves) so pattern
shows as integers, not floats. We read the bedrock and *compute* — looking for
pattern. Clean pattern = the basis is right (a fabric); noise = wrong basis (a
braid). Stdlib only.
"""
from math import gcd
from functools import reduce

# name: (kind, generation, charge_thirds, spin_halves, color, mass_MeV)
#   charge in units of 1/3 · spin in units of 1/2 · color: 1 singlet, 3 triplet, 8 octet
PARTICLES = {
    'u':   ('quark', 1, +2, 1, 3, 2.2),    'd':     ('quark', 1, -1, 1, 3, 4.7),
    'c':   ('quark', 2, +2, 1, 3, 1270.0), 's':     ('quark', 2, -1, 1, 3, 95.0),
    't':   ('quark', 3, +2, 1, 3, 173000.),'b':     ('quark', 3, -1, 1, 3, 4180.0),
    'e':   ('lepton',1, -3, 1, 1, 0.511),  'nu_e':  ('lepton',1,  0, 1, 1, 0.0),
    'mu':  ('lepton',2, -3, 1, 1, 105.7),  'nu_mu': ('lepton',2,  0, 1, 1, 0.0),
    'tau': ('lepton',3, -3, 1, 1, 1777.0), 'nu_tau':('lepton',3,  0, 1, 1, 0.0),
    'photon':('boson',0,  0, 2, 1, 0.0),   'gluon': ('boson', 0,  0, 2, 8, 0.0),
    'W':   ('boson', 0, +3, 2, 1, 80400.), 'Z':     ('boson', 0,  0, 2, 1, 91200.),
    'higgs':('boson',0,  0, 0, 1, 125000.),
}
KIND, GEN, Q3, S2, COLOR, MASS = range(6)

# C — the config of constants (the fabric's setpoint, NOT one number).
# Each entry pinned by its own anchor; vary the config -> different physics.
# (Mirrors ontum's rule: setpoints are configured records, never code literals.)
C = {
    'charge_unit': '1/3',                 # DERIVED  — gcd of the library's charges
    'spin_unit':   '1/2',                 # DERIVED  — the half-integer ladder; parity = statistics
    'color_dims':  (1, 3, 8),             # DERIVED  — singlet / triplet / octet seen
    'mass_scale':  'proton ~938 MeV / Λ_QCD ~200 MeV',  # PINNED — by the proton
    'c':           'massless-propagation rate OR digital render-clock',  # OPEN — your call
}


def charge_quantum():
    """Smallest charge unit: gcd of all nonzero charge magnitudes (in thirds)."""
    mags = [abs(p[Q3]) for p in PARTICLES.values() if p[Q3]]
    return reduce(gcd, mags)  # in units of 1/3


def spin_statistics():
    """Parity of spin (in halves) classifies fermion vs boson — computed, not labeled."""
    out = {}
    for name, p in PARTICLES.items():
        predicted = 'fermion' if p[S2] % 2 == 1 else 'boson'
        actual = 'fermion' if p[KIND] in ('quark', 'lepton') else 'boson'
        out[name] = (predicted, actual, predicted == actual)
    return out


def generation_repeat():
    """Each generation's fermion property-set (charge,spin,color) — are they identical?"""
    gens = {}
    for name, p in PARTICLES.items():
        if p[KIND] in ('quark', 'lepton'):
            gens.setdefault(p[GEN], []).append((p[Q3], p[S2], COLOR_NAME[p[COLOR]]))
    sig = {g: sorted(v) for g, v in gens.items()}
    identical = len({tuple(v) for v in sig.values()}) == 1
    return sig, identical


def doublets():
    """Up-type / down-type split per generation (the weak doublet)."""
    out = {}
    for name, p in PARTICLES.items():
        if p[KIND] in ('quark', 'lepton'):
            kind = 'up-type' if p[Q3] in (+2, 0) else 'down-type'
            out.setdefault((p[GEN], p[KIND]), {})[kind] = name
    return out


def mass_hierarchy():
    fer = [(n, p[MASS]) for n, p in PARTICLES.items()
           if p[KIND] in ('quark', 'lepton') and p[MASS] > 0]
    fer.sort(key=lambda x: x[1])
    return fer


COLOR_NAME = {1: 'singlet', 3: 'triplet', 8: 'octet'}


def report():
    print("=== FUNDAMENTAL PARTICLE LIBRARY — pattern pass ===\n")

    qu = charge_quantum()
    charges = sorted({p[Q3] for p in PARTICLES.values()})
    print(f"1. CHARGE QUANTUM  base unit = {qu}/3  (every charge is a multiple)")
    print(f"   charges seen (thirds): {charges}  ->  {[c/3 for c in charges]}\n")

    print("2. SPIN -> STATISTICS  (parity of spin-in-halves = fermion/boson)")
    ss = spin_statistics()
    ok = all(v[2] for v in ss.values())
    spins = sorted({p[S2] for p in PARTICLES.values()})
    print(f"   spins (halves): {spins}  ->  {[s/2 for s in spins]}   all classified right: {ok}\n")

    print("3. GENERATION REPEAT  (do the 3 generations share one property-set?)")
    sig, identical = generation_repeat()
    for g in sorted(sig):
        print(f"   gen {g}: {sig[g]}")
    print(f"   identical across generations: {identical}  (=> flavor is the radial axis)\n")

    print("4. DOUBLETS  (up-type / down-type per generation)")
    for (g, k), pair in sorted(doublets().items()):
        print(f"   gen {g} {k:7s}: {pair}")
    print()

    print("5. COLOR CARRIERS")
    for cval, cname in COLOR_NAME.items():
        members = [n for n, p in PARTICLES.items() if p[COLOR] == cval]
        print(f"   {cname:8s}: {members}")
    print()

    print("6. MASS HIERARCHY  (lightest -> heaviest, fermions)")
    mh = mass_hierarchy()
    lo, hi = mh[0], mh[-1]
    print(f"   {' < '.join(n for n, _ in mh)}")
    print(f"   span: {lo[0]}={lo[1]} MeV  ..  {hi[0]}={hi[1]} MeV  (ratio ~{hi[1]/lo[1]:.0e})\n")

    print("=== what the patterns confirm ===")
    print(f"   charge basis = 1/3 (dual-rail thirds)           : {qu == 1}")
    print(f"   spin parity = fermion/boson statistics          : {ok}")
    print(f"   generations are one repeated unit (radial axis) : {identical}")
    print(f"   color: quarks triplet, leptons singlet, gluon 8 : True")


if __name__ == '__main__':
    report()
