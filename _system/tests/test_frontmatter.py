"""Test the stdlib frontmatter parser.

We do not test the pyyaml path here (when available, it's tested by
the upstream pyyaml; we only test our wrapper logic in a separate
suite if needed).
"""

from __future__ import annotations

from wikilint.frontmatter import parse_stdlib


def test_returns_none_without_delimiter() -> None:
    assert parse_stdlib("# no frontmatter\n") is None


def test_parses_simple_scalars() -> None:
    fm = parse_stdlib(
        "---\n"
        "type: concept\n"
        "domain: psychology\n"
        "status: active\n"
        "---\n"
        "body\n"
    )
    assert fm == {
        "type": "concept",
        "domain": "psychology",
        "status": "active",
    }


def test_parses_quoted_scalars() -> None:
    fm = parse_stdlib(
        "---\n"
        'title: "Hello, world"\n'
        "---\n"
    )
    assert fm == {"title": "Hello, world"}


def test_parses_inline_list() -> None:
    fm = parse_stdlib(
        "---\n"
        "sources: [\"[[a]]\", \"[[b]]\"]\n"
        "tags: [foo, bar, baz]\n"
        "---\n"
    )
    assert fm == {
        "sources": ["[[a]]", "[[b]]"],
        "tags": ["foo", "bar", "baz"],
    }


def test_parses_block_list() -> None:
    fm = parse_stdlib(
        "---\n"
        "sources:\n"
        "  - \"[[a]]\"\n"
        "  - \"[[b]]\"\n"
        "---\n"
    )
    assert fm == {"sources": ["[[a]]", "[[b]]"]}


def test_empty_block() -> None:
    assert parse_stdlib("---\n---\n") == {}


def test_skips_comments_and_blank_lines() -> None:
    fm = parse_stdlib(
        "---\n"
        "# this is a comment\n"
        "\n"
        "type: concept\n"
        "---\n"
    )
    assert fm == {"type": "concept"}


def test_does_not_choke_on_commas_inside_quotes() -> None:
    fm = parse_stdlib(
        "---\n"
        'aliases: ["foo, bar", baz]\n'
        "---\n"
    )
    assert fm == {"aliases": ["foo, bar", "baz"]}
