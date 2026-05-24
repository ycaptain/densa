<!-- Thanks for sending a PR. Please fill in the sections below. -->

## Summary

<!-- 1–3 sentences. What does this change and why? -->

## Type of change

- [ ] Doc / typo / clarity fix
- [ ] Prompt or template edit
- [ ] Validator (`_system/densa/`) bug fix or improvement
- [ ] L1 schema change (`AGENTS.md`) — **requires prior issue discussion**
- [ ] New example L2 or example seed
- [ ] CI / tooling

## Checklist

- [ ] Ran `python -m densa --all` locally; it reports `OK: ... 0 error(s) ...`.
- [ ] For validator changes (`_system/densa/`): `pytest`, `ruff`, and `mypy` all pass.
- [ ] Wired the pre-commit hook (`git config core.hooksPath _system/hooks`) so future commits stay clean.
- [ ] Commit messages follow the `<op>(<scope>): <summary>` convention from `AGENTS.md` §9.
- [ ] No `raw/` files were edited, renamed, moved, or deleted.
- [ ] No past entries in any `log.md` were rewritten.
- [ ] If this is a breaking schema change, included a migration script under `_system/scripts/migrate_NN_<slug>.py` and bumped `schema_version` in `AGENTS.md` frontmatter.
- [ ] Updated `CHANGELOG.md` under `## [Unreleased]`.

## Related issue

<!-- Link the issue this PR addresses. For schema changes, link the
     issue where the change was discussed and approved. -->

Closes #
