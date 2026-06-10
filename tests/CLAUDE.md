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
