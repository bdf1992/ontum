# Gen-0 Construction Check

**The test (bdo):** can we build *every* gen-0 particle and field from its
components — before adding more? If one doesn't build, that's the gap to close
first. This reads each particle the way the cards do, but in *our* component
language.

Components in play: **role** (1/6/8/12) · **charge** (electric + iso, dual-rail) ·
**color** (RGB-cube + Null) · **flavor** (type × tier) · **spin** (winding) ·
**mass** (massless/mass/massive) · **parity** · **path** (trace) · **status**.

## Matter — the first generation (fermions)

| particle | role | charge (elec / iso) | color | spin | mass | builds? |
|---|---|---|---|---|---|---|
| **up (u)** | vertex | +2/3 / iso+ | R·G·B | ½ | mass | ✅ |
| **down (d)** | vertex | −1/3 / iso− | R·G·B | ½ | mass | ✅ |
| **electron (e⁻)** | vertex | −1 / iso− | **Null** (colorless) | ½ | mass | ✅ *needs color-Null* |
| **neutrino (νe)** | vertex | **Null** / iso≠0 | Null | ½ (chiral L) | ~massless | ✅ *the worked case* |
| **antiparticles** | — | through-neck inversion | invert | flip | = | ✅ *anti = neck-cross* |

## Fields — the force carriers (bosons)

| field | role | charge | color | spin | mass | builds? |
|---|---|---|---|---|---|---|
| **photon (γ)** | edge / field | 0 | Null | 1 | massless | ⚠ *spin-magnitude* |
| **gluon (g)** | **edge (binding)** | 0 | color·anticolor (8) | 1 | massless | ✅ *gluon = the edge* ⚠ spin |
| **W±** | edge / field | ±1 | Null | 1 | massive | ✅ *= the weak/flavor operator* ⚠ spin |
| **Z⁰** | edge / field | 0 | Null | 1 | massive | ⚠ *neutral-weak; spin* |
| **Higgs (H)** | field | 0 | Null | **0** (scalar) | massive | ⚠ *the mass mechanism (energy OPEN)* |

## Composites — gen-0 hadrons (color-neutral chains)

| object | makeup | charge | color | builds? |
|---|---|---|---|---|
| **proton** | u u d | +1 | neutral (R+G+B) | ✅ singlet |
| **neutron** | u d d | 0 | neutral | ✅ singlet |
| **pion (π⁺)** | u d̄ | +1 | neutral | ✅ meson |

## What builds cleanly

Quarks, electron, neutrino, antiparticles, proton/neutron/pion — **all build from
the components.** The gluon even resolves a role: it's the **edge (binding)**, which
is what cube-role 12 *was*. Color-neutrality (the singlet) builds every composite.

## The gaps to close *before* adding more (the point of this check)

1. **Spin magnitude.** Our spin is the winding *sense* (½ direction). The
   *magnitude* — ½ vs 1 vs 0 vs 2 = fermion / vector / scalar / tensor — isn't
   pinned. Candidate: **winding-number = magnitude**, **statistics (fermion/boson)
   = parity**. This is the biggest gap; almost every boson row hits it.
2. **Color-Null.** Color needs a **Null** (off-cube = colorless) for leptons,
   exactly like charge has Null per axis. Small, mechanical.
3. **The Higgs / mass mechanism.** Builds only once **energy** (the deferred
   renormalization) is defined — Higgs *is* the mass-setting field.
4. **Z⁰ (neutral weak).** The weak operator's neutral form — we have W (charged);
   Z is its neutral sibling.

## Verdict

Gen-0 is **~80% constructible** from current components. The four gaps above are
specific and bounded — close them and *every* gen-0 particle and field builds from
its makeup. **Then** add more. Nothing here is code yet; this is the spec that the
first build must satisfy.
