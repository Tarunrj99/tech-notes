# Mac Tools

macOS-specific scripts and utilities — runnable with a single `curl | bash` command that auto-installs any optional dependencies.

[Back to tools/](../README.md) · [Back to repo root](../../README.md)

---

## Tools

| Tool | Description | Commands |
|------|-------------|----------|
| [`mac-info/`](mac-info/) | Battery health, charging, power flow, CPU, memory, disk, network, thermals & top processes | **Report:** `bash <(curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/mac-info/run.sh)` <br> **Live monitor:** `bash <(curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/mac-info/run.sh) --live` <br> **Export:** append `--export` |

---

## Requirements

- macOS 12 Monterey or later
- Python 3.8+ (pre-installed on macOS)
- `psutil` pip package — **auto-installed** by `run.sh` if missing
