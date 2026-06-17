#!/usr/bin/env python3
"""Deterministic fold: 10 family files -> pattern-commons.v1.json + a gate summary.

Reads families/*.evolved.json, assembles the evolved Commons, and re-checks
every pattern's verdict against its axis scores (the final inflation gate).
Read-only on the family files; writes only pattern-commons.v1.json.
"""
import json, glob, os

HERE = os.path.dirname(os.path.abspath(__file__))
FAM_DIR = os.path.join(HERE, "families")
ORDER = ["living","topo","spatial","play","instr","hud","edit",
         "register","interface-ai","async"]

def axis_score(p):
    """Return (n_axes_present_at_partial_or_full, expected_verdict)."""
    ax = p.get("axis") or {}
    # agents used either 'register' or 'commitment' for axis #1
    a1 = ax.get("commitment", ax.get("register", "none"))
    a2 = ax.get("provenance", "none")
    a3 = ax.get("agent_drivable", ax.get("agent", "none"))
    hits = sum(1 for v in (a1,a2,a3) if str(v).lower() in ("partial","full"))
    if hits >= 2: exp = "ai-native"
    elif hits == 1: exp = "truth-capable"
    else: exp = "decoration"
    return hits, exp

def load(fid):
    path = os.path.join(FAM_DIR, fid + ".evolved.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)

families, patterns, mismatches, kin_links = [], [], [], 0
tally = {"decoration":0, "truth-capable":0, "ai-native":0}
new_ai_native = 0

for fid in ORDER:
    try:
        d = load(fid)
    except FileNotFoundError:
        print(f"  MISSING: {fid}.evolved.json"); continue
    fam = d.get("family", {"id": fid})
    families.append(fam)
    rows = []
    for tier_key, tier in (("patterns","v0-retag"), ("new_patterns","new")):
        for p in d.get(tier_key) or []:
            p = dict(p); p["_family"] = fam.get("id", fid); p["_tier"] = tier
            verdict = (p.get("verdict") or "").strip()
            hits, exp = axis_score(p)
            if verdict and verdict != exp:
                mismatches.append(f"{fid}:{p.get('id','?')} verdict={verdict} but axis says {exp} ({hits} axes)")
            if verdict in tally: tally[verdict] += 1
            if tier == "new" and verdict == "ai-native":
                globals().__setitem__("new_ai_native", new_ai_native+0)  # noop guard
            if p.get("kin"): kin_links += len(p["kin"])
            rows.append(p)
    patterns.extend(rows)

new_ai_native = sum(1 for p in patterns if p["_tier"]=="new" and (p.get("verdict")=="ai-native"))
v0_retag = sum(1 for p in patterns if p["_tier"]=="v0-retag")
new_total = sum(1 for p in patterns if p["_tier"]=="new")

commons = {
    "name": "pattern-commons",
    "version": 1,
    "evolved": "2026-06-16",
    "provenance": "Evolved from v0 via the evolution SDLC loop (RUBRIC + RECONCILIATION): "
                  "10 family agents, an independent review gate (18 issues), and a round-1 "
                  "revision on the reconciled commitment model (register=commitment/line, "
                  "strata=epistemic/colour, anima=felt/motion). v0 patterns honestly re-tagged; "
                  "new ai-native patterns authored for the three new families. PROPOSED tier — "
                  "promotion past proposed is bdo's (D-4).",
    "axes": {
        "register": "COMMITMENT on the propose->admit lifecycle (ink=admitted / pencil=proposed|simulated) -> line-treatment + badge",
        "strata": "EPISTEMIC origin (fundamental/derived/learned) -> colour / layer",
        "anima": "FELT field (strength x tempo) -> size / motion"
    },
    "families": families,
    "patterns": patterns,
    "landmarks_note": "v0 landmarks retained; 2026 AI-native landmark refresh DEFERRED "
                      "(30-day pull too thin to mint credibly — absence recorded, not faked).",
}

out = os.path.join(HERE, "pattern-commons.v1.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(commons, f, indent=2, ensure_ascii=False)

print("=== MERGE SUMMARY: pattern-commons v1 ===")
print(f"families: {len(families)}  (7 evolved + 3 new)")
print(f"patterns: {len(patterns)}  = {v0_retag} v0-retag + {new_total} new")
print(f"verdict tally (all): {tally}")
print(f"new ai-native patterns: {new_ai_native}")
print(f"kin (dedup) links: {kin_links}")
print(f"GATE — verdict/axis mismatches: {len(mismatches)}")
for m in mismatches: print("   ! " + m)
print(f"written: {out}")
print("\nper-family:")
for fid in ORDER:
    fp = [p for p in patterns if p["_family"]==fid]
    t = {"decoration":0,"truth-capable":0,"ai-native":0}
    for p in fp:
        if p.get("verdict") in t: t[p["verdict"]]+=1
    print(f"  {fid:13} {len(fp):2} patterns  ai-native {t['ai-native']} / truth {t['truth-capable']} / deco {t['decoration']}")
