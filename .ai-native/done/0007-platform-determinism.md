# Done-line 0007 — platform determinism: the bytes are the truth on every OS

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the test suite passes on Windows — the kill test proves
> the same un-catchable-kill property with a cross-platform hard kill —
> and the working tree's atom bytes re-match their announced `sha256`
> hashes so the orphaned pipeline history reconnects with no
> retro-invalidation (D-5): `atom.epic-layer.v0` re-surfaces in the owner
> inbox awaiting bdo's stamp; and the guard is infra-as-code —
> `.gitattributes` pins LF for source, exempts `.ai-native/` identity
> bytes from eol conversion entirely, and union-merges the append-only
> logs — so no future checkout on any platform can orphan history again.

Context, on the record: discovered 2026-06-10 on bdo's Windows machine.
`core.autocrlf=true` rewrote every atom to CRLF at checkout; identity is
the content hash, so the fold read every atom as unborn, `--status`
showed an empty field, and the inbox hid an item that was waiting on the
owner. The fix restores the stored LF bytes (the announced identity)
rather than re-announcing under new hashes — history reconnects; nothing
is erased or superseded.
