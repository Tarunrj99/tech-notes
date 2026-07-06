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

# ── Terminal animation helpers ─────────────────────────────────────────────
#   Works when stdout is a TTY (interactive terminal).
#   Falls back to plain echoes when piped / redirected.
_HAS_TTY=false
[ -t 1 ] && _HAS_TTY=true

_SPIN_PID=""
_LINES=0   # number of status lines printed during setup (for cleanup)

# Start an animated braille spinner in the background, overwriting current line.
_spin_start() {
    if $_HAS_TTY; then
        ( i=0; f="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
          while true; do
              printf "\r  %s  %s   " "${f:$((i % 10)):1}" "$1"
              sleep 0.08; i=$(( i + 1 ))
          done ) &
        _SPIN_PID=$!
    fi
}

# Kill the spinner and erase its line.
_spin_stop() {
    if [ -n "$_SPIN_PID" ]; then
        kill "$_SPIN_PID" 2>/dev/null
        wait "$_SPIN_PID" 2>/dev/null || true
        _SPIN_PID=""
    fi
    if $_HAS_TTY; then printf "\r\033[K"; fi
}

# Print a tracked status line (will be erased later by _clear_setup).
_say() { printf "  %s\n" "$1"; _LINES=$(( _LINES + 1 )); }

# Erase the most-recently printed status line (for in-place replacement).
_unsay() {
    if $_HAS_TTY; then printf "\033[A\033[2K"; fi
    _LINES=$(( _LINES - 1 ))
}

# Erase all tracked setup lines, leaving a clean terminal for the report.
_clear_setup() {
    if $_HAS_TTY; then
        while [ "$_LINES" -gt 0 ]; do
            printf "\033[A\033[2K"
            _LINES=$(( _LINES - 1 ))
        done
    fi
    _LINES=0
}

# ── 1. macOS check ─────────────────────────────────────────────────────────
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "  This script is macOS-only."; exit 1
fi

# ── 2. Python 3 check ──────────────────────────────────────────────────────
_spin_start "Checking Python"

if ! command -v python3 &>/dev/null; then
    _spin_stop
    echo ""; echo "  Python 3 not found."; echo ""
    echo "  Install options:"
    echo "    brew install python3"
    echo "    https://www.python.org/downloads/"
    echo ""; exit 1
fi

PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [[ "$PY_MAJOR" -lt 3 ]] || { [[ "$PY_MAJOR" -eq 3 ]] && [[ "$PY_MINOR" -lt 8 ]]; }; then
    _spin_stop
    echo "  Python 3.8+ required. Found: ${PY_MAJOR}.${PY_MINOR}.  Upgrade: brew install python3"
    exit 1
fi

_spin_stop
_say "Python ${PY_MAJOR}.${PY_MINOR}"

# ── 3. psutil check / install ──────────────────────────────────────────────
_spin_start "Checking dependencies"

if ! python3 -c "import psutil" 2>/dev/null; then
    _spin_stop
    _say "Installing psutil..."
    _spin_start "Installing psutil"

    if   python3 -m pip install --quiet --user psutil                         2>/dev/null ||
         python3 -m pip install --quiet --user --break-system-packages psutil 2>/dev/null ||
         python3 -m pip install --quiet psutil                                2>/dev/null; then
        _spin_stop; _unsay; _say "psutil installed"
    else
        _spin_stop; _unsay; _say "psutil unavailable — running in basic mode"
    fi
else
    _spin_stop
fi

# ── 4. Download report script ──────────────────────────────────────────────
TMP_SCRIPT=$(mktemp "${TMPDIR:-/tmp}/mac_battery_info_XXXXXXXX")
trap 'rm -f "${TMP_SCRIPT}"' EXIT

_spin_start "Fetching report"
if ! curl -fsSL "${SCRIPT_URL}" -o "${TMP_SCRIPT}" 2>/dev/null; then
    _spin_stop
    echo "  Download failed — check your internet connection."; exit 1
fi
_spin_stop

# ── 5. Clear setup lines and run the report ────────────────────────────────
#   All setup lines disappear; the Python report output follows cleanly.
_clear_setup

# Pass all arguments (e.g. --export, --export /path) straight to Python.
python3 "${TMP_SCRIPT}" "$@"
