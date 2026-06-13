# Done-line 0064 — the Whiteout pen: a marked, recoverable correction that refuses what's been consumed

Written before code, per §9.4. When this line is met, stop.

Whiteout is correction fluid for the substrate. It LEAVES A MARK (the
correction is a visible superseding append), you can STILL SEE UNDER IT
(the original is never destroyed — the log is append-only, so you fold
without the correction to recover it), and it does NOT work on HUGE
mistakes (once downstream has *consumed* the old value, a whiteout would
lie about a past that already propagated — that needs a retro, not
correction fluid). It is the generalization of `supersede-done` into a
bounded, marked, general correction. The teeth (§10): a correction that
works on anything is erasure with extra steps; the refusal is what keeps
it honest.

> **Done when:** the records pen gains a `whiteout` mode that corrects a
> prior record by appending a MARKED correction — the original is never
> erased (it stays on the append-only log and is foldable underneath, so
> the supersession chain reads *now / what it covered / why*), and the
> fold honours the correction as the default view; the mode REFUSES a
> "HUGE" correction by a computable **consumption test** — the target is
> un-whiteoutable once anything downstream has consumed it (a later log
> record cites its id or hash, or it is terminal/landed-to-main), and the
> refusal NAMES the escalation (a retro, or bdo's hand) instead of
> overwriting a past that already propagated; and softening a frozen
> done-line's bar stays bdo's `supersede` gesture, never a session's
> whiteout (no free stop-card). Proven by test (the §10 teeth): a small,
> unconsumed mistake is corrected and the original stays readable under
> the mark; a consumed correction refuses to fit and says where it must
> go instead.
