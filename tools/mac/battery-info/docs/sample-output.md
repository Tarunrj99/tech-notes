# 📋 Sample Output — Mac Battery & System Info

This is a real terminal output captured from a **MacBook Air (Apple M1, 16 GB)** running **macOS 15.5 Sequoia**, plugged into a **70W USB-C charger**, battery at **80%** and actively charging.

```
╔══════════════════════════════════════════════════════════════════╗
║        🍎  Mac System & Battery Report  ·  2026-07-06 14:44:09        ║
╚══════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🖥️   MACHINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Model           : MacBook Air
  Chip            : Apple M1  [arm64]
  CPU Cores       : 8 physical · 8 logical
  RAM             : 16 GB
  Serial          : FVFKW2SV1WG7
  macOS           : 15.5  (build 24F74)
  Hostname        : Taruns-MacBook-Air.local

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔌  CHARGER / ADAPTER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Name            : 70W USB-C Power Adapter
  Manufacturer    : Apple Inc.
  Model ID        : 0x701C
  Serial          : F16H6R008TK0000450
  Firmware        : 01030030  (HW: 1.0)
  Rated Power     : 68 W
  Max Voltage     : 20.00 V
  Max Current     : 3.40 A
  Protocol        : USB-C PD (auto-negotiated)
  Connected       : Yes ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚡  POWER FLOW  (real-time)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Power Source    : AC Power
  Wall Input      : 28.42 W  (20.37 V × 1.395 A)
  System Receives : 28.44 W
  System Load     : 7.81 W
  Battery Power   : 20.64 W  (charging)
  Adapter Loss    : 0.68 W  (efficiency overhead)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔋  BATTERY — STATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Level           : 80%  (81% via pmset)
  Status          : Charging ⚡
  Time to Full    : 55m
  Charging Speed  : 1.66 A @ 4.28 V  →  7.09 W
  Battery Voltage : 12.560 V
  Instantaneous I : 1.643 A  (20.64 W)
  Today Min/Max   : 14% – 73%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔋  BATTERY — HEALTH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Health          : 80.6%  →  Good 🟢
  Max Capacity    : 3533 mAh  (design: 4382 mAh)
  Nominal Cap     : 3663 mAh
  Current Charge  : 2818 mAh
  Cycle Count     : 415  /  1000  (41.5% used)
  Cycles Left     : ~585
  Battery Serial  : F5D32260BUCPJYVAT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🌡️   THERMAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Battery Temp    : 31.1 °C  (now)
  Lifetime Avg    : 28.8 °C
  Lifetime Min    : 14.5 °C
  Lifetime Max    : 45.0 °C

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🏃  RUNTIME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Uptime          : 38d 18h 30m
  Total Op. Hours : 26,425 h  (lifetime battery usage)
  Load Avg        : 1.87  3.15  3.63  (1m · 5m · 15m)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💾  MEMORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total           : 16.0 GB
  Active          : 4.43 GB
  Wired           : 2.22 GB
  Compressed      : 3.92 GB
  Inactive        : 4.39 GB
  Free            : 0.47 GB
  Pressure        : 97% (High 🔴)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💿  DISK  ( / )
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total           : 228 GB
  Used            : 10 GB  (15%)
  Free            : 62 GB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚙️   POWER MANAGEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Sleep (idle)    : disabled
  Max Charge Ever : 3.33 A  (lifetime peak)
```

---

## Field Reference

### 🔋 Battery Health %

Calculated as: `(AppleRawMaxCapacity / DesignCapacity) × 100`

| Range     | Label     |
|-----------|-----------|
| ≥ 90%     | Excellent ✅ |
| 80–89%    | Good 🟢   |
| 70–79%    | Fair 🟡   |
| 60–69%    | Degraded 🟠 |
| < 60%     | Poor 🔴   |

### ⚡ Power Flow Explained

```
Wall outlet
   │
   ▼  Wall Input  (SystemVoltageIn × SystemCurrentIn)
[Adapter]
   │
   ▼  System Receives  (SystemPowerIn from telemetry)
[Mac power plane]
   ├──► System Load   (CPU + GPU + peripherals)
   └──► Battery Power (goes to battery when charging)
```

### 🌡️ Temperature Units

Battery temperature comes from `ioreg` in units of **1/100 °C** (e.g. `3113` → `31.13 °C`).  
Lifetime stats are stored in **1/10 °C** (e.g. `288` → `28.8 °C`).

### 🏃 Total Operating Hours

Sourced from `BatteryData.LifetimeData.TotalOperatingTime` inside `ioreg`. This counts cumulative hours the battery has been active (not just uptime).
