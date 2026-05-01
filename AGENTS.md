# AGENTS.md — Workflow for Adding New Notes

> **Read this file every time before adding or pushing content to this repo.**
> It works as a checklist for both humans and AI agents (Cursor, Claude Code, etc.).
> If you follow every step here, the repo stays clean, secure, and discoverable.

---

## TL;DR (the 7-step flow)

1. Decide the right **folder** for your note (see [Folder map](#folder-map))
2. Pick a **filename** following the [naming rules](#naming-rules)
3. Write the note using the [note template](#note-template)
4. **Sanitize** all real values → use `<placeholders>` (see [Sanitization rules](#sanitization-rules))
5. Run the [secret scan](#secret-scan) before staging
6. Update the **index** in `README.md`
7. Commit with the [commit format](#commit-message-format) and push

---

## Folder map

If your note doesn't fit, **create a new folder** (and add it to README's structure section).

| Folder | What goes here | Examples |
|---|---|---|
| `ai-prompts/` | **Tool-agnostic** AI prompts / system instructions that work in multiple AI tools (Cursor, Claude Code, ChatGPT, Gemini, etc.). Each prompt has a universal `prompt.md` plus per-tool wrappers in `wrappers/`. | google-docs-html-formatting, code-review-checklist, commit-message-style |
| `linux/` | Distro-level installs, services, system config, desktops, CLI tooling on Linux | XFCE-on-Ubuntu, systemd timers, fail2ban setup |
| `cloud/gcp/` | GCP-specific guides | GKE setup, Cloud Run deploy, IAM patterns |
| `cloud/aws/` | AWS-specific guides | EKS setup, EC2 patterns, IAM roles |
| `cloud/azure/` | Azure-specific guides | AKS setup, AAD setup |
| `kubernetes/` | k8s-cluster-agnostic | Helm patterns, operators, RBAC, troubleshooting |
| `docker/` | Docker / containerd / image building | multi-stage Dockerfile, buildx, registry setup |
| `networking/` | VPN, DNS, firewalls, LBs, proxies | nginx reverse proxy, WireGuard, Cloudflare tunnel |
| `tools/` | CLI tools, IDEs, dev environment setups | Claude Code, gcloud, terraform, kubectl plugins |
| `databases/` | Postgres, MySQL, MongoDB, Redis, etc. | Postgres tuning, MySQL backup automation |
| `monitoring/` | Grafana, Prometheus, Loki, Datadog | Grafana healthcheck, Prometheus federation |
| `security/` | Audits, hardening, certs, secrets management | Vault setup, TLS cert renewal, audit logging |
| `ci-cd/` | GitHub Actions, GitLab CI, ArgoCD, Jenkins | reusable workflows, OIDC to cloud |
| `snippets/` | One-off shell scripts, aliases, dotfile chunks | useful one-liners, `.zshrc` excerpts |

> **Rule:** empty folders aren't tracked in git. Create the folder only when you have content for it.

---

## Naming rules

For both folders and files:

- **lowercase** only
- **kebab-case** (words separated by `-`)
- **descriptive** — filename alone (with its folder context) tells the reader what's inside
- end with `.md` for guides
- no spaces, no underscores, no `MyGuide.MD`
- **don't repeat the folder name in the filename** — context is implied by the folder
  - `tools/cursor/rules-setup-guide.md` ✅ (folder gives "cursor")
  - `tools/cursor/cursor-rules-setup-guide.md` ❌ (redundant prefix)

| Good | Bad |
|---|---|
| `linux/ubuntu-vm-xfce-rdp-setup-guide.md` | `linux/linux-ubuntu-vm-xfce-rdp.md` |
| `tools/cursor/rules-setup-guide.md` | `tools/cursor/cursor-rules.md` |
| `cloud/gcp/gke-private-cluster-with-shared-vpc.md` | `cloud/gcp/gcp-gke-cluster.md` |
| `nginx-reverse-proxy-with-cert-renewal.md` | `nginx notes.md` |
| `postgres-pgbouncer-tuning.md` | `pgbouncer.MD` |

---

## Note template

Copy this into your new file as a starting point:

````markdown
# <Title — what the reader will accomplish>

> One-line summary of the goal and target environment.

| Item | Value |
|---|---|
| OS / target | e.g. Ubuntu 24.04 |
| Tested on | e.g. AWS EC2 t3.medium, May 2026 |
| Time to complete | ~30 min |
| Difficulty | beginner / intermediate / advanced |

---

## Why this exists

2–3 sentences on the problem this guide solves.

---

## Prerequisites

- bullet list of what the reader needs (tools, access, credentials)

---

## Steps

### Step 1 — <action>

```bash
# command(s)
```

What just happened (1–2 lines).

### Step 2 — <action>

...

---

## Verification

How to confirm everything worked (commands or expected output).

---

## Troubleshooting

| Issue | Fix |
|---|---|
| ... | ... |

---

_Tested: <YYYY-MM-DD>_
````

---

## Sanitization rules

**Before committing, replace ALL of these with placeholders:**

| Real value (NEVER commit) | Use this placeholder instead |
|---|---|
| Real IP addresses (public OR internal) | `<vm-public-ip>`, `<server-ip>`, `<your-ip>` |
| Hostnames / instance names | `<vm-name>`, `<host>`, `<server-name>` |
| Cloud project IDs | `<gcp-project-id>`, `<aws-account-id>`, `<azure-subscription-id>` |
| Region / zone | `<region>`, `<zone>` |
| Real usernames (your colleagues, customers) | `<username>`, `<your-username>` |
| Email addresses | `<your-email>`, `user@example.com` |
| Domain names you own/control | `example.com`, `<your-domain>` |
| API keys, tokens, passwords | `<api-key>`, `<token>`, `<password>` (and **rotate the real one**) |
| SSH private keys (any portion) | `<path-to-private-key>` |
| Bucket / DB / queue names that are private | `<bucket-name>`, `<db-name>` |
| Slack / Teams webhooks | `<slack-webhook-url>` |
| Customer / employer names | rewrite generically ("the team", "the org") |

**Allowed real values (these are fine):**

- Public package names: `xrdp`, `ubuntu-desktop`, `kubectl`
- Public URLs: `https://apt.kubernetes.io`, `https://claude.ai/install.sh`
- Public IP ranges that are documented (e.g. GCP IAP CIDR `35.235.240.0/20`)
- Open-source licenses, version numbers
- Vendor product names: `GCP`, `AWS`, `XFCE`, `Claude Code`

---

## Secret scan

Run this **before every commit** in the repo root:

```bash
rg -i 'password\s*[:=]|api[-_]?key|secret[-_]?key|token\s*[:=]|sk-[a-z0-9]{20}|ghp_[A-Za-z0-9]{20}|aws_secret|BEGIN.*PRIVATE KEY|[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' \
  --glob '!*.gitignore' --glob '!AGENTS.md'
```

If any matches show up that aren't placeholders, **fix them before committing.**

For a heavier scan, install [`gitleaks`](https://github.com/gitleaks/gitleaks):

```bash
brew install gitleaks
gitleaks detect --no-git -v
```

---

## Update the README index

When you add a new guide, **append a link to the index in `README.md`** under the matching folder section.

Example — after adding `linux/postgres-on-ubuntu-setup.md`:

```diff
 ### Linux

 - [Setting up GUI mode in Ubuntu Linux 26.04 through CLI](linux/ubuntu-vm-xfce-rdp-setup-guide.md) — install XFCE desktop on a headless Ubuntu VM and access it over RDP.
+- [Installing PostgreSQL 16 on Ubuntu 24.04](linux/postgres-on-ubuntu-setup.md) — production-ready Postgres install with hardening and backup setup.
```

If you create a new top-level folder, also add it to the **Repository structure** section in `README.md`.

---

## Update `.gitignore` if needed

If your guide produces or references files you don't want committed (e.g. local test outputs, generated configs, scratch dirs), add them to `.gitignore` at the repo root:

```bash
echo 'scratch/' >> .gitignore
echo '*.local.yaml' >> .gitignore
```

---

## Commit message format

Use **Conventional Commits**:

```
<type>: <short summary in imperative mood>

<optional body — what and why, not how>
```

Types:

| Type | Use for |
|---|---|
| `docs` | Most additions/edits to notes |
| `feat` | New folder or major restructure |
| `fix` | Correcting a bug or wrong command in an existing guide |
| `chore` | Repo maintenance (gitignore, license, README structure) |
| `refactor` | Reorganizing files without changing content |

Examples:

```
docs: add PostgreSQL 16 install guide for Ubuntu 24.04

docs(linux): fix incorrect xrdp port in troubleshooting section

chore: add docker/ to .gitignore for local test outputs

feat: add ci-cd/ folder with GitHub Actions OIDC-to-GCP guide
```

---

## Pre-push checklist

Before `git push`, confirm:

- [ ] File is in the **correct folder** (or new folder is justified + added to README structure)
- [ ] Filename follows **kebab-case** rules
- [ ] Note uses the **template** (title, prereqs, steps, verification, troubleshooting)
- [ ] **All real values replaced** with placeholders (run [secret scan](#secret-scan))
- [ ] **README index updated** with a link to the new note
- [ ] `.gitignore` updated if needed
- [ ] Commit message follows the [format](#commit-message-format)
- [ ] `git diff` reviewed line-by-line (no accidental large blobs, no `node_modules`, no `.env`)

---

## For AI agents (Cursor / Claude Code / etc.)

If you're an AI agent helping the user add a note:

1. **Read this whole file first.** Don't skip steps.
2. Always **ask the user** before creating a new top-level folder.
3. Always **propose** the placeholder substitutions before committing — don't auto-replace silently in case the user wants to keep some values.
4. Always **run the secret-scan command** before suggesting `git add`.
5. Always **update the README index** in the same change set.
6. Use the [commit message format](#commit-message-format).
7. **Never** push without showing the user the staged diff first.

---

## Quick reference card (print/pin this)

```
┌─────────────────────────────────────────────────────────┐
│ 1. Pick folder    → see Folder map                      │
│ 2. Name file      → kebab-case, descriptive .md         │
│ 3. Use template   → title, prereqs, steps, verify, ts   │
│ 4. Sanitize       → replace all real values             │
│ 5. Scan secrets   → rg + gitleaks                       │
│ 6. Index in README→ add link under correct section      │
│ 7. Commit         → docs: <imperative summary>          │
│ 8. Diff + push    → review staged changes first         │
└─────────────────────────────────────────────────────────┘
```

---

_Last updated: May 1, 2026_
