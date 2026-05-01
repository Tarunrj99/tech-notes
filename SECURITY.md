# Security Policy

This repository is a **documentation / notes** repository — it contains no running code, services, or executables.

However, since the notes include real-world setup commands, there is a small risk that something sensitive (an internal hostname, IP address, API key, password, etc.) is accidentally committed in a guide.

## Reporting a sensitive disclosure

If you spot **any** of the following in this repository:

- Internal hostnames, IPs, or domain names
- API keys, tokens, passwords, or private SSH keys
- Customer or employer-identifying information
- Credentials of any kind, even partial

**Please do NOT open a public GitHub issue.**

Instead, contact the maintainer privately:

- Open a [private security advisory on GitHub](https://github.com/Tarunrj99/tech-notes/security/advisories/new)
- Or email the maintainer (link via the [GitHub profile](https://github.com/Tarunrj99))

I'll review and remove (or rewrite the git history if needed) within **48 hours**.

## What's NOT a security issue

- A guide using a placeholder like `<your-username>` or `<vm-public-ip>` is intentional and safe.
- A guide describing an *attack technique* (e.g. firewall rules, RDP hardening) is informational, not a vulnerability.

## Scope

This policy covers only the contents of this repository.
For vulnerabilities in third-party tools mentioned in guides (e.g. xrdp, Docker, kubectl, Claude Code), please report them upstream to those projects.

---

Thank you for helping keep these notes safe and reusable.
