# Done-line 0005 — the owner briefing, and the inbox on the web

Written before code, per §9.4. When this line is met, stop.

> **Done when:** an atom can carry an owner **briefing** — the story told
> in layers for an owner arriving blind or distracted: headline, the value
> in the owner's terms, why-now, what each verdict concretely does, the
> cost of a wrong call, and only *then* mechanism and reading paths; the
> inbox renders it value-first both in the CLI and as a self-contained,
> phone-readable `inbox.html` (a pure fold over atoms/ + log/ — cache,
> never truth, §14.1); `loop/web.py serve` serves that page locally with
> verdict forms that clear items **through the existing pen only** (no
> second write path), bound to localhost until auth exists (named, not
> built); atoms without a briefing still render from what they have (no
> re-judging in-flight work just to re-shape it); and the amended
> owner-inbox atom (**v1**) is itself the exemplar — authored with a full
> briefing, re-judged by the real L0, waiting at bdo's stamp rendered the
> new way.

The infrastructure trajectory, made clear now so it doesn't have to be
re-decided later (bdo: "we can make sure the infrastructure is clear"):

1. **now** — `render`: a static, self-contained HTML file; works opened
   from disk, sent as an artifact, or dropped on any static host.
   `serve`: the same render live on localhost/LAN with verdict forms.
2. **next** — the same fold behind a small served endpoint; **auth before
   any bind beyond localhost** (named here, its own version).
3. **online** — same files-as-truth, same one pen; only the host changes.
   Nothing in the data layer moves.

Source: bdo's amend on atom.owner-inbox.v0 (`rcp.efd40f7169c8`), in his
words: web-based, eventually served, phone-accessible; richer metadata;
"the story is told so it explains the value, which then boils into
mechanisms after." Doctrine: §3 (pulley), D-4, D-6, I-3, I-5 (a rendered
file's version is computed from its inputs), §14.1 (cache rule). Stamp:
the amend receipt itself.

Next, not now: auth + serving beyond localhost; notification; the amend
path as a first-class flow (this session walks it by hand: v0 retired,
v1 authored, lineage kept).
