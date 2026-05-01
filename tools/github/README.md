# GitHub

> Setup guides for GitHub-specific tooling — Apps, Actions, branch protection, org-wide automation patterns.

[Back to repo root](../../README.md) · [`tools/`](../README.md) · [`tools/cursor/`](../cursor/) · [Repo conventions](../../AGENTS.md)

---

## Notes

| Note | What you'll set up | Audience | Status |
| --- | --- | --- | --- |
| [Org-owned GitHub App for CI/CD — setup & migration](org-github-app-for-cicd-setup-guide.md) | Replace personal PATs / "service-user accounts" with an **org-owned GitHub App** that mints short-lived installation tokens. Includes the migration playbook for centralized reusable workflows + bulk update of downstream app repos. | Platform / DevOps engineers, GitHub org admins | stable |

*More GitHub notes (branch protection rulesets, Actions runners, OIDC federation, gh CLI snippets) will be added here as they are published.*

---

## Conventions

- Org names → `<your-org>`
- Repo names → `<your-repo>` or `<centralized-workflows-repo>` / `<example-app>` when referring to a specific role
- Secret names: keep the convention used in real workflows (`CICD_APP_ID`, `CICD_APP_PRIVATE_KEY`) — these are names, not values, so they're safe to use literally
- Branch names: `dev`, `main`, `master`, `release`, `v3`, `v4`, `feature/...` — the names themselves are not sensitive
- PR description / image URLs → `<your-public-image-url>`

See [`../README.md`](../README.md) and [`AGENTS.md`](../../AGENTS.md) for the full conventions.
