# Done-line 0089 — The arc digest reads as a glance and only claims a gesture when one is real

Written before code, per §9.4. When this line is met, stop.

bdo opened the daily arc digest (issue #154) and named it "honestly hard to
read and make gestures about." It was: `render()` led with a paragraph-long
divergence under a "these need you" banner — over work that was a session's to
rebuild, not his — then re-dumped all nine full arc descriptions and every
atom, every day. Two failures at once: unreadable (volume) and ungesturable
(it promised a gesture that was not there).

> **Done when:** `loop/digest.py`'s `render()` is a scannable glance that
> (1) leads with **Your move** — a fold over the dataset naming only the
> unconfirmed arcs with built work waiting on his stamp, and saying "nothing"
> plainly when nothing is on him; (2) keeps the §10 divergence teeth but
> terse and ownership-marked, so a divergence whose move is a session's
> appears under Divergences and is **not** presented as bdo's gesture;
> (3) collapses each arc to one tally line (✓/○, n/total landed, plus any
> awaiting/parked/refused), expanding only live pieces and never re-dumping
> the arc prose that lives in its epic file — with the fold (`digest.digest`)
> and its §10 dataset teeth unchanged, and `tests/test_digest.py`
> `TestGestureSurface` pinning the contract (a confirmed arc harbouring a
> refused piece yields a divergence AND an empty `owner_gestures` AND a
> render that says "Your move: nothing").
