# Sample Output — Mac System & Battery Report

> **Generated on:** MacBook Air (M1, 16 GB, macOS 15.5 Sequoia)  
> Output is 14 sections. Run time ≈ 15–20 seconds (dominated by `top -l 1`, `system_profiler`, and the `curl` public IP lookups).

---

```
╔══════════════════════════════════════════════════════════════════╗
║      🍎  Mac System & Battery Report  ·  2026-07-06 17:45:12     ║
║                      Created by Tarun Saini                      ║
╚══════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🖥️   MACHINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Model           : MacBook Air  (MacBookAir10,1)  [Z12400095HN/A]
  Chip            : Apple M1  [arm64]
  CPU Cores       : 8 physical · 8 logical
  RAM             : 16 GB
  Disk            : APPLE SSD AP0256Q  (251 GB)
  macOS           : 15.5 Sequoia  (build 24F74)
  Serial          : FVFKW2SV1WG7
  Hostname        : Taruns-MacBook-Air.local

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔌  CHARGER / ADAPTER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Connected       : Yes ✅
  Name            : 70W USB-C Power Adapter
  Manufacturer    : Apple Inc.
  Model ID        : 0x701C
  Serial          : F16H6R008TK0000450
  Firmware        : 01030030  (HW rev: 1.0)
  Adapter Rating  : 68 W  (rated max)
  Negotiated PD   : 20 V × 3.4 A = 68 W  (USB-C PD profile 3)
  Wall Draw Now   : 28.76 W  (20.37 V × 1.412 A)
  Adapter Usage   : [████████░░░░░░░░░░░░] 42%  ⬜
  Headroom Left   : 39.2 W  (unused capacity)

  [When charger is disconnected:]
  Connected       : No ❌  (running on internal battery)
  Last known      : —

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚡  POWER FLOW  (real-time, from PMU telemetry)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Power Source    : AC Power
  ┌─ Wall Input    : 28.76 W  ← from wall outlet
  │  Adapter Loss  : 0.69 W  ← conversion overhead
  │  System Gets   : 28.77 W  ← delivered to Mac
  ├─ System Load   : 7.75 W  ← CPU + GPU + peripherals
  └─ Battery In    : 21.02 W  ← going into battery pack
  ─────────────────────────────────────────────────────────────────
  Balance check   : 7.75 + 21.02 = 28.77 W  (should ≈ 28.76 W)

  [When discharging (no charger):]
  Power Source    : Battery Power
  System Load     : 4.90 W  ← CPU + GPU + peripherals
  Battery Out     : 4.90 W  ← draining from pack

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔋  BATTERY — STATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Level           : [█████████████████████░░░] 86%  🟢
  Status          : Charging ⚡
  Time to Full    : 41m
  Battery Voltage : 12.648 V  (pack)
  Current Now     : 1.662 A  (+, charging)
  Pack Power      : 21.02 W  (charging into pack)
  Low Power Mode  : Off
  Today Range     : 14% – 96%  (min/max SOC today)
  Cell Voltages   : Cell1: 4.208V  Cell2: 4.211V  Cell3: 4.228V

  [When discharging:]
  Status          : Discharging 🔋
  Time Remaining  : 7h 15m
  Current Now     : 0.291 A  (-, discharging)
  Pack Power      : 4.90 W  (draining from pack)
  Low Power Mode  : On 🔋

  [When macOS Optimised Battery Charging is active:]
  ℹ️ Not charging: Optimized Battery Charging active  (normal — macOS manages charge timing)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🩺  BATTERY — HEALTH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Health          : [███████████████████░░░░░] 81%  🟢  (Good)
  Max Capacity    : 3,538 mAh  ←  design was 4,382 mAh  (lost 844 mAh)
  Nominal Cap     : 3,668 mAh
  Current Charge  : 3,013 mAh
  Qmax (cells)    : 3939 mAh, 3951 mAh, 3901 mAh
  Cycle Count     : [████████░░░░░░░░░░░░] 42%  🟢
                    416 used  /  1000 rated  (~584 remaining)
  Battery Serial  : F5D32260BUCPJYVAT
  Peak V ever     : 13.036 V  |  Low V ever : 8.986 V
  Peak charge I   : 3.329 A  (lifetime max)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🌡️   THERMAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Battery Temp    : 31.1 °C  (right now)
  Lifetime Avg    : 28.8 °C
  Lifetime Min    : 14.5 °C
  Lifetime Max    : 45.0 °C
  Thermally ltd   : None  (never throttled)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🏃  RUNTIME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Uptime          : 38d 21h 27m
  Total Op. Hours : 26,449 h  (cumulative lifetime battery active hours)
  Load Avg        : 3.38  4.73  7.36  (1m · 5m · 15m)
  Processes       : 511 running

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚙️   CPU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Usage           : [████████░░░░░░░░░░░░░░░░] 34%  🟢
  User            : 12.5%
  System          : 21.6%
  Idle            : 65.9%
  Frequency       : 3,204 MHz
  Per-Core        : C0: 38%  C1: 30%  C2: 30%  C3: 25%  C4: 33%  C5: 15%  C6: 5%  C7: 24%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎮  GPU & DISPLAY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  GPU             : Apple M1  (7-core GPU)
  Metal           : Metal 3
  Display Type    : Built-In Retina LCD
  Resolution      : 2560 x 1600 Retina
  Connection      : Internal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💾  MEMORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Usage           : [█████████████████░░░░░░░] 73%  🟡  (Moderate)
  Total           : 16.0 GB
  Active          : 3.75 GB  (in use by apps)
  Wired           : 2.43 GB  (kernel, locked)
  Compressed      : 5.48 GB  (swapped via compressor)
  Inactive        : 3.68 GB  (reclaimable)
  Free            : 0.11 GB
  Swap            : 2.38 GB used / 4.00 GB total (encrypted)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📋  TOP PROCESSES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ── By CPU ───────────────────────────────────────────────────────
  PID       CPU%   MEM%  Process
  ───────  ─────  ─────  ───────────────────────────────────
  18445     86.8    0.1  ApplicationsStorageExtension
  11115     86.5    4.6  Cursor Helper
  700       31.3    0.6  WindowServer
  3940      30.6    0.2  mobileassetd
  18428     28.2    0.1  StorageManagementService
  ── By Memory ────────────────────────────────────────────────────
  PID       CPU%   MEM%  Process
  ───────  ─────  ─────  ───────────────────────────────────
  11115     86.5    4.6  Cursor Helper
  5838       0.0    3.5  mediaanalysisd
  909       11.3    3.3  Google Chrome
  8360      11.2    1.6  WhatsApp
  11259      0.0    1.6  node

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💿  DISK  ( / )
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Storage         : APPLE SSD AP0256Q  (251 GB)
  Usage           : [█████████████████░░░░░░░] 72%  🟡
  Container Total : 245.1 GB  (physical SSD)
  System Volume   : 11.2 GB  (macOS system, read-only sealed snapshot)
  Data Volume     : 154.2 GB  (apps, user files, documents)
  Container Free  : 67.1 GB  (System Settings may show ~5-10 GB more — purgeable caches)
  I/O (now)       : 23 tps · 0.36 MB/s  (disk0)
  Read (lifetime) : 2849.52 GB  |  Write: 1417.46 GB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🌐  NETWORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  IPv4  (en0)     : 192.168.1.56
  Local IPv6      : 2406:b400:75:218e:c19:286c:8474:b55c
  Public IP (v4)  : 183.82.xxx.xxx
  Public IP (v6)  : 2406:b400:75:218e:xxxx:xxxx:xxxx:xxxx
  Wi-Fi SSID      : Zeyora
  Wi-Fi Channel   : 52 (5GHz, 80MHz)
  Signal/Noise    : -66 dBm / -91 dBm
  TX Rate         : 260 Mbps
  RX (since boot) : 60.42 GB
  TX (since boot) : 36.90 GB
  en0             : ↓ 60.42 GB  ↑ 36.90 GB

  [When Wi-Fi is not connected:]
  Wi-Fi SSID      : Not connected
  (Wi-Fi Channel, Signal/Noise, and TX Rate lines are hidden)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💤  POWER MANAGEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Power Source    : AC Power
  Sleep Timer     : 1 min
  Disk Sleep      : 10 min
  Half-dim        : disabled
  Lid Wake        : disabled
  Sleep prevented : Yes (assertion active)
  Low Power Mode  : Off
```

---

## Field Glossary

### Machine
| Field | Meaning |
|-------|---------|
| Model | Full Apple marketing name + internal board ID + SKU/order number |
| Chip | SoC or CPU name + architecture |
| CPU Cores | Physical cores (efficiency + performance) + logical cores |
| RAM | Total unified memory capacity |
| Disk | NVMe/SSD model and raw capacity |
| macOS | Version number, codename, and build |
| Serial | Mac hardware serial number |
| Hostname | Computer name visible on the local network |

### Charger / Adapter
| Field | Meaning |
|-------|---------|
| Negotiated PD | USB-C Power Delivery contract: voltage × current = watts the Mac agreed with the charger |
| Wall Draw Now | Actual instantaneous watts being drawn from the outlet right now |
| Adapter Usage | What fraction of the charger's PD contract is currently being used |
| Headroom Left | How much more power the charger *could* deliver if needed |

### Power Flow
| Field | Meaning |
|-------|---------|
| Wall Input | Power leaving the outlet |
| Adapter Loss | Heat/conversion loss in the charger brick |
| System Gets | Power arriving at the Mac's logic board |
| System Load | CPU + GPU + display + peripherals consumption |
| Battery In | Surplus going into charging the battery |
| Balance check | Sanity check: System Load + Battery In ≈ Wall Input |

### Battery — State
| Field | Meaning |
|-------|---------|
| Level | State of Charge (%) |
| Current Now | `+` = charging, `−` = discharging |
| Pack Power | Watts into/out-of the battery pack right now |
| Today Range | The min/max charge level touched today |
| Cell Voltages | Per-cell voltage; sum ≈ pack voltage |
| Not charging reason 128 | macOS Optimized Battery Charging active (normal behaviour) |

### Battery — Health
| Field | Meaning |
|-------|---------|
| Health % | `Max Capacity / Design Capacity` — the industry-standard SoH metric |
| Max Capacity | Measured max charge the battery can hold *now* |
| Design Capacity | Original factory capacity |
| Qmax | Per-cell Coulomb-counter estimate of true cell capacity |
| Cycle Count | Apple counts a cycle as 100% worth of discharge spread over any number of charges |

### Thermal
| Field | Meaning |
|-------|---------|
| Thermally ltd | Total seconds where charging was slowed due to heat (lifetime counter); "None" = never throttled |

### Runtime
| Field | Meaning |
|-------|---------|
| Total Op. Hours | Hours the battery has been active, ever (cumulative lifetime) |
| Load Avg | Unix 1-minute, 5-minute, 15-minute CPU load averages |
| Processes | Total number of active processes at report time |

### CPU
| Field | Meaning |
|-------|---------|
| Usage | Combined user + system CPU% |
| Per-Core | Per-core CPU% (requires `psutil`; shows all cores including efficiency cores) |
| Frequency | Current CPU clock speed (requires `psutil`) |

### GPU & Display
| Field | Meaning |
|-------|---------|
| GPU | Integrated GPU name and core count |
| Metal | Metal API version (Apple's GPU compute API) |
| Display Type | Panel technology (LCD, OLED, etc.) |
| Resolution | Native pixel resolution |
| Connection | How display connects to GPU (Internal / DisplayPort / etc.) |

### Memory
| Field | Meaning |
|-------|---------|
| Active | RAM in use by foreground applications |
| Wired | RAM locked by the kernel (cannot be swapped) |
| Compressed | Pages Apple's memory compressor has squashed; still in RAM, not on disk |
| Inactive | Pages not recently used; reclaimed first when RAM is needed |
| Swap | Overflow pages written to SSD (`sysctl vm.swapusage`); always encrypted on Apple Silicon |

### Top Processes
| Field | Meaning |
|-------|---------|
| By CPU | Top 5 processes sorted by CPU% — shows what's spiking the processor |
| By Memory | Top 5 processes sorted by MEM% — shows what's consuming the most RAM |
| CPU% | CPU utilisation of that process right now |
| MEM% | Percentage of total RAM used by this process |
| Process | Shortened binary name (full path stripped) |

### Disk
| Field | Meaning |
|-------|---------|
| Storage | Physical NVMe/SSD model number and raw capacity |
| Usage % | `(Container Total − Container Free) / Container Total` — the true utilisation |
| Container Total | Full APFS container size (matches SSD capacity minus EFI/firmware partitions) |
| System Volume | Read-only APFS snapshot containing the macOS installation |
| Data Volume | Writable APFS volume for apps, user home, and documents |
| Container Free | Space available to both volumes combined |
| I/O (now) | Real-time disk I/O from the latest 1-second `iostat` sample |
| Read/Write lifetime | Cumulative bytes transferred since last boot (via `psutil`) |

### Network
| Field | Meaning |
|-------|---------|
| IPv4 (en0) | Local network address on the primary Wi-Fi interface |
| Local IPv6 | Stable SLAAC address — used for incoming connections on the LAN |
| Public IP (v4) | External IPv4 address fetched from `api.ipify.org` |
| Public IP (v6) | Temporary privacy-extension IPv6 address fetched from `api6.ipify.org` — this matches what `whatismyip.com` shows, not the stable local address |
| Wi-Fi Channel | Channel and band only shown when actually associated to an SSID |
| Signal/Noise | RSSI signal strength vs noise floor in dBm |
| TX Rate | 802.11 PHY transmit rate negotiated with the access point |
| RX / TX since boot | Cumulative network bytes on all `en*` interfaces since boot |

### Power Management
| Field | Meaning |
|-------|---------|
| Sleep Timer | Inactivity delay before system sleep (`pmset sleep`) |
| Disk Sleep | Inactivity delay before disk spin-down (`pmset disksleep`) |
| Sleep prevented | `PreventUserIdleSystemSleep` assertion is active (e.g. a video call or download is running) |
