# Mac Tools

macOS-specific scripts and utilities — runnable with a single `curl | bash` command that auto-installs any optional dependencies.

[Back to tools/](../README.md) · [Back to repo root](../../README.md)

---

## Tools

| Tool | Description | Commands |
|------|-------------|----------|
| [`battery-info/`](battery-info/) | Full battery health, charging, power flow, thermals & system snapshot | **Report:** `curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/run.sh \| bash` <br> **Live monitor:** `curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/run.sh \| bash -s -- --live` <br> **Export:** append `-- --export` |

---

## Requirements

- macOS 12 Monterey or later
- Python 3.8+ (pre-installed on macOS)
- `psutil` pip package — **auto-installed** by `run.sh` if missing
