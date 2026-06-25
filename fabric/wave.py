"""
fabric/wave.py — gen -1: the winding substrate, and its bounded modes.

bdo's insight: a WAVE is the 1-D compression (projection) of the WINDING (the
solenoid/helix). So there is no separate wave primitive — the wave IS the winding,
seen in lower dimension. The unbounded winding is gen -1 (the substrate);
BOUNDING it (the gen 0 config event) quantizes it into enumerable modes — the
particles. We create a bounded wave and study its modes against the library.
Stdlib only.
"""
import math, cmath


def helix(theta, radius=1.0, pitch=1.0, sense=+1):
    """A winding in 3-D: (r cosθ, r sinθ, pitch·θ/2π). sense = +1 / -1 = handedness."""
    return (radius * math.cos(sense * theta),
            radius * math.sin(sense * theta),
            pitch * theta / (2 * math.pi))


def project_1d(theta, radius=1.0, pitch=1.0, sense=+1):
    """Compress the winding to 1-D: (axial z, transverse x) = a sinusoid = a WAVE."""
    x, _, z = helix(theta, radius, pitch, sense)
    return (z, x)


def demo_projection(pitch=1.0, radius=1.0, sense=+1, steps=8):
    """Show the helix projects to a sine: z advances, x oscillates."""
    print("WAVE = 1-D compression of the WINDING  (helix -> sine)")
    print(f"  pitch={pitch} -> wavelength ; radius={radius} -> amplitude ; sense={sense:+d} -> handedness")
    for i in range(steps + 1):
        theta = 2 * math.pi * i / steps      # one full turn
        z, x = project_1d(theta, radius, pitch, sense)
        bar = int(round((x + radius) / (2 * radius) * 20))
        print(f"  z={z:4.2f}  x={x:+5.2f}  {' ' * bar}o")
    # the same winding with opposite sense is the mirror wave (handed color / helicity)
    print(f"  (sense {-sense:+d} = the mirror wave: same wavelength, opposite twist = handedness)\n")


def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def bounded_modes(n_modes=6, L=1.0):
    """Standing-wave modes on [0,L], fixed ends: λ_n = 2L/n, ratio λ_n/λ_1 = 1/n."""
    return [(n, 2 * L / n, 1.0 / n, is_prime(n)) for n in range(1, n_modes + 1)]


# what the library says are the load-bearing ratios (from library.py)
PHYSICAL_UNIT = {2: 'spin   (1/2 — duality / C2)',
                 3: 'charge (1/3 — triality / C3)'}


def reach(mass, k=1.0):
    """Yukawa reach ~ 1/mass: massless -> infinite (long-range), massive -> short."""
    return float('inf') if mass == 0 else k / mass


def helical_sim(a, b):
    """Complex inner product of two windings (lists of phasors r·e^{iθ}).
    Returns (magnitude, phase): magnitude = cosine-like ALIGNMENT;
    phase = sine-like relative WINDING (handedness). Keeps both."""
    inner = sum(x.conjugate() * y for x, y in zip(a, b))
    na = math.sqrt(sum(abs(x) ** 2 for x in a))
    nb = math.sqrt(sum(abs(y) ** 2 for y in b))
    if not na or not nb:
        return (0.0, 0.0)
    z = inner / (na * nb)
    return (abs(z), cmath.phase(z))


def plain_cosine(a, b):
    """Real cosine on the real parts only — DROPS the winding/handedness."""
    ar = [x.real for x in a]
    br = [y.real for y in b]
    dot = sum(p * q for p, q in zip(ar, br))
    na = math.sqrt(sum(p * p for p in ar))
    nb = math.sqrt(sum(q * q for q in br))
    return dot / (na * nb) if na and nb else 0.0


def demo_similarity():
    """Same color (alignment), opposite twist (handedness): cosine is blind, helical sees it."""
    left = [cmath.exp(1j * math.pi / 4)] * 4    # winds one way
    right = [cmath.exp(-1j * math.pi / 4)] * 4  # same color, opposite twist
    print("HELICAL SIMILARITY  (cosine + sine on the field, not cosine on an axis)")
    print(f"  plain cosine (real axis): {plain_cosine(left, right):+.3f}   <- says identical; blind to handedness")
    mag, ph = helical_sim(left, right)
    print(f"  helical (complex):        |align|={mag:.3f}  phase={ph:+.3f} rad   <- same alignment, OPPOSITE twist caught")
    print("  => cos = alignment, sin = the twist. Accumulated along the path = holonomy = provenance.\n")


def study():
    demo_projection()

    print("BOUNDING the winding -> enumerable modes  (gen -1 winding -> gen 0 modes)")
    print(f"  {'n':>2}  {'wavelength':>10}  {'ratio 1/n':>9}  {'prime?':>6}  correspondence")
    for n, lam, ratio, prime in bounded_modes():
        note = PHYSICAL_UNIT.get(n, 'composite' if not prime else '—')
        print(f"  {n:>2}  {lam:>10.4f}  {ratio:>9.4f}  {str(prime):>6}  {note}")

    print("\nPATTERN")
    print("  - mode 2 -> ratio 1/2 = the spin unit (duality)   [prime]")
    print("  - mode 3 -> ratio 1/3 = the charge unit (triality) [prime]")
    print("  - the two load-bearing ratios are the first two PRIME modes (2, 3).")
    print("  - composite modes (4=2², 6=2·3) are products, not new fundamentals.")

    print("\nHONEST EDGES")
    print("  - CONFIRMED: bounding quantizes (modes are enumerable); 1/2 & 1/3 = modes 2,3.")
    print("  - SPECULATIVE: 'prime modes = fundamental ratios' — 5,7 predict 1/5,1/7 units;")
    print("    no library unit claims those yet (gap, or they live in higher gens).")
    print("  - NOT shown: mode number does NOT give mass (masses aren't 1:2:3) — mass")
    print("    needs the field-stack/energy, not a single bounded wave. Modes explain")
    print("    QUANTIZATION (why discrete), not the VALUES (how heavy).")

    print()
    demo_similarity()
    print("A WAVE IS NOT A 1-D LINE  (that is the human drawing / a cross-section)")
    print("  real wave propagates in MANY directions; forces set by energy/spin/mass.")
    print("  REACH ~ 1/mass (Yukawa): massless -> long-range (photon/gluon),")
    print("  massive -> short-range (W/Z). It interacts with fields within its reach.")


if __name__ == '__main__':
    study()
