# 🔋 Mac Battery & System Info

A single-file Python script that prints a rich, real-time report of your Mac's battery health, charging state, power flow, thermals, memory, disk, and hardware — all in one terminal output.

**macOS only** (Apple Silicon + Intel). No third-party dependencies; uses only `ioreg`, `system_profiler`, `sysctl`, `pmset`, and `vm_stat`.

---

## 📦 Repository

| Field   | Value                                                                                                                                   |
|---------|-----------------------------------------------------------------------------------------------------------------------------------------|
| Raw URL | `https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/scripts/battery_info.py`                          |
| Repo    | `https://github.com/Tarunrj99/tech-notes/tree/main/tools/mac/battery-info`                                                             |

---

## ⚡ Single-Command Run (fetch & execute from GitHub)

```bash
curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/scripts/battery_info.py | python3
```

> No installation needed. Downloads and runs the script in one step.

---

## 🖥️ Local Run

```bash
python3 tools/mac/battery-info/scripts/battery_info.py
```

Or after cloning:

```bash
git clone https://github.com/Tarunrj99/tech-notes.git
cd tech-notes
python3 tools/mac/battery-info/scripts/battery_info.py
```

---

## 📊 What It Reports

The report is divided into 9 sections:

| Section             | Key Data Points                                                                 |
|---------------------|---------------------------------------------------------------------------------|
| 🖥️ Machine          | Model, Chip (M1/M2/Intel), CPU cores, RAM, Serial, macOS version               |
| 🔌 Charger/Adapter  | Name, manufacturer, serial, firmware, rated watts, max voltage/current          |
| ⚡ Power Flow        | Wall input W, system load W, battery charge W, adapter efficiency loss          |
| 🔋 Battery State    | Level %, status, time to full/empty, charging speed, today's min/max %          |
| 🔋 Battery Health   | Health %, max capacity vs design capacity (mAh), cycle count, cycles remaining  |
| 🌡️ Thermal          | Battery temperature now + lifetime avg/min/max                                  |
| 🏃 Runtime          | Uptime, lifetime operating hours, load averages (1m/5m/15m)                    |
| 💾 Memory           | Total, active, wired, compressed, inactive, free, memory pressure label         |
| 💿 Disk             | Total, used, free for `/`                                                       |
| ⚙️ Power Management | Sleep idle timer, lifetime peak charge current                                  |

---

## 📁 Directory Structure

```
mac-tools/
└── battery-info/
    ├── README.md                  ← you are here
    ├── scripts/
    │   └── battery_info.py       ← the script (no dependencies)
    └── docs/
        └── sample-output.md      ← example terminal output
```

---

## 📋 Requirements

- macOS 12 Monterey or later (tested on macOS 15 Sequoia)
- Python 3.8+  (pre-installed on macOS)
- No `pip install` required

---

## 🔒 Privacy Note

The script reads only local hardware registers via macOS system tools. No data is sent anywhere. All output stays in your terminal.

---

## 📝 Sample Output

See [`docs/sample-output.md`](docs/sample-output.md) for a full example.
