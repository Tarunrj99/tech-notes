# tech-notes

> Personal collection of setup guides, how-tos, and troubleshooting notes covering cloud, Linux, Kubernetes, Docker, networking, and developer tooling. Step-by-step and copy-paste ready — every command tested on real systems.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Why this repo

Every engineer has the same problem: *"I set this up six months ago — how did I do it again?"*

This repo is the answer. Each note is a self-contained, dated, command-by-command walkthrough that I (or anyone) can follow without searching Google or Stack Overflow again.

Think of it as a **personal runbook + public knowledge base**.

---

## Repository structure

```
tech-notes/
├── README.md                # this file
├── AGENTS.md                # the workflow for adding new notes (READ FIRST)
├── LICENSE                  # MIT
├── SECURITY.md              # how to report a security issue
├── CONTRIBUTING.md          # how to add a new note
├── .gitignore
│
├── ai-prompts/              # Tool-agnostic AI prompts (Cursor + Claude + ChatGPT + ...)
├── linux/                   # Linux installs, configs, troubleshooting
├── cloud/                   # Cloud-provider specific guides (GCP / AWS / Azure)
├── kubernetes/              # k8s installs, helm, operators, troubleshooting
├── docker/                  # Docker / containerd / image building
├── networking/              # VPN, DNS, firewalls, load balancers
├── tools/                   # CLI tools, IDEs, dev environment setups
└── snippets/                # Quick one-liners and shell snippets
```

> Folders are added as content lands — empty folders aren't tracked.

---

## Index

### AI Prompts (tool-agnostic)

- [Google Docs HTML formatting](ai-prompts/google-docs-html-formatting/) — universal AI prompt that converts any HTML file into a layout that pastes cleanly into Google Docs. Wrappers included for Cursor (`.mdc`) and Claude Code (`SKILL.md`); also works in ChatGPT/Gemini as a plain prompt. Trigger: `apply doc formatting`.

### Linux

- [Setting up GUI mode in Ubuntu Linux 26.04 through CLI](linux/ubuntu-vm-xfce-rdp-setup-guide.md) — install XFCE desktop on a headless Ubuntu VM and access it over RDP. Works on local, GCP, AWS, Azure, or any Ubuntu VM.

### Tools

- [Cursor — Rules Setup & Reference Guide](tools/cursor/rules-setup-guide.md) — what Cursor Rules are, how to create global vs project rules, plus 6 Cursor-specific drop-in rules (commit format, Kubernetes/Docker conventions, shell scripting, security hygiene, GCP CLI hygiene). Files in [`tools/cursor/rules/`](tools/cursor/rules/).

*(More notes will be added here as they are published.)*

---

## How to use

1. Browse the folder structure or use the index above.
2. Open the `.md` file you need.
3. Follow the steps — every command is copy-paste ready.
4. If you hit a snag, check the **Troubleshooting** section at the bottom of each guide.

All guides assume:

- You're comfortable in a terminal
- You have `sudo` access (for installs)
- You're using a modern Ubuntu / Debian / RHEL-derivative unless stated otherwise

---

## Conventions

- **Filenames:** lowercase kebab-case, descriptive (`ubuntu-vm-xfce-rdp-setup-guide.md`)
- **Top of every note:** short purpose, target OS / version, dependencies
- **Code blocks:** all commands fenced; no smart quotes, no line numbers, no prompts (`$`) inside the block
- **Placeholders:** wrapped in angle brackets, e.g. `<your-username>`, `<vm-public-ip>` — never real hostnames, IPs, or credentials
- **Cloud-agnostic where possible:** if a step differs by provider, list them side-by-side

---

## Contributing / Adding a new note

**Read [AGENTS.md](AGENTS.md) first** — it's the single source of truth for the workflow:

- Where to put new files (folder map)
- How to name them (kebab-case rules)
- The note template
- How to sanitize real values into placeholders
- Secret-scan command to run before commit
- How to update the index in this README
- Commit message format
- Pre-push checklist

The same file is followed by AI agents (Cursor, Claude Code, etc.) when they help add content.

For external contributors, see also [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Security

Found a sensitive value (real IP, key, credential) accidentally committed?
Please **don't** open a public issue — see [SECURITY.md](SECURITY.md) for responsible disclosure.

---

## License

[MIT](LICENSE) © Tarun Saini

You're free to copy, adapt, and redistribute these notes — attribution appreciated but not required.
