"""Templates must conform to the L1 frontmatter contract.

Every file under ``_system/templates/*.md`` is the seed for a future
wiki page; if the template ships without a universal-required field,
Templater-created pages start life violating L1 §3. This suite is
the mechanical gate that keeps that from happening — when adding a
new template, the gate fires once and the contributor adds the
missing fields before merge.

Uses :func:`densa.frontmatter.parse_stdlib` rather than pyyaml so
the test does not pull in optional dependencies; the stdlib backend
handles the YAML subset we ship in templates.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from densa.frontmatter import parse_stdlib

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"

# Mirrors AGENTS.md §3 universal frontmatter (minus `sources`, which
# does not apply to `fleeting` etc. and is enforced by AGENTS005 only
# where the L1 §3.1 table requires it).
REQUIRED_UNIVERSAL: frozenset[str] = frozenset({
    "type",
    "domain",
    "created",
    "updated",
    "aliases",
    "tags",
    "status",
    "compiled_against",
})

# AGENTS.md §3.3 — these `type` values MUST also carry `last_validated`.
REQUIRES_LAST_VALIDATED: frozenset[str] = frozenset({
    "concept",
    "framework",
    "protocol",
    "entity",
})


def _all_templates() -> list[Path]:
    return sorted(TEMPLATES_DIR.glob("*.md"))


@pytest.mark.parametrize(
    "template",
    _all_templates(),
    ids=lambda p: p.name,
)
def test_universal_frontmatter(template: Path) -> None:
    fm = parse_stdlib(template.read_text(encoding="utf-8"))
    assert fm is not None, f"{template.name}: no frontmatter block"
    missing = REQUIRED_UNIVERSAL - fm.keys()
    assert not missing, (
        f"{template.name}: missing universal keys {sorted(missing)} "
        f"(see AGENTS.md §3)"
    )


@pytest.mark.parametrize(
    "template",
    _all_templates(),
    ids=lambda p: p.name,
)
def test_last_validated_where_required(template: Path) -> None:
    fm = parse_stdlib(template.read_text(encoding="utf-8"))
    assert fm is not None, f"{template.name}: no frontmatter block"
    page_type = fm.get("type")
    if page_type in REQUIRES_LAST_VALIDATED:
        assert "last_validated" in fm, (
            f"{template.name} (type={page_type}): missing `last_validated` "
            f"(see AGENTS.md §3.3)"
        )


@pytest.mark.parametrize(
    "template",
    _all_templates(),
    ids=lambda p: p.name,
)
def test_domain_is_placeholder_or_psychology_l2_specific(
    template: Path,
) -> None:
    """Generic templates ship with `domain: <your-domain>` so adopters
    customise; only L2-specific templates (`psychology-*`) may hard-code
    a domain.
    """
    fm = parse_stdlib(template.read_text(encoding="utf-8"))
    assert fm is not None
    domain = fm.get("domain", "")
    name = template.name
    if name.startswith(("psychology-", "psychiatry-")):
        assert domain == "psychology", (
            f"{name}: L2-specific template should declare `domain: psychology`"
        )
    elif name.startswith("writing-"):
        # writing/ is an opt-in workspace outside the L2 schema (see
        # DESIGN.md §"Optional layers"); its templates hard-code
        # `domain: writing` for symmetry, but the tree is excluded from
        # AGENTS003/006 enforcement via WIKILINK_SKIP_TOP_LEVEL.
        assert domain == "writing", (
            f"{name}: writing-* template should declare `domain: writing`"
        )
    else:
        assert domain.startswith("<") and domain.endswith(">"), (
            f"{name}: generic template must use a placeholder domain "
            f"(got {domain!r}); only psychology-*/psychiatry-*/writing-* "
            f"templates may hard-code a domain"
        )
