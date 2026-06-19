# Report 0084 — Overnight Causality Sites Search

# Report: Overnight Causality Sites Search

## End-state
- Branch: codex/overnight-causality-relations in C:\Users\bdf19\ontum-wt\codex-overnight-causality-relations.
- Arc worked: epic.causality-surface.
- Landed three bounded increments: 0111 Causality Site Nodes, 0112 Causality Site Mermaid, 0113 Causality Atom Search Fold.
- Commits: 2cb66f3, 6c4a43d, edc7080.

## What changed
- term_economy now interns first-class projected SiteNodes for evidence targets; schemas and projection docs name sites explicitly; the committed projection was regenerated.
- Mermaid rendering now emits each projected SiteNode once and routes term evidence edges into shared sites.
- Added causality/atom_search.py, a read-only atom search projection over real atom records and folded lifecycle state, plus command docs.

## Validation
- python -m unittest tests.test_term_economy -v: pass (15 tests).
- python -m unittest tests.test_atom_search -v: pass (5 tests).
- python causality/atom_search.py causality welcome: pass; returns typed JSON over atom.causality-welcome-mat.v0 and atom.causality-term-economy.v0.
- python -m unittest discover -s tests -v: pass after each increment; final run 844 tests in 128.823s.

## Needs-you / boundaries
- The IDE-visible story/space causality files were not present on fresh main, so this run did not touch relation-composition/story-corpus work from another branch.
- overnight.py checkpoint reported handoff at 23:33 local because it compared against same-day 08:00; I treated that as not the intended next-morning overnight boundary and continued through bounded causality increments. This helper edge is worth fixing separately.
- The next causality step is larger: promote atom search from read-only projection into the virtual request-node/API path, without bypassing pens or owner authority.
