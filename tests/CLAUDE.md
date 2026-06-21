# tests/ — the receipts for the code

Run from the repo root: `python -m unittest discover -s tests -v`.
Stdlib `unittest` only — no runners, no fixtures beyond `tempfile`.

Conventions the suite already holds:

- Every test module states which done-line it pins in its docstring;
  a test that pins nothing is polish (§12).
- Temp-root scaffolding: build a throwaway `.ai-native` root
  (`make_root`), admit setpoints/realness with `by="test-bdo"`, drive
  with `orchestrate`/`reconcile`, assert over the log files
  themselves — never over in-memory state (D-5).
- Hooks and guards are tested as subprocesses with JSON on stdin and
  `ONTUM_*` env overrides — the contract is exit codes and streams,
  not internals.
- Byte-determinism is asserted as bytes (`read_bytes`), not text.
- The §10 bar: prefer a test where a locally-fine artifact *refuses to
  fit* over one that confirms the happy path.

These conventions are no longer prose-only: `python -m loop.suite census`
(done-line 0171) is the read-only fold that measures them — it types each
test (guard / refusal / fold / …), names which organ and done-line it
attributes to, and surfaces the gaps (an untyped test, a done-line no test
pins, a refusal-named test that asserts no rejection). It is the loop
sensing its test body, the `census.py` of the suite; the planned
test-operator / test-administrator seats run mutation and change-scope
assays on top of its attribution map.
