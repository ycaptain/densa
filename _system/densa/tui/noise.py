"""Known-noise classification for diagnostics.

The full-repo validator (`densa --all`) surfaces a large, *expected*
band of findings that originate in gitignored, example-bearing trees:
the local maintainer tracker under ``docs/maintainers/`` and the
Backlog task store under ``.backlog/`` both contain ``[[wikilink]]``
examples and prose that legitimately trip rules like wikilink
resolvability. As of 2026-06-15 that band is ~104 findings.

The viewer mutes this band *by path origin* rather than by rule ID:
the noise is a property of *where the file lives*, not of which rule
fired, so a prefix test is both simpler and more robust than pinning a
rule number that may renumber. The muted count stays visible in the
status bar so the band is legible-as-a-number without drowning the
real findings.
"""

from __future__ import annotations

# Repo-relative, forward-slash prefixes whose findings are expected
# noise. Kept as a module constant (no filesystem walk) so the
# predicate is pure and total.
NOISE_PREFIXES: tuple[str, ...] = (
    "docs/maintainers/",
    ".backlog/",
)


def is_known_noise(path: str) -> bool:
    """Return ``True`` iff *path* originates in a known-noise tree.

    *path* is a repo-relative, forward-slash string (the form
    :attr:`densa.report.Diagnostic.path` already guarantees). Pure and
    total: no I/O, never raises.
    """
    return any(path.startswith(prefix) for prefix in NOISE_PREFIXES)
