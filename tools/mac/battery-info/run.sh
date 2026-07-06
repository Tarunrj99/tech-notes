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
#   Export report to file (saved to ~/Desktop/battery-report-<timestamp>.txt):
#     curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/run.sh | bash -s -- --export
#
#   Export to a custom path:
#     curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/run.sh | bash -s -- --export ~/Documents/my-report.txt
#
set -euo pipefail

RAW_BASE="https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info"
SCRIPT_URL="${RAW_BASE}/scripts/battery_info.py"
REQ_URL="${RAW_BASE}/requirements.txt"

# ── 1. macOS check ─────────────────────────────────────────────────────────
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "❌  This script is macOS-only. Exiting."
    exit 1
fi

# ── 2. Python 3 check ──────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo ""
    echo "❌  Python 3 not found on this machine."
    echo ""
    echo "    Install options:"
    echo "      brew install python3          (via Homebrew)"
    echo "      https://www.python.org/downloads/   (official installer)"
    echo ""
    exit 1
fi

PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [[ "$PY_MAJOR" -lt 3 ]] || { [[ "$PY_MAJOR" -eq 3 ]] && [[ "$PY_MINOR" -lt 8 ]]; }; then
    echo "❌  Python 3.8+ required. Found: ${PY_MAJOR}.${PY_MINOR}"
    echo "    Upgrade: brew install python3"
    exit 1
fi

echo "✅  Python ${PY_MAJOR}.${PY_MINOR} detected"

# ── 3. Install required packages ───────────────────────────────────────────
echo "📦  Checking dependencies…"

install_pkg() {
    local pkg="$1"
    if python3 -c "import ${pkg}" 2>/dev/null; then
        echo "    ✅  ${pkg} already installed"
        return
    fi
    echo "    📥  Installing ${pkg}…"
    # 1. Standard user install
    if python3 -m pip install --quiet --user "${pkg}" 2>/dev/null; then
        echo "    ✅  ${pkg} installed"
        return
    fi
    # 2. PEP 668 (externally-managed Python, e.g. Homebrew Python on macOS 14+)
    if python3 -m pip install --quiet --user --break-system-packages "${pkg}" 2>/dev/null; then
        echo "    ✅  ${pkg} installed (PEP 668 override)"
        return
    fi
    # 3. System-wide (may need sudo)
    if python3 -m pip install --quiet "${pkg}" 2>/dev/null; then
        echo "    ✅  ${pkg} installed (system)"
        return
    fi
    echo "    ⚠️   ${pkg} install failed — basic mode (CPU per-core stats will be skipped)"
    echo "         Manual fix: python3 -m pip install --user --break-system-packages ${pkg}"
}

# psutil: optional — enables CPU per-core stats, disk I/O, network I/O
install_pkg psutil

# ── 4. Download & run the report ───────────────────────────────────────────
echo "🔍  Fetching report script…"
TMP_SCRIPT=$(mktemp "${TMPDIR:-/tmp}/mac_battery_info_XXXXXXXX")

# Always delete the temp file when the script exits (success, error, or signal).
trap 'rm -f "${TMP_SCRIPT}"' EXIT

if ! curl -fsSL "${SCRIPT_URL}" -o "${TMP_SCRIPT}" 2>/dev/null; then
    echo "❌  Could not download the script. Check your internet connection."
    exit 1
fi

echo ""

# Pass all arguments (e.g. --export, --export /path) straight to Python
python3 "${TMP_SCRIPT}" "$@"
