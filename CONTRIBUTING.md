# Contributing to tech-notes

Thanks for your interest. This repo is a personal notes collection, but PRs that improve clarity, fix mistakes, or add high-quality new guides are very welcome.

## Quick start

1. Fork the repo
2. Create a branch: `git checkout -b add/<short-description>`
3. Add or edit a `.md` file in the appropriate folder (see [folder conventions](#folder-conventions))
4. Run `git diff` and check your work
5. Open a Pull Request describing what you added/changed and why

## What makes a good note

A good note answers **"how do I do X on Y?"** in the shortest possible path.

| Do | Don't |
|---|---|
| Copy-paste ready commands | Pseudo-code or "do it like this" |
| Tested on a real system | Untested or theoretical |
| Cloud-agnostic where possible | Lock to one provider unless required |
| Use placeholders for any real values | Leak real IPs, hostnames, keys |
| Include the **what**, **why**, and **troubleshooting** | Just commands with no context |

## Folder conventions

| Folder | Use for |
|---|---|
| `linux/` | Anything Linux-distro level: installs, desktop, services, system config |
| `cloud/<provider>/` | Provider-specific (gcp/, aws/, azure/) |
| `kubernetes/` | k8s clusters, helm, operators, troubleshooting |
| `docker/` | Docker / containerd / image building |
| `networking/` | VPN, DNS, firewalls, load balancers |
| `tools/` | CLI tools, IDEs, dev environments |
| `snippets/` | Short one-off shell snippets / aliases |

If your note doesn't fit, suggest a new folder in the PR description.

## Filename rules

- Lowercase
- Kebab-case (words separated by `-`)
- Descriptive: filename alone should tell the reader what it is
- End in `.md`

Good: `ubuntu-vm-xfce-rdp-setup-guide.md`, `gke-private-cluster-setup.md`
Bad: `notes.md`, `setup.md`, `MyGuide.MD`

## Note template

Copy this into a new file and fill in:

```markdown
# <Title — what the reader will accomplish>

> One-line summary of the goal and target environment.

| Item | Value |
|---|---|
| OS / target | e.g. Ubuntu 24.04 |
| Tested on | e.g. AWS EC2 t3.medium, May 2026 |
| Time to complete | ~30 min |

---

## Prerequisites

- bullet list of things the reader needs

---

## Steps

### Step 1 — <action>

```bash
# command
```

Explanation of what just happened (1-2 lines).

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

_Tested: <date>_
```

## Style

- Use **headings**, **tables**, and **fenced code blocks** liberally
- One command per line in code blocks (so they're easy to copy)
- No `$` prompt prefix in commands
- Wrap long URLs in `<>` or markdown link syntax
- Avoid screenshots unless absolutely needed (text is searchable; images aren't)

## Sensitive data

Before committing, search your file for accidental leaks:

```bash
rg -i 'password|token|secret|api[-_]?key|aws_|sk-|ghp_|<your-real-ip>'
```

If you find anything, replace with a `<placeholder>` and check `git diff` before pushing.

If something sensitive **is** committed by accident, see [SECURITY.md](SECURITY.md).

---

Thanks for contributing.
