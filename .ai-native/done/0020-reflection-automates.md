# Done-line 0020 — the reflection automates: matrix rules, and the beat that applies them

Written before code, per §9.4. When this line is met, stop.

bdo's stamp, on the record (chat, 2026-06-10): the pub/sub directive
("a pubsub with a translation matrix capable of automating the
reflection if it's configured… this skill should become a pattern
commons dedicated to using, extending, and managing that service as
application"), the session's shape answer (the log is the topic, rules
are the subscriptions, reflection records are the acks, drift is the
unconsumed backlog — level-triggered on existing beats, no broker, no
daemon), the named contract change (hooks gain their first write), and
his "Lets do it then." This done-line is that stamp executed.

> **Done when:** reflection rules are admitted records — kind ×
> surface → enabled, signed `--by`, latest wins (`python -m
> loop.reflect rule --kind owner-stamp-queue --surface github-issues
> --on --by bdo`) — and the drift an enabled rule names applies
> *itself* on the loop's beats: a `Stop` hook (the harness's
> after-each-turn beat, the repo's first writing hook — contract
> change stamped above) runs the reflector pen's `auto` verb, which
> applies drift only for enabled (kind, surface) pairs, receipts every
> auto-applied act exactly like a manual apply (signed by the auto
> beat), and is a silent no-op when nothing is enabled or nothing
> drifts; the hook never blocks and never breaks the turn (exit 0
> always, fail-open); a disabled or absent rule means no outward write
> — §10: configured-off drift must *not* reflect; manual `apply` still
> works for any registered surface, rule or no rule; and tests pin
> rule latest-wins, the disabled no-op, the enabled auto-apply, and
> the hook's fail-open exit.

One kind exists today — `owner-stamp-queue`, the only drift the fold
computes. The kinds table is the extension point: new kinds (new folds)
and new surface kinds (new translators in the pen) join as entries plus
rules, never as new systems. The skill doc becomes the pattern commons
(use / extend / manage). Next-not-now: more kinds, more surfaces, the
served web inbox (auth still named-not-built).
