# 🔋 Mac Battery & System Info

A single Python script that prints a real-time, richly detailed report of your Mac's battery health, charging state, power flow, GPU, CPU, memory, disk, network, top processes, and hardware — all in one terminal output.

**macOS only** (Apple Silicon + Intel). Core features require no pip packages. The optional `psutil` package (auto-installed by `run.sh`) adds CPU per-core stats and I/O counters.

---

## ⚡ Single Command — Fetch, Install & Run

```bash
curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/run.sh | bash
```

> This one command does everything:
> 1. Shows an animated spinner that stays visible through setup AND report generation (~15 s) — disappears cleanly before the report is displayed
> 2. Checks that Python 3.8+ is installed
> 3. Auto-installs the `psutil` package if missing (handles PEP 668 / Homebrew Python)
> 4. Downloads `battery_info.py` to a temp file
> 5. Runs the full report; stdout is buffered so the spinner stays clean until Python finishes
> 6. Cleans up all temp files on exit

---

## 📤 Export the Report to a File

### Save to Desktop (default path)

```bash
curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/run.sh | bash -s -- --export
```

> Saves to: `~/Desktop/battery-report-YYYY-MM-DD-HH-MM.txt`
> The report is also printed to the terminal at the same time.

### Save to a custom path

```bash
curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/run.sh | bash -s -- --export ~/Documents/my-report.txt
```

### How export works

| What happens | Detail |
|---|---|
| Report prints to terminal | Always, regardless of `--export` |
| File is written | UTF-8 plain text, ANSI color codes stripped for clean reading |
| Default save location | `~/Desktop/battery-report-<timestamp>.txt` |
| Custom path | Pass any path after `--export` |
| Timestamp format | `YYYY-MM-DD-HH-MM` e.g. `battery-report-2026-07-06-15-30.txt` |

---

## 🖥️ Local Run (after cloning)

```bash
# Clone the repo
git clone https://github.com/Tarunrj99/tech-notes.git
cd tech-notes

# Run the bootstrap (installs psutil, runs report)
bash tools/mac/battery-info/run.sh

# Or run the script directly (basic mode, no psutil install)
python3 tools/mac/battery-info/scripts/battery_info.py

# Run with export
python3 tools/mac/battery-info/scripts/battery_info.py --export
python3 tools/mac/battery-info/scripts/battery_info.py --export ~/Desktop/report.txt
```

---

## 📦 Dependencies

| Package | Required | How to get | What it adds |
|---------|----------|-----------|--------------|
| Python 3.8+ | **Yes** | Pre-installed on macOS / `brew install python3` | Core runtime |
| `psutil` | Optional | Auto-installed by `run.sh` | CPU per-core %, CPU frequency, disk I/O counters, network I/O counters |

All other data comes from macOS built-in tools:
`ioreg` · `system_profiler` · `sysctl` · `pmset` · `vm_stat` · `top` · `ps` · `diskutil` · `netstat` · `iostat` · `networksetup` · `ipconfig` · `scutil` · `curl`

---

## 📊 What the Report Shows (14 Sections)

### 1. 🖥️ Machine
| Field | What it shows |
|---|---|
| Model | MacBook model name and identifier |
| Chip | Apple M1/M2/M3 or Intel chip, architecture (arm64/x86_64) |
| CPU Cores | Physical + logical core count |
| RAM | Total unified memory |
| Disk | SSD model and capacity |
| macOS | Version, codename (Sequoia / Sonoma / etc.), and build number |
| Serial | Mac serial number |
| Hostname | Computer name on the network |

---

### 2. 🔌 Charger / Adapter
| Field | What it shows |
|---|---|
| Connected | Yes/No with status |
| Name | Adapter product name (e.g. "70W USB-C Power Adapter") |
| Manufacturer | Apple Inc. or third-party |
| Model ID | Internal adapter model hex code |
| Serial | Adapter hardware serial number |
| Firmware | Adapter firmware version + hardware revision |
| Adapter Rating | Rated max wattage |
| **Negotiated PD** | USB-C Power Delivery profile actually in use (e.g. 20V × 3.4A = 68W profile 3) |
| **Wall Draw Now** | Real-time watts being drawn from the wall (V × A from PMU) |
| **Adapter Usage** | % of the negotiated PD contract being used (with progress bar) |
| **Headroom Left** | Unused wattage — how much more the adapter could deliver |

> **Why "Wall Draw Now" varies:** Your 68W adapter doesn't always draw 68W. It adjusts dynamically. At idle with battery near full, you may see 8–12W. At low battery + heavy load, you'll see 30–60W.

---

### 3. ⚡ Power Flow (real-time, from PMU telemetry)
Shows exactly where every watt from the wall goes.

```
Wall Input   29.25 W  ← measured at the adapter
  Adapter Loss  0.71 W  ← conversion inefficiency (heat in the brick)
  System Gets  29.26 W  ← delivered to the Mac internals
    System Load  8.37 W  ← CPU + GPU + display + peripherals
    Battery In  20.89 W  ← going into the battery pack

Balance check: 8.37 + 20.89 = 29.26 W  ≈ 29.25 W ✓
```

> The **balance check** is a self-validation — it confirms the PMU telemetry numbers are consistent.

---

### 4. 🔋 Battery — State
| Field | What it shows |
|---|---|
| Level | % charge with Unicode progress bar |
| Status | Charging ⚡ / Discharging 🔋 / Full ✅ / Plugged-not-charging |
| Time to Full / Remaining | Estimated time based on current charge/drain rate |
| Battery Voltage | Pack voltage right now (typically 10–13V for a 3-cell pack) |
| Current Now | Amps flowing in (+) or out (-) of the pack |
| **Pack Power** | True watts going into/out of the battery (from PMU telemetry) |
| Low Power Mode | On/Off |
| Today Range | Minimum and maximum SOC % seen today |
| **Cell Voltages** | Individual voltage of each cell in the pack |

> **Pack Power vs Wall Input:** Pack Power (~20W) ≠ Wall Input (~29W) because the system also consumes ~9W. Wall Input = System Load + Battery Power.

---

### 5. 🩺 Battery — Health
| Field | What it shows |
|---|---|
| **Health %** | `(Max Capacity / Design Capacity) × 100` — the standard SoH metric |
| Max Capacity | Current real max (mAh), degraded from original design |
| Design Capacity | Original factory-rated capacity |
| Nominal Cap | Apple's nominal reference capacity |
| Current Charge | mAh currently stored |
| **Qmax (cells)** | Measured per-cell capacity from coulomb counting (internal gauge) |
| Cycle Count | Charges used vs rated lifespan, with progress bar + remaining estimate |
| Battery Serial | The battery module's own serial (different from Mac serial) |
| Peak V / Low V | Highest and lowest pack voltages in the battery's lifetime |
| Peak Charge I | Maximum charging current ever recorded |

**Health labels:**

| Range | Label |
|---|---|
| ≥ 90% | Excellent |
| 80–89% | Good |
| 70–79% | Fair |
| 60–69% | Degraded |
| < 60% | Poor |

---

### 6. 🌡️ Thermal
| Field | What it shows |
|---|---|
| Battery Temp (now) | Current battery temperature in °C |
| Lifetime Avg | Average temperature over the battery's entire life |
| Lifetime Min / Max | Coldest/hottest the battery has ever been |
| Thermally limited | Total seconds Apple has throttled charging speed due to heat (lifetime counter) |

---

### 7. 🏃 Runtime
| Field | What it shows |
|---|---|
| Uptime | How long since last restart |
| Total Op. Hours | Cumulative lifetime hours the battery has been active |
| Load Avg | 1-minute, 5-minute, 15-minute CPU load averages |
| **Processes** | Total number of running processes right now |

---

### 8. ⚙️ CPU
| Field | What it shows |
|---|---|
| Usage | Overall CPU % with bar (user + system) |
| User / System / Idle | CPU time breakdown |
| Frequency | Current CPU frequency in MHz (requires `psutil`) |
| **Per-Core** | Individual % for each core, e.g. C0: 15%, C1: 20%… (requires `psutil`) |

> Per-core data and frequency require `psutil` — auto-installed by `run.sh`.

---

### 9. 🎮 GPU & Display
| Field | What it shows |
|---|---|
| GPU | Integrated GPU name and core count (e.g. Apple M1, 7-core GPU) |
| Metal | Metal GPU API version (Metal 3 on M1/M2/M3) |
| Display Type | Panel technology (Built-In Retina LCD, etc.) |
| Resolution | Native pixel resolution (e.g. 2560 × 1600 Retina) |
| Connection | How the display connects (Internal, DisplayPort, etc.) |

---

### 10. 💾 Memory
| Field | What it shows |
|---|---|
| Usage | % with bar and pressure label |
| Total | Total unified memory |
| Active | Pages currently in use by foreground apps |
| Wired | Kernel/OS pages locked in RAM (cannot be swapped) |
| Compressed | Pages squashed by macOS memory compressor (still in RAM) |
| Inactive | Reclaimable cached pages |
| Free | Immediately available pages |
| **Swap** | Pages written to SSD as overflow (`sysctl vm.swapusage`); always AES-encrypted on Apple Silicon |

**Pressure labels:** Normal (< 60%) · Moderate (60–80%) · High (> 80%)

---

### 11. 📋 Top Processes
| Field | What it shows |
|---|---|
| PID | Process ID |
| CPU% | Current CPU utilisation of that process |
| MEM% | Percentage of total RAM consumed |
| Process | Shortened binary name (full `/Applications/…` paths stripped) |

Shows **two sub-tables**: "By CPU" (top 5 sorted by CPU%) and "By Memory" (top 5 sorted by MEM%). Placing this after Memory lets you see total CPU + RAM usage first, then identify which processes are responsible.

---

### 12. 💿 Disk ( / )
| Field | What it shows |
|---|---|
| **Storage** | Physical NVMe/SSD model number and raw drive capacity |
| Usage | `(Container Total − Free) / Total` — the true utilisation % |
| Container Total | Full APFS container size (matches physical SSD minus firmware partitions) |
| **System Volume** | Read-only APFS volume containing the macOS installation |
| **Data Volume** | Writable APFS volume for your apps, home folder, and documents |
| Container Free | Space available to both volumes combined |
| I/O (now) | Real-time disk I/O from latest 1-second `iostat` sample (not a historical average) |
| Read / Write lifetime | Cumulative GB transferred since boot (requires `psutil`) |

> **Why two volumes?** macOS uses a sealed read-only System snapshot + a writable Data volume in the same APFS container. `df` only shows the snapshot (misleadingly small). `diskutil` gives the full picture.

---

### 13. 🌐 Network
| Field | What it shows |
|---|---|
| IPv4 | Local IP address on the primary interface (en0) |
| Local IPv6 | Stable SLAAC address on en0 (used for incoming connections) |
| Public IP (v4) | External IPv4 seen by remote servers (`api.ipify.org`) |
| Public IP (v6) | Public IPv6 using macOS privacy extension — matches whatismyip.com (`api6.ipify.org`) |
| Wi-Fi SSID | Connected Wi-Fi network name (blank section if not on Wi-Fi) |
| Wi-Fi Channel | Channel and band — only shown when associated to an SSID |
| Signal / Noise | RSSI signal strength vs noise floor in dBm |
| TX Rate | 802.11 PHY transmit rate negotiated with access point |
| RX / TX (since boot) | Total GB received and sent on all `en*` interfaces since boot |
| Per-interface | Breakdown per en0, en1, etc. (from `netstat` hardware counters) |

---

### 14. 💤 Power Management
| Field | What it shows |
|---|---|
| Power Source | AC Power or Battery Power |
| Sleep Timer | Minutes until system sleep (0 = disabled) |
| Disk Sleep | Disk spin-down / SSD power-down timer |
| Half-dim | Whether display dims at 50% before sleeping — shows `N/A` on macOS 15 Sequoia+ (no longer reported by `pmset`) |
| Lid Wake | Whether opening the lid wakes the Mac — shows `N/A` on macOS 15 Sequoia+ (managed by the OS, not `pmset`) |
| Sleep prevented | `PreventUserIdleSystemSleep` assertion active (e.g. video call, download in progress) |
| Low Power Mode | On / Off (reduces background CPU to extend battery life) |

---

## 📁 Directory Structure

```
battery-info/
├── README.md                  ← you are here (full docs)
├── run.sh                     ← bootstrap: check Python, install deps, fetch & run
├── requirements.txt           ← pip dependencies (psutil>=5.9.0)
├── scripts/
│   └── battery_info.py        ← the report script (700+ lines, no required pip deps)
└── docs/
    └── sample-output.md       ← real terminal output with per-field glossary
```

---

## 📋 Requirements

| Requirement | Version | Notes |
|---|---|---|
| macOS | 12 Monterey+ | Tested on macOS 14 Sonoma and 15 Sequoia |
| Python | 3.8+ | Pre-installed on macOS |
| psutil (pip) | 5.9.0+ | **Optional** — auto-installed by `run.sh` |
| Internet | — | Required only for `run.sh` download and Public IP lookup |

---

## 🔒 Privacy

- No data is sent anywhere except two `curl` calls — one to `api.ipify.org` (IPv4) and one to `api6.ipify.org` (IPv6) for the public IP fields — search for `api.ipify.org` in `battery_info.py` and remove those two lines to disable it
- All battery and hardware data is read from local macOS system interfaces
- `run.sh` downloads `battery_info.py` from this public GitHub repo only, to a temp file that is deleted after the run
