# Mac Tools

macOS-specific scripts and utilities — runnable with a single `bash <(curl ...)` command that auto-installs any optional dependencies.

[Back to repo root](../README.md)

---

## Tools

| Tool | Description | Commands |
|------|-------------|----------|
| [`mac-info/`](mac-info/) | Battery health, charging, power flow, CPU, memory, disk, network, thermals & top processes | **Report:** `bash <(curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/mac/mac-info/run.sh)` <br> **Live monitor:** `bash <(curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/mac/mac-info/run.sh) --live` <br> **Export:** append `--export` |

## Guides

| Guide | Description |
|-------|-------------|
| [`secure-api-credentials-keychain.md`](secure-api-credentials-keychain.md) | Complete guide to storing and using API credentials (AWS, MongoDB, Cloudflare) securely using macOS Keychain — includes `load-secrets.sh`, AI assistant rules, Git best practices, and a 30-point security checklist |

---

## Requirements

- macOS 12 Monterey or later
- Python 3.8+ (pre-installed on macOS)
- `psutil` pip package — **auto-installed** by `run.sh` if missing
