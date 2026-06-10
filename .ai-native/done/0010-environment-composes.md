# Done-line 0010 — the environment composes: @-imports, not one big file

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the environment is composed, not inlined (bdo's @/@@
> directive, on the record in chat 2026-06-10: "our CLAUDE file is
> WRONG right now… module layering with @ pulling in specific sections
> of documentation… and the double @@ also so our local folder and
> global directories compose"): module environments live next to their
> modules — `loop/CLAUDE.md`, `glyphs/CLAUDE.md`, `.ai-native/CLAUDE.md`
> — formed from local definitions, to be sharpened where they live; the
> root `CLAUDE.md` becomes the thin composition surface that @-imports
> them and names the scope stack (user-global beneath, project above —
> the double-@ composition, D-9/§8); nothing load-bearing drops in the
> move (doctrine pointer, horizon, hard rules, working method stay at
> root; commands and architecture live with `loop/`; the records layout
> with `.ai-native/`); the moved docs catch up with tonight's substrate
> (summons, hooks, node prompts); and `CLAUDE.md` is finally committed —
> the config surface under the loop's eyes instead of an untracked
> orphan on one machine.

Tripwire check (§12), answered before starting: this is not
self-initiated structure-polish — the owner directed it, dated, in his
own words, after defining what @/@@ mean here. The change is config-as-
code: it alters what every future session loads, which is exactly the
kind of wording §7 says is code, so it lands as a stamped increment on
the PR like any other.
