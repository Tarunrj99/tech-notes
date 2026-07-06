#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Mac Battery & System Info — Bootstrap Runner                   ║
# ║  Checks Python 3, installs missing packages, runs the report.   ║
# ╚══════════════════════════════════════════════════════════════════╝
#
# USAGE (fetch & run from GitHub in one command):
#
#   Normal report:
#     curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/run.sh | bash
#
#   Export to Desktop (battery-report-<timestamp>.txt):
#     curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/run.sh | bash -s -- --export
#
#   Export to a custom path:
#     curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/run.sh | bash -s -- --export ~/Documents/my-report.txt
#
set -euo pipefail

SCRIPT_URL="https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/scripts/battery_info.py"

# ── Spinner helpers ────────────────────────────────────────────────────────
# One animated spinner line that updates its message across all setup steps.
# In non-TTY mode (CI, pipe-to-file) setup runs silently; errors go to stderr.
_HAS_TTY=false; [ -t 1 ] && _HAS_TTY=true
_SPIN_PID=""

# _spin "message"  — stop any running spinner, start a new one with message.
# _spin            — stop spinner and clear the line (no new spinner started).
_spin() {
    # Stop any running spinner
    if [ -n "$_SPIN_PID" ]; then
        kill "$_SPIN_PID" 2>/dev/null
        wait "$_SPIN_PID" 2>/dev/null || true
        _SPIN_PID=""
        if $_HAS_TTY; then printf "\r\033[K"; fi
    fi
    # Start new spinner if TTY and message provided
    if $_HAS_TTY && [ -n "${1:-}" ]; then
        local msg="$1"
        ( i=0; f="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
          while true; do
              printf "\r  %s  %s  " "${f:$((i % 10)):1}" "$msg"
              sleep 0.08; i=$(( i + 1 ))
          done ) &
        _SPIN_PID=$!
    fi
}

# ── 1. macOS check ─────────────────────────────────────────────────────────
if [[ "$(uname -s)" != "Darwin" ]]; then
    printf "  This script is macOS-only.\n" >&2; exit 1
fi

# ── 2. Python check ────────────────────────────────────────────────────────
_spin "Checking Python"

if ! command -v python3 &>/dev/null; then
    _spin
    printf "\n  Python 3 not found.\n\n" >&2
    printf "  Install: brew install python3  or  https://www.python.org/downloads/\n\n" >&2
    exit 1
fi

PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [[ "$PY_MAJOR" -lt 3 ]] || { [[ "$PY_MAJOR" -eq 3 ]] && [[ "$PY_MINOR" -lt 8 ]]; }; then
    _spin
    printf "  Python 3.8+ required. Found: %s.%s  —  Upgrade: brew install python3\n" \
           "$PY_MAJOR" "$PY_MINOR" >&2
    exit 1
fi

# ── 3. psutil check / install ──────────────────────────────────────────────
_spin "Checking dependencies"

if ! python3 -c "import psutil" 2>/dev/null; then
    _spin "Installing psutil"
    python3 -m pip install --quiet --user psutil                         2>/dev/null ||
    python3 -m pip install --quiet --user --break-system-packages psutil 2>/dev/null ||
    python3 -m pip install --quiet psutil                                2>/dev/null ||
    true   # continue in basic mode if all attempts fail
fi

# ── 4. Download report script ──────────────────────────────────────────────
_spin "Fetching report"

TMP_SCRIPT=$(mktemp "${TMPDIR:-/tmp}/mac_battery_info_XXXXXXXX")
trap 'rm -f "${TMP_SCRIPT}"' EXIT

if ! curl -fsSL "${SCRIPT_URL}" -o "${TMP_SCRIPT}" 2>/dev/null; then
    _spin
    printf "  Download failed — check your internet connection.\n" >&2; exit 1
fi

# ── 5. Clear spinner and run the report ────────────────────────────────────
# The animated line disappears; the Python report output starts on a clean terminal.
_spin

python3 "${TMP_SCRIPT}" "$@"
