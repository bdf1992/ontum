#!/usr/bin/env python3
"""The relation ledger (relation-ledger.v0): the record substrate for the
relational middle band — representation *without* mechanism.

The arc's two poles are well served: deterministic code that *does* a
thing, and admitted nodes that *judge* a thing. The band between them —
"these inputs tend to predict that consequence", a relation asserted and
then *borne out or not* by what actually happened — has no home. This is
that home, at its first, deliberately humble increment: LOGGED relation
claims and observed consequence receipts. Not embeddings. The vector
organ (`model_candidate`) is declared here as a later, admitted shape and
is explicitly **out of scope** for v0 — a schema slot, not a mechanism.

The grain is the loop's: declared records (like `loop.tags`' dimension
schema) and a pure read-only fold over them (like `loop.census` /
`loop.heal`). v0 takes its records as in-memory lists — there is no log
write here, no second source of truth. Five record kinds are declared in
`SCHEMA`:

  relation_claim          asserts "inputs in bucket B predict consequence C".
  relation_probe          a question posed against a bucket (declared; the
                          active-probing organ rides a later increment).
  consequence_receipt     records an observed (action -> consequence) tie.
  model_candidate         a learned representation over a bucket (the
                          embeddings organ — DECLARED, out of scope in v0).
  bucket_coherence_report the fold's output: per bucket, did the claim's
                          predicted consequence MATCH the observed receipts?

The fold (`coherence_report`) crosses claims with receipts per bucket and
asks the one question that separates a *predictive* relation from a
*trivial* one: of the observations in this bucket, how many bore out the
claim? That ratio is the bucket's **coherence rate** — and it is the
learning-progress proxy on purpose: progress is the RATE at which buckets
*stabilize into predictive coherence* (compression), NOT raw surprise. A
bucket whose claim is borne out by a majority of its receipts reads
PREDICTIVE; one whose receipts refute it reads TRIVIAL; a claim with no
receipts yet is UNTESTED; observations under no claim are UNCLAIMED.

The §10 teeth live in the match check (`_matches`): the whole separation
of PREDICTIVE from TRIVIAL rests on comparing the *observed* consequence
to the *predicted* one. Neutralize that check — read every observation as
a match — and a refuted bucket falsely reads PREDICTIVE. The fold takes
its matcher as an injectable seam precisely so the test can substitute a
fabricated always-coherent classifier and prove the real check is what
does the work (`tests/test_relation_ledger.py`).

Read-only, propose-grain (D-4): this names what is predictive and what is
trivial; it never mints a relation or promotes a candidate. Declared even
at zero live records (the cool-valve / heal-detector grain) — the sensor
exists before the load arrives.

CLI:
  python -m loop.relation_ledger              the fold over sample records, read-only
  python -m loop.relation_ledger --records <p>  fold a JSON file: {claims, receipts}
  python -m loop.relation_ledger --json       the raw dataset (machine-readable)

Stdlib only, no network, no log write. Ends with a clear result on stdout
(D-6): done | report.
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

# --------------------------------------------------------------- the schema
# Five declared record kinds, in the grain of loop.tags' DIMENSIONS: data,
# not code paths. `fields` names each field and what it carries; `required`
# is the closed spine a record of that kind must satisfy; `gloss` is the
# one-line reading. v0 *uses* relation_claim + consequence_receipt and folds
# them into bucket_coherence_report — the other two are declared shapes the
# later increments fill (active probing, learned representations).
SCHEMA = {
    "relation_claim": {
        "gloss": "asserts that inputs in bucket B predict consequence C",
        "required": ("id", "bucket", "predicted_consequence"),
        "fields": {
            "id": "the claim's identity",
            "bucket": "the bucket of inputs the claim is about",
            "predicted_consequence": "the consequence C the claim predicts",
            "by": "who asserted it (provenance)",
        },
    },
    "relation_probe": {
        "gloss": "a question posed against a bucket — declared; the active-"
                 "probing organ rides a later increment, out of scope in v0",
        "required": ("id", "bucket", "question"),
        "fields": {
            "id": "the probe's identity",
            "bucket": "the bucket being probed",
            "question": "what is being asked of the relation",
        },
    },
    "consequence_receipt": {
        "gloss": "records an observed (action -> consequence) tie",
        "required": ("id", "bucket", "observed_consequence"),
        "fields": {
            "id": "the receipt's identity",
            "bucket": "the bucket the action's inputs fell in",
            "action": "what was done (optional, for the cold reader)",
            "observed_consequence": "the consequence that actually followed",
        },
    },
    "model_candidate": {
        "gloss": "a learned representation over a bucket — the embeddings "
                 "organ; DECLARED here, explicitly out of scope for v0",
        "required": ("id", "bucket", "representation"),
        "fields": {
            "id": "the candidate's identity",
            "bucket": "the bucket it represents",
            "representation": "the learned form (a LATER admitted organ)",
        },
    },
    "bucket_coherence_report": {
        "gloss": "the fold's output: per bucket, did the claim's predicted "
                 "consequence match the observed receipts, and at what rate",
        "required": ("bucket", "verdict", "coherence_rate"),
        "fields": {
            "bucket": "the bucket reported on",
            "claim_id": "the claim folded (None when UNCLAIMED)",
            "predicted": "the predicted consequence (None when UNCLAIMED)",
            "observations": "how many receipts fell in this bucket",
            "borne_out": "how many of them matched the prediction",
            "coherence_rate": "borne_out / observations — the learning-progress proxy",
            "verdict": "PREDICTIVE | TRIVIAL | UNTESTED | UNCLAIMED",
        },
    },
}

# The verdicts a bucket can read. PREDICTIVE / TRIVIAL are the live split;
# UNTESTED / UNCLAIMED are the honest absences (a claim with no receipts, or
# receipts with no claim) — named, never guessed past.
PREDICTIVE = "PREDICTIVE"
TRIVIAL = "TRIVIAL"
UNTESTED = "UNTESTED"
UNCLAIMED = "UNCLAIMED"

# A bucket is predictive when a MAJORITY of its observations bear out the
# claim. The bar is the discriminator, not decoration: at 0.5 a coin-flip
# relation (half borne out) is TRIVIAL, as it must be — a relation that holds
# no better than chance compresses nothing.
COHERENCE_BAR = 0.5


def _matches(observed, predicted):
    """The load-bearing check (§10): does an observed consequence bear out the
    predicted one? Exact equality on the consequence token. This single
    comparison is what separates a predictive bucket from a refuted one —
    neutralize it (always True) and every refuted bucket falsely reads
    PREDICTIVE, which `tests/test_relation_ledger.py` proves by substituting a
    fabricated matcher through the `match` seam of `coherence_report`."""
    return observed == predicted


def validate_record(kind, rec):
    """The schema door: a record must name a declared kind and carry that
    kind's required fields. Returns the list of complaints (empty == clean) —
    a finding names its own check, never prose."""
    spec = SCHEMA.get(kind)
    if spec is None:
        return [f"unknown record kind {kind!r} (not in SCHEMA)"]
    missing = [f for f in spec["required"] if f not in rec]
    return [f"{kind} missing required field {f!r}" for f in missing]


def coherence_report(claims, receipts, match=_matches):
    """The pure read-only fold: cross relation_claims with consequence_receipts
    per bucket and report coherence. `match` is the injectable comparison seam
    (default `_matches`) so the §10 test can prove it is non-vacuous.

    Returns the dataset render()/--json speak: per-bucket rows that conform to
    the bucket_coherence_report schema, the verdict counts, and the
    system-level predictive fraction (the compression-progress proxy over all
    tested, claimed buckets)."""
    claim_by_bucket = {}
    for c in claims:
        claim_by_bucket[c["bucket"]] = c
    receipts_by_bucket = defaultdict(list)
    for r in receipts:
        receipts_by_bucket[r["bucket"]].append(r)

    rows = []
    for bucket in sorted(set(claim_by_bucket) | set(receipts_by_bucket)):
        claim = claim_by_bucket.get(bucket)
        recs = receipts_by_bucket.get(bucket, [])
        observations = len(recs)
        if claim is None:
            # observations under no claim: nothing to bear out — UNCLAIMED.
            rows.append({
                "bucket": bucket, "claim_id": None, "predicted": None,
                "observations": observations, "borne_out": 0,
                "coherence_rate": 0.0, "verdict": UNCLAIMED,
            })
            continue
        predicted = claim["predicted_consequence"]
        borne_out = sum(1 for r in recs
                        if match(r.get("observed_consequence"), predicted))
        rate = (borne_out / observations) if observations else 0.0
        if observations == 0:
            verdict = UNTESTED          # a claim, no receipts to test it yet
        elif rate > COHERENCE_BAR:
            verdict = PREDICTIVE        # the claim is borne out — compression
        else:
            verdict = TRIVIAL           # the claim is refuted / no better than chance
        rows.append({
            "bucket": bucket, "claim_id": claim["id"], "predicted": predicted,
            "observations": observations, "borne_out": borne_out,
            "coherence_rate": round(rate, 4), "verdict": verdict,
        })

    counts = dict(Counter(r["verdict"] for r in rows))
    tested = counts.get(PREDICTIVE, 0) + counts.get(TRIVIAL, 0)
    predictive_fraction = round(counts.get(PREDICTIVE, 0) / tested, 4) if tested else 0.0
    return {
        "buckets": rows,
        "counts": counts,
        "predictive_fraction": predictive_fraction,
        "scanned": {"claims": len(claims), "receipts": len(receipts)},
    }


# ---------------------------------------------------------------- sample data
# v0 has no log records; the organ is declared anyway (the cool-valve grain).
# This sample is what the CLI folds when none is supplied — one bucket whose
# claim is borne out (PREDICTIVE) and one whose receipts refute it (TRIVIAL),
# so a cold reader sees the split the fold draws.
SAMPLE_CLAIMS = [
    {"id": "claim.warm-expands", "bucket": "warm",
     "predicted_consequence": "expands", "by": "sample"},
    {"id": "claim.coin-heads", "bucket": "coin",
     "predicted_consequence": "heads", "by": "sample"},
]
SAMPLE_RECEIPTS = [
    {"id": "rcp.w1", "bucket": "warm", "action": "heat", "observed_consequence": "expands"},
    {"id": "rcp.w2", "bucket": "warm", "action": "heat", "observed_consequence": "expands"},
    {"id": "rcp.w3", "bucket": "warm", "action": "heat", "observed_consequence": "contracts"},
    {"id": "rcp.c1", "bucket": "coin", "action": "flip", "observed_consequence": "heads"},
    {"id": "rcp.c2", "bucket": "coin", "action": "flip", "observed_consequence": "tails"},
]


def _load_records(path):
    """Read a {claims, receipts} JSON file, validating each record against its
    declared schema. A bad record is refused with its own complaint (D-6)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    claims = data.get("claims", [])
    receipts = data.get("receipts", [])
    complaints = []
    for c in claims:
        complaints += validate_record("relation_claim", c)
    for r in receipts:
        complaints += validate_record("consequence_receipt", r)
    return claims, receipts, complaints


def render(d):
    lines = ["# Relation ledger — bucket coherence", "",
             "_relation claims crossed with consequence receipts: which "
             "buckets predict, which are trivial. Read-only; the relations "
             "stay proposed (D-4)._", ""]
    s = d["scanned"]
    lines.append(f"Folded {s['claims']} claim(s) and {s['receipts']} receipt(s).")
    lines.append("")
    if not d["buckets"]:
        lines.append("No records — the organ is declared and idle (the "
                     "cool-valve grain). Hand it claims and receipts to fold.")
        return "\n".join(lines)
    order = {PREDICTIVE: 0, TRIVIAL: 1, UNTESTED: 2, UNCLAIMED: 3}
    for row in sorted(d["buckets"], key=lambda r: (order.get(r["verdict"], 9), r["bucket"])):
        head = f"- `{row['bucket']}` — {row['verdict']}"
        if row["claim_id"] is not None:
            head += (f" (claim {row['claim_id']} predicts {row['predicted']!r}; "
                     f"{row['borne_out']}/{row['observations']} borne out, "
                     f"coherence {row['coherence_rate']})")
        else:
            head += f" ({row['observations']} observation(s), no claim)"
        lines.append(head)
    lines.append("")
    lines.append(f"Predictive fraction (learning-progress proxy): "
                 f"{d['predictive_fraction']} of tested, claimed buckets.")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--records", type=Path, default=None,
                    help="a JSON file {claims, receipts} to fold (default: sample)")
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    args = ap.parse_args(argv)

    complaints = []
    if args.records is not None:
        claims, receipts, complaints = _load_records(args.records)
    else:
        claims, receipts = SAMPLE_CLAIMS, SAMPLE_RECEIPTS

    if complaints:
        for c in complaints:
            print(f"  refused: {c}", file=sys.stderr)
        print(f"result: needs-you — {len(complaints)} record(s) refused at the "
              f"schema door; fix them and re-fold")
        return 1

    d = coherence_report(claims, receipts)
    if args.json:
        print(json.dumps(d, indent=2, sort_keys=True))
    else:
        print(render(d))
        print()

    trivial = d["counts"].get(TRIVIAL, 0)
    if trivial:
        print(f"result: report — {trivial} bucket(s) read TRIVIAL (a claim its "
              f"receipts refute); predictive fraction {d['predictive_fraction']}. "
              f"The relations stay yours to mint (D-4).")
    else:
        n = len(d["buckets"])
        print(f"result: done — {n} bucket(s) folded; no claim is refuted by its "
              f"receipts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
