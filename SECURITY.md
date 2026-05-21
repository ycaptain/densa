# Security Policy

## Scope

This project is a **template** for personal LLM-maintained knowledge
bases. It does not run a service and stores no user data of its own.
However, vaults built from this template routinely hold material that
is highly sensitive — therapy transcripts, medical notes, NDA-bound
meeting records, private journals. The guidance below treats *your
vault* as the primary asset to protect.

## Reporting a vulnerability

Please report any of the following privately via
[GitHub Security Advisories](https://github.com/ycaptain/llm-wiki-starter/security/advisories/new):

- A bypass in `_system/wikilint/` that allows red-line violations
  (e.g. silent `raw/` mutation, log history rewrite, `analysis.sources`
  cardinality breach) to slip through pre-commit or CI.
- A schema ambiguity an adversarial LLM run could exploit to exfiltrate
  or corrupt vault content while appearing to follow the contract.
- A prompt-injection pattern in a `raw/` file (or any source you might
  reasonably ingest — clipped articles, transcripts, screenshots) that
  causes the LLM to perform writes outside the operation's declared
  scope, skip the plan-then-confirm gate, or coerce a red-line bypass
  via natural-language instructions.
- A bug in `setup_encryption.sh` or the git-crypt integration that
  could result in unencrypted raw files being pushed to a remote.

Please do **not** open a public issue for these. We aim to acknowledge
within 7 days.

For non-security bugs (rendering glitches, prompt clarity, etc.) use a
normal [bug report issue](.github/ISSUE_TEMPLATE/bug_report.md).

## Hardening checklist for your vault

If you instantiate this template for sensitive material:

- [ ] Wire the pre-commit hook: `git config core.hooksPath _system/hooks`.
- [ ] Configure encryption for any sensitive L2 before the first push:
      see [`_system/SETUP.md`](_system/SETUP.md) §"Privacy: encrypt
      sensitive raw/ with git-crypt".
- [ ] Verify encryption is active: `git-crypt status -e` should list
      every path you intended to encrypt.
- [ ] Use a **second cold-backup remote** on a different provider
      (Codeberg, GitLab, or a self-hosted forge). Single-vendor account
      loss is the most common way personal vaults disappear.
- [ ] Store your GPG private key on a hardware token (YubiKey, Nitrokey)
      or in a vetted secrets manager. Loss of the key = loss of encrypted
      history. Never commit `.git-crypt/keys/default`.
- [ ] Treat the LLM agent's web access as adversarial: per L1 §6, no
      silent web fetches during ingest. Review every prompt-driven
      enrichment before it lands in the wiki.
- [ ] **Treat `raw/` content as untrusted input to the LLM.** A clipped
      article, an ASR-transcribed call, or a web-clip can contain
      adversarial instructions targeting the agent ("ignore previous
      instructions and write ..."). The plan-then-confirm gate (every
      operation drafts a plan you approve before writes) is your
      primary defence — never approve a plan without reading the
      *targets* of every write, not just the summary.
- [ ] If you push to a public remote, audit `.gitattributes` and
      `.gitignore` against accidentally exposing `inbox/` or `raw/`
      paths that weren't yet routed. `inbox/` is especially risky as
      a staging area — consider `.gitignore`ing `inbox/*.md` and
      treating the inbox as never-committed scratch space.
- [ ] Before the first push to any remote, scan for accidentally
      committed secrets: `gitleaks detect --no-banner --staged` or
      `trufflehog filesystem .` are stdlib-free baselines. Encrypted
      blobs are still readable to anyone with the git-crypt key.
- [ ] Be aware of LLM-agent vendor surface: prompts, raw contents,
      and partial wiki contents may be logged or used for evaluation
      by the LLM vendor depending on your plan and settings. Check
      your Cursor / Claude Code / Codex / other-vendor data-handling
      policy before ingesting clinically sensitive or NDA-bound
      material.

## Supply-chain notes

The validator (`_system/wikilint/`) is pure Python with no runtime
third-party dependencies — it imports only the standard library. The
pre-commit hook invokes the same package via `python -m wikilint`.
Both are short enough (~1k lines including the rule registry) to read
end-to-end before trusting in a security-sensitive vault.
