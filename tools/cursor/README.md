# Cursor

> [⬅ Back to repo root](../../README.md) · [Workflow rules (AGENTS.md)](../../AGENTS.md) · [Tool-agnostic AI prompts](../../ai-prompts/README.md)

Notes and reusable assets for the [Cursor IDE](https://cursor.com).

## Contents

| File / folder | Purpose |
|---|---|
| [`rules-setup-guide.md`](rules-setup-guide.md) | Complete walkthrough — what Cursor Rules are, how to create global vs project rules, file structure, naming conventions, and 7 ready-to-use rules with explanation. |
| [`rules/`](rules/) | Cursor-specific `.mdc` rule files. Drop any of them into `~/.cursor/rules/` (global) or `<your-project>/.cursor/rules/` (project) and reload Cursor. |

> The **Google Docs HTML formatting** rule is universal (works in Cursor, Claude Code, ChatGPT, etc.) and lives in [`../../ai-prompts/google-docs-html-formatting/`](../../ai-prompts/google-docs-html-formatting/). The Cursor wrapper is at [`../../ai-prompts/google-docs-html-formatting/wrappers/cursor.mdc`](../../ai-prompts/google-docs-html-formatting/wrappers/cursor.mdc).

## Quick install — all Cursor-specific rules at once (global)

```bash
mkdir -p ~/.cursor/rules
cp tools/cursor/rules/*.mdc ~/.cursor/rules/
# Then in Cursor: Cmd+Shift+P → Reload Window
```

## Quick install — single rule

```bash
cp tools/cursor/rules/git-commit-format.mdc ~/.cursor/rules/
```

## Available Cursor-specific rules

| Rule | What it does | When it triggers |
|---|---|---|
| `git-commit-format.mdc` | Enforce Conventional Commits message style | On request — when writing commit messages |
| `no-cursor-trailer.mdc` | Hard ban on `Co-authored-by: Cursor` — three-layer auto protection (global git template + Cursor hook + rule) | Always on (every session) |
| `devops-kubernetes.mdc` | YAML/Helm/Kubernetes conventions | Auto-loads on `*.yaml` / `*.yml` files |
| `shell-scripting.mdc` | Bash best practices (`set -euo pipefail`, error handling, etc.) | Auto-loads on `*.sh` files |
| `docker-best-practices.mdc` | Dockerfile + Compose best practices | Auto-loads on `Dockerfile*` / `docker-compose*.yml` |
| `security-hygiene.mdc` | Universal "never commit secrets" rules | Always on (every session) |
| `gcp-cli-hygiene.mdc` | gcloud / GCP resource conventions | Auto-loads on `*.sh` / `*.yaml` files |

See [`rules-setup-guide.md`](rules-setup-guide.md) for the full explanation of each rule, including how to write your own.

## Related

- [Google Docs HTML formatting](../../ai-prompts/google-docs-html-formatting/) — universal AI prompt (also has a Cursor wrapper)
- [All tool-agnostic AI prompts](../../ai-prompts/README.md)
- [Workflow rules — AGENTS.md](../../AGENTS.md) at repo root
