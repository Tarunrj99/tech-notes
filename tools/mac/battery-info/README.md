# 🔋 Mac Battery & System Info

A single Python script that prints a real-time, richly detailed report of your Mac's battery health, charging state, power flow, CPU, memory, disk, network, and hardware — all in one terminal output.

**macOS only** (Apple Silicon + Intel). Core features require no pip packages. The optional `psutil` package (auto-installed by `run.sh`) adds CPU per-core stats and I/O counters.

---

## ⚡ Single Command — Fetch, Install & Run

```bash
curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/run.sh | bash
```

> This one command does everything:
> 1. Checks that Python 3.8+ is installed
> 2. Auto-installs the `psutil` package if missing
> 3. Downloads `battery_info.py` to a temp file
> 4. Runs the full report
> 5. Cleans up the temp file

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

> Replace `~/Documents/my-report.txt` with any path you want.

### How export works

| What happens | Detail |
|---|---|
| Report prints to terminal | Always, same output as without `--export` |
| File is written | UTF-8 text, full report including all sections |
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
| `psutil` | Optional | Auto-installed by `run.sh` | CPU per-core %, disk I/O counters, network I/O counters |

All other data comes from macOS built-in tools:
`ioreg` · `system_profiler` · `sysctl` · `pmset` · `vm_stat` · `top` · `df` · `netstat` · `iostat` · `networksetup` · `scutil` · `curl`

---

## 📊 What the Report Shows (12 Sections)

### 🖥️ Machine
| Field | What it shows |
|---|---|
| Model | MacBook model name and identifier |
| Chip | Apple M1/M2/M3 or Intel chip, architecture (arm64/x86_64) |
| CPU Cores | Physical + logical core count |
| RAM | Total memory |
| Serial | Mac serial number |
| macOS | OS name, version, build number |
| Hostname | Computer name on the network |

---

### 🔌 Charger / Adapter
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

> **Why "Wall Draw Now" matters:** Your 68W adapter does NOT always draw 68W. It adjusts based on what the system needs. If the battery is at 90% and the system is idle, you might only see 8–12W. At low battery + heavy load, you'll see 30–60W.

---

### ⚡ Power Flow (real-time, from PMU telemetry)
Shows exactly where every watt from the wall goes.

```
Wall Input   29.25 W  ← measured at the adapter
  Adapter Loss  0.71 W  ← conversion inefficiency
  System Gets  29.26 W  ← delivered to the Mac internals
    System Load  8.37 W  ← CPU + GPU + display + peripherals
    Battery In  20.89 W  ← going into the battery pack

Balance check: 8.37 + 20.89 = 29.26 W  ≈ 29.25 W ✓
```

> The **balance check** confirms the numbers add up — it's a self-validation of the PMU telemetry data.

---

### 🔋 Battery — State
| Field | What it shows |
|---|---|
| Level | % charge with progress bar |
| Status | Charging ⚡ / Discharging 🔋 / Full ✅ / Plugged-not-charging |
| Time to Full / Remaining | Estimated time based on current charge/drain rate |
| Battery Voltage | Pack voltage right now (typically 10–13V) |
| Current Now | Amps flowing in (+) or out (-) of the pack |
| **Pack Power** | True watts going into/out of the battery (Amperage × Pack Voltage) |
| Low Power Mode | On/Off |
| Today Range | Minimum and maximum SOC % seen today |
| **Cell Voltages** | Individual voltages of each cell (Cell1/Cell2/Cell3) + pack sum |

> **Pack Power vs Wall Input:** Pack Power (~20W) ≠ Wall Input (~29W) because the system also draws ~9W for running. Wall Input = System Load + Battery Power.

---

### 🔋 Battery — Health
| Field | What it shows |
|---|---|
| Health % | `(Max Capacity / Design Capacity) × 100` — how much original capacity remains |
| Max Capacity | Current real max (mAh), degraded from design |
| Design Capacity | Original factory capacity |
| Nominal Cap | Apple's nominal reference capacity |
| Current Charge | mAh currently stored in the battery |
| **Qmax (cells)** | Measured capacity of each cell from coulomb counting (internal gauge data) |
| Cycle Count | Charges used vs rated lifespan, with progress bar |
| Battery Serial | The battery module's own serial number (different from Mac serial) |
| Peak V / Low V | Highest and lowest pack voltages in lifetime |
| Peak Charge I | Maximum charging current ever seen |

**Health labels:**

| Range | Label |
|---|---|
| ≥ 90% | Excellent ✅ |
| 80–89% | Good 🟢 |
| 70–79% | Fair 🟡 |
| 60–69% | Degraded 🟠 |
| < 60% | Poor 🔴 |

---

### 🌡️ Thermal
| Field | What it shows |
|---|---|
| Battery Temp (now) | Current battery temperature in °C |
| Lifetime Avg | Average temperature over the battery's life |
| Lifetime Min/Max | Coldest/hottest the battery has ever been |
| Thermally limited | Total seconds Apple has throttled charging due to heat |

---

### 🏃 Runtime
| Field | What it shows |
|---|---|
| Uptime | How long the Mac has been running since last restart |
| Total Op. Hours | Cumulative lifetime hours the battery has been active |
| Load Avg | 1-minute, 5-minute, and 15-minute CPU load averages |

---

### ⚙️ CPU
| Field | What it shows |
|---|---|
| Usage | Overall CPU % with bar (user + system) |
| User / System / Idle | Breakdown of CPU time |
| Frequency | Current CPU frequency in MHz (psutil) |
| **Per-Core** | Individual usage per core, e.g. C0: 15%, C1: 20%… (psutil required) |

> Per-core data and frequency require `psutil` (auto-installed by `run.sh`).

---

### 💾 Memory
| Field | What it shows |
|---|---|
| Usage | % with bar and pressure label |
| Total | Total RAM |
| Active | Pages currently in use by apps |
| Wired | Kernel/OS pages that cannot be swapped |
| Compressed | Pages compressed by macOS memory compressor |
| Inactive | Reclaimable cached pages |
| Free | Immediately available pages |

**Pressure labels:** Normal ✅ (< 60%) · Moderate 🟡 (60–80%) · High pressure 🔴 (> 80%)

---

### 💿 Disk ( / )
| Field | What it shows |
|---|---|
| Usage | % used with bar |
| Total / Used / Free | Disk space in GB |
| I/O (now) | Current transfers/sec and MB/sec from `iostat` |
| Read / Write (lifetime) | Total GB read/written since boot (psutil) |

---

### 🌐 Network
| Field | What it shows |
|---|---|
| IPv4 | Local IP address (en0) |
| IPv6 | IPv6 address |
| Public IP | Your public internet-facing IP (fetched from ipify.org) |
| Wi-Fi SSID | Connected Wi-Fi network name |
| Wi-Fi Channel | Channel and band (e.g. 52, 5GHz, 80MHz) |
| Signal/Noise | Wi-Fi signal quality in dBm |
| TX Rate | Wi-Fi link speed in Mbps |
| **RX / TX (since boot)** | Total GB received and sent since last restart |
| Per-interface | Breakdown by en0, en1 etc. (psutil) |

---

### ⚙️ Power Management
| Field | What it shows |
|---|---|
| Power Source | AC Power or Battery Power |
| Sleep Timer | Minutes until display/system sleeps (0 = disabled) |
| Disk Sleep | Disk spin-down timer |
| Half-dim | Whether display dims at 50% before sleep |
| Lid Wake | Whether opening lid wakes the Mac |
| Sleep prevented | Whether any app or process is blocking sleep |
| Low Power Mode | On/Off |

---

## 📁 Directory Structure

```
battery-info/
├── README.md                  ← you are here (full docs)
├── run.sh                     ← bootstrap: check Python, install deps, run report
├── requirements.txt           ← pip dependencies (psutil>=5.9.0)
├── scripts/
│   └── battery_info.py        ← the report script (560+ lines, no required deps)
└── docs/
    └── sample-output.md       ← example terminal output with field reference
```

---

## 📋 Requirements

| Requirement | Version | Notes |
|---|---|---|
| macOS | 12 Monterey+ | Tested on macOS 15 Sequoia |
| Python | 3.8+ | Pre-installed on macOS |
| psutil (pip) | 5.9.0+ | **Optional** — auto-installed by `run.sh` |
| Internet | — | Required only for `run.sh` and Public IP lookup |

---

## 🔒 Privacy

- No data is sent anywhere (except one `curl` to `api.ipify.org` for public IP — remove it if not wanted)
- All battery and hardware data is read from local macOS registers
- `run.sh` downloads `battery_info.py` from this repo only
