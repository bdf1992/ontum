"""Pivot's home-half CLI: build the question to ship, grade the answer home.

The benchmark cannot be played in-repo — the recoverer must be a foreign,
uncontaminated model, reached by an envoy package (bdo, chat 2026-06-10).
So this CLI does the two deterministic things that stay home:

  --status                       verify the container, show the populations
  --question <pop> [--out p]     emit the cold-play prompt — the QUESTION,
                                 truth withheld — ready to seal into an envoy
  --grade <pop> --recovery <p>   score a returned recovery against the held
                                 truth; refuses an unlawful tiling

Never calls a model. Every run ends `done | report | needs-you`.
"""
import argparse
import json
import sys

from pivot import instrument as ins


def _truth(pop):
    if pop not in ins.POPULATIONS:
        raise SystemExit("needs-you: unknown population %r (have: %s)"
                         % (pop, ", ".join(sorted(ins.POPULATIONS))))
    return ins.POPULATIONS[pop]()


def cmd_status():
    laws = ins.verify_container()
    print("Pivot instrument — container verified")
    print("  %s" % laws["graded_census"])
    print("  reference frame: 8 corner / 12 edge / 6 face / 1 center = 27")
    print("  chance kind-match (random floor reference): %.3f"
          % ins.chance_kind_match())
    print()
    print("populations (truth held home; only the question ships):")
    for name in ("random", "s-frame", "surface"):
        pop = ins.POPULATIONS[name]()
        print("  %-8s %2d occupants  (%s)"
              % (name, len(pop),
                 {"random": "floor", "s-frame": "the test object",
                  "surface": "ceiling"}[name]))
    print()
    print("done: instrument is sound; play happens off-repo (envoy pass).")


def cmd_question(pop, out):
    truth = _truth(pop)
    occupants = sorted(truth)            # alphabetical: carries no coord hint
    prompt = ins.recovery_prompt(occupants)
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(prompt + "\n")
        print("report: wrote the %s question to %s (%d occupants, truth withheld)"
              % (pop, out, len(occupants)))
    else:
        sys.stdout.write(prompt + "\n")


def cmd_grade(pop, recovery_path):
    truth = _truth(pop)
    with open(recovery_path, encoding="utf-8") as fh:
        recovery = json.load(fh)
    try:
        score = ins.grade(recovery, truth)
    except ins.RefusedToFit as exc:
        print("report: recovery REFUSED — %s" % exc)
        print("  (a locally-plausible placement that does not tile the cube; "
              "the gate noticed.)")
        return
    floor = ins.chance_kind_match()
    print("done: %s recovery graded" % pop)
    print("  kind-match  %.3f   (chance floor %.3f)"
          % (score["kind_match"], floor))
    print("  exact-match %.3f   (well-posed only once the axis is revealed)"
          % score["exact_match"])
    placed = ins.place_on_scale(score["kind_match"], floor, 1.0)
    if placed is not None:
        print("  on the noise->obvious scale: %.0f%%" % (placed * 100))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pivot.run", description=__doc__)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--question", metavar="POP")
    ap.add_argument("--out", metavar="PATH")
    ap.add_argument("--grade", metavar="POP")
    ap.add_argument("--recovery", metavar="PATH")
    args = ap.parse_args(argv)

    if args.status:
        cmd_status()
    elif args.question:
        cmd_question(args.question, args.out)
    elif args.grade:
        if not args.recovery:
            raise SystemExit("needs-you: --grade needs --recovery <path>")
        cmd_grade(args.grade, args.recovery)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
