# tech-notes

**A personal tech knowledge base.**
Step-by-step setup guides, reusable AI prompts, IDE rules, and troubleshooting notes for cloud, Linux, Kubernetes, Docker, and developer tooling — every command tested on real systems.

*One repo. Everything I've ever set up. Copy-paste ready.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Made with Markdown](https://img.shields.io/badge/made%20with-markdown-1f425f.svg)](https://daringfireball.net/projects/markdown/)
[![Last commit](https://img.shields.io/github/last-commit/Tarunrj99/tech-notes)](https://github.com/Tarunrj99/tech-notes/commits/main)
[![Repo size](https://img.shields.io/github/repo-size/Tarunrj99/tech-notes)](https://github.com/Tarunrj99/tech-notes)

[Why](#why-this-repo-exists) · [Catalog](#note-catalog) · [Layout](#repository-layout) · [How to use](#how-to-use) · [Conventions](#conventions) · [Contribute](#adding-a-new-note) · [License](#license)

---

## Why this repo exists

Every engineer has the same recurring problem: *"I set this up six months ago — how exactly did I do it again?"*

Most answers end up scattered across browser bookmarks, Slack DMs, scratch files in `~/Downloads`, and half-remembered Stack Overflow threads. By the time you find them, the version you used is deprecated and the top-voted answer doesn't apply anymore.

This repo is the opposite:

- **Each note is self-contained** — purpose, prerequisites, copy-paste commands, troubleshooting, all in one file.
- **Each note is dated and tested** — written from a real working setup, not from memory.
- **Each note is sanitized** — real IPs, emails, and project IDs are replaced with `<placeholders>` so the file is safe to share publicly.
- **Each note is portable** — cloud-agnostic where possible, with provider-specific commands listed side-by-side when they differ.

Think of it as a **personal runbook + public knowledge base**. Bookmark a note once, follow it forever.

---

## Table of contents

1. [Why this repo exists](#why-this-repo-exists)
2. [Note catalog](#note-catalog)
3. [Repository layout](#repository-layout)
4. [How to use](#how-to-use)
5. [Conventions](#conventions)
6. [Adding a new note](#adding-a-new-note)
7. [Repo docs index](#repo-docs-index)
8. [Security](#security)
9. [License](#license)

---

## Note catalog

> Every published note in this repo, grouped by topic. Status legend: **stable** = tested end-to-end · **draft** = WIP, may have gaps.

### AI prompts (tool-agnostic)

| Note | What you get | Works with | Status |
| --- | --- | --- | --- |
| [Google Docs HTML formatting](ai-prompts/google-docs-html-formatting/) | Universal AI prompt that converts any HTML file into a layout that pastes cleanly into Google Docs (proper headings, lists, tables, code blocks). Trigger phrase: `apply doc formatting`. | Cursor (`.mdc`), Claude Code (`SKILL.md`), ChatGPT, Gemini, any LLM | stable |

### Cloud — AWS

| Note | What you'll set up | Tested with | Status |
| --- | --- | --- | --- |
| [SES — CloudWatch logging setup](cloud/aws/ses-cloudwatch-logging-setup-guide.md) | Per-email SES visibility (bounce / complaint / delivery) via SES → SNS → Lambda → CloudWatch. Drop-in CloudFormation template, deployed three times. Catches reputation problems **before** AWS enforces a SHUTDOWN. | SES + Lambda Python 3.12, CloudFormation, AWS CloudShell | stable |

### Cloud — GCP

| Note | What you'll set up | Tested with | Status |
| --- | --- | --- | --- |
| [GCS bucket — public file access & security](cloud/gcp/gcs-bucket-public-access-and-security-guide.md) | Make GCS files **publicly readable by URL** but the bucket **not listable**. Includes a Cloud Function (Gen 2, Python) that auto-applies public-read ACL on every new upload. | GCS, Cloud Functions Gen 2, Eventarc | stable |

### Kubernetes

| Note | What you'll set up | Cluster | Status |
| --- | --- | --- | --- |
| [GKE RBAC — DevOps user access setup](kubernetes/gke-rbac-devops-user-access-guide.md) | Custom `ClusterRole` + `ClusterRoleBinding` granting operational (port-forward, log view, exec, restart, Helm uninstall) access **without** giving full admin or app-creation rights. Includes a complete RBAC parameter reference for extending. | GKE | stable |
| [GKE + AccuKnox CNAPP — integration & onboarding](kubernetes/gke-accuknox-cnapp-integration-guide.md) | End-to-end onboarding of a GKE cluster to AccuKnox CNAPP — IAM, custom role, VPC egress firewall (the #1 failure point), KubeArmor + agents via Helm, multi-cluster, GAR image scanning, real troubleshooting. | GKE | stable |

### Linux

| Note | What you'll set up | Tested on | Status |
| --- | --- | --- | --- |
| [Ubuntu VM — XFCE desktop + RDP access from CLI](linux/ubuntu-vm-xfce-rdp-setup-guide.md) | Headless Ubuntu VM → full XFCE desktop accessible via RDP (Windows App / Microsoft Remote Desktop). Cloud-agnostic: works on local VMs, GCP, AWS, and Azure. | Ubuntu 26.04 | stable |

### macOS

| Tool | What you get | Run | Status |
| --- | --- | --- | --- |
| [Mac System Info + Live Monitor](mac/mac-info/) | Full macOS snapshot — battery health, charging & power flow, CPU, memory, disk, network, thermals, top processes. Includes a live real-time dashboard (like `htop`) that refreshes every 3 s. | `bash <(curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/mac/mac-info/run.sh)` | stable |

### Tools

| Note | What you'll learn | Audience | Status |
| --- | --- | --- | --- |
| [Cursor — Rules setup & reference guide](tools/cursor/rules-setup-guide.md) | What Cursor Rules are, global vs project rules, file format, plus 6 drop-in `.mdc` rules (commit format, K8s, Docker, shell, security, GCP CLI). Files in [`tools/cursor/rules/`](tools/cursor/rules/). | Cursor IDE users | stable |
| [GitHub — Org-owned GitHub App for CI/CD](tools/github/org-github-app-for-cicd-setup-guide.md) | Replace personal PATs / "service-user accounts" with an org-owned GitHub App that mints short-lived installation tokens. Includes the migration playbook for centralized reusable workflows + bulk-update of downstream app repos. | Platform / DevOps engineers, GitHub org admins | stable |

*More notes will be added here as they're published. The order inside each section is alphabetical.*

---

## Repository layout

```
tech-notes/
├── README.md                          ← you are here (start here)
├── AGENTS.md                          ← workflow for adding notes (read before contributing)
├── CONTRIBUTING.md                    ← short version for human contributors
├── SECURITY.md                        ← how to report sensitive data leaks
├── LICENSE                            ← MIT
├── .gitignore
│
├── ai-prompts/                        ← tool-agnostic AI prompts
│   ├── README.md
│   └── google-docs-html-formatting/
│       ├── README.md
│       ├── prompt.md                  ← the universal prompt text
│       └── wrappers/
│           ├── cursor.mdc             ← Cursor wrapper (with frontmatter)
│           └── claude-skill.md        ← Claude Code skill wrapper
│
├── cloud/                             ← public-cloud-specific guides
│   ├── README.md
│   ├── aws/
│   │   ├── README.md
│   │   └── ses-cloudwatch-logging-setup-guide.md
│   └── gcp/
│       ├── README.md
│       └── gcs-bucket-public-access-and-security-guide.md
│
├── kubernetes/                        ← K8s installs, RBAC, security integrations
│   ├── README.md
│   ├── gke-rbac-devops-user-access-guide.md
│   └── gke-accuknox-cnapp-integration-guide.md
│
├── linux/                             ← Linux installs, configs, troubleshooting
│   ├── README.md
│   └── ubuntu-vm-xfce-rdp-setup-guide.md
│
├── mac/                               ← macOS scripts and utilities
│   ├── README.md
│   └── mac-info/                      ← battery, power, CPU, memory, disk, network — static + live monitor
│
└── tools/                             ← IDE rules, CLI configs, dev environment setups
    ├── README.md
    ├── cursor/
    │   ├── README.md
    │   ├── rules-setup-guide.md
    │   └── rules/                     ← drop-in .mdc files
    │       ├── devops-kubernetes.mdc
    │       ├── docker-best-practices.mdc
    │       ├── gcp-cli-hygiene.mdc
    │       ├── git-commit-format.mdc
    │       ├── security-hygiene.mdc
    │       └── shell-scripting.mdc
    └── github/
        ├── README.md
        └── org-github-app-for-cicd-setup-guide.md
```

> Folders are added as content lands — empty folders aren't tracked. Future planned folders include `cloud/azure/`, `docker/`, `networking/`, `snippets/`.

---

## How to use

1. **Browse the [catalog](#note-catalog) above** or open the folder you need.
2. **Open the `.md` file** — every note starts with a one-line purpose, prerequisites, and target OS.
3. **Copy-paste commands** — they're written to run as-is. Replace anything in `<angle brackets>` with your own values.
4. **Hit a snag?** Each note has a *Troubleshooting* section at the bottom for the failure modes I actually ran into.

### Assumptions every note makes

- You're comfortable in a terminal.
- You have `sudo` access on the target machine (for installs).
- You're on a modern Ubuntu / Debian / RHEL-derivative unless the note says otherwise.

---

## Conventions

The bar is low: **a note is a real conversation in plain markdown**. The structural rules below exist only to keep things searchable and sanitized.

| Aspect | Convention |
| --- | --- |
| Filenames | lowercase `kebab-case`, descriptive (`ubuntu-vm-xfce-rdp-setup-guide.md`) |
| Top of every note | one-line purpose · target OS / version · prerequisites |
| Code blocks | all commands fenced; no smart quotes, no line numbers, no `$` prompt inside the block |
| Placeholders | wrapped in angle brackets — `<your-username>`, `<vm-public-ip>`, `<project-id>` — never real values |
| Cloud-agnostic | if a step differs by provider, list them side-by-side (GCP / AWS / Azure) |
| One scenario per file | don't combine "install + monitor + scale" into one mega-note; split it |
| Date inside the note | a small "_tested on YYYY-MM-DD on Ubuntu X.Y_" line near the top |

---

## Adding a new note

> **Read [AGENTS.md](AGENTS.md) first.** It is the single source of truth for the workflow — followed by humans **and** by AI agents (Cursor, Claude Code, etc.) when they help add content.

The short version:

1. Pick the right folder (or create one if it's a new topic — see the layout above).
2. Name the file in `kebab-case` describing the *outcome* (`vpn-wireguard-server-setup.md`, not `wg-stuff.md`).
3. Use the note template at the top of `AGENTS.md`.
4. Sanitize: replace every real IP, email, project ID, and username with `<placeholders>`.
5. Run the secret-scan command from `AGENTS.md` before committing.
6. Update the [Note catalog](#note-catalog) table in this README.
7. Commit with the format defined in `AGENTS.md` (`docs(<topic>): add ...`).

A short version for external contributors lives in [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Repo docs index

| Doc | What's in it |
| --- | --- |
| [README.md](README.md) | This file — entry point, catalog, conventions |
| [AGENTS.md](AGENTS.md) | Full workflow for adding notes, sanitization rules, secret-scan command, pre-push checklist (used by humans **and** AI agents) |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Short version for external human contributors |
| [SECURITY.md](SECURITY.md) | How to report a leaked secret or sensitive value found in this repo |
| [LICENSE](LICENSE) | MIT |

---

## Security

Found a sensitive value (real IP, email, key, credential) accidentally committed?
**Please don't open a public issue** — follow the responsible-disclosure process in [SECURITY.md](SECURITY.md).

The repo also has a sanitization workflow baked into [AGENTS.md](AGENTS.md) so this shouldn't happen at commit time, but mistakes happen — quiet disclosure helps me clean up history without exposing the value further.

---

## License

[MIT](LICENSE) © Tarun Saini

You're free to copy, adapt, and redistribute these notes inside your organisation or to fork them as the base for your own knowledge base. Attribution is appreciated but not required.
