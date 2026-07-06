# Sample Output — Mac System & Battery Report

> **Generated on:** MacBook Air (M1, 16 GB, macOS 15.5 Sequoia)  
> Output is 14 sections. Run time ≈ 15–20 seconds (dominated by `top -l 1`, `system_profiler`, and the `curl` public IP lookup).

---

```
╔══════════════════════════════════════════════════════════════════╗
║     🍎  Mac System & Battery Report  ·  2026-07-06 15:47:19     ║
╚══════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🖥️   MACHINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Model           : MacBook Air  (MacBookAir10,1)  [Z12400095HN/A]
  Chip            : Apple M1  [arm64]
  CPU Cores       : 8 physical · 8 logical
  RAM             : 16 GB
  Serial          : FVFKW2SV1WG7
  macOS           : 15.5 Sequoia  (build 24F74)
  Hostname        : Taruns-MacBook-Air.local
  Python          : 3.14.5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎮  GPU & DISPLAY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  GPU             : Apple M1  (7-core GPU)
  Metal           : Metal 3
  Display Type    : Built-In Retina LCD
  Resolution      : 2560 x 1600 Retina
  Connection      : Internal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔌  CHARGER / ADAPTER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Connected       : No ❌  (running on internal battery)
  Last known      : —

  [When charger is connected, this section shows:]
  Connected       : Yes ✅
  Name            : 70W USB-C Power Adapter
  Manufacturer    : Apple Inc.
  Model ID        : 0x701C
  Serial          : F16H6R008TK0000450
  Firmware        : 01030030  (HW rev: 1.0)
  Adapter Rating  : 68 W  (rated max)
  Negotiated PD   : 20 V × 3.4 A = 68 W  (USB-C PD profile 3)
  Wall Draw Now   : 22.99 W  (20.42 V × 1.126 A)
  Adapter Usage   : [███████░░░░░░░░░░░░░] 34%  ⬜
  Headroom Left   : 45.0 W  (unused capacity)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚡  POWER FLOW  (real-time, from PMU telemetry)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Power Source    : Battery Power
  System Load     : 1.78 W  ← CPU + GPU + peripherals
  Battery Out     : 1.78 W  ← draining from pack
  ─────────────────────────────────────────────────────────────────
  Drain rate      : 0.143 A × 12.421 V = 1.78 W

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔋  BATTERY — STATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Level           : [███████████████████████░] 95%  🟢
  Status          : Discharging 🔋
  Time Remaining  : 18h 31m
  Battery Voltage : 12.421 V  (pack)
  Current Now     : 0.143 A  (-, discharging)
  Pack Power      : 1.78 W  (draining from pack)
  Low Power Mode  : On 🔋
  Today Range     : 14% – 96%  (min/max SOC today)
  Cell Voltages   : Cell1: 4.142V  Cell2: 4.143V  Cell3: 4.136V  (pack sum: 12.421 V)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔋  BATTERY — HEALTH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Health          : [███████████████████░░░░░] 81%  🟢  →  Good 🟢
  Max Capacity    : 3,555 mAh  ←  design was 4,382 mAh  (lost 827 mAh)
  Nominal Cap     : 3,685 mAh
  Current Charge  : 3,351 mAh  (94% of max)
  Qmax (cells)    : 3939 mAh, 3951 mAh, 3901 mAh
  Cycle Count     : [████████░░░░░░░░░░░░] 42%  🟢
                    415 used  /  1000 rated  (~585 remaining)
  Battery Serial  : F5D32260BUCPJYVAT
  Peak V ever     : 13.036 V  |  Low V ever : 8.986 V
  Peak charge I   : 3.329 A  (lifetime max)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🌡️   THERMAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Battery Temp    : 31.0 °C  (right now)
  Lifetime Avg    : 28.8 °C
  Lifetime Min    : 14.5 °C
  Lifetime Max    : 45.0 °C
  Thermally ltd   : 0 s  (total charging time throttled by heat)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🏃  RUNTIME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Uptime          : 38d 19h 32m
  Total Op. Hours : 26,425 h  (cumulative lifetime battery active hours)
  Load Avg        : 2.00  2.47  2.40  (1m · 5m · 15m)
  Processes       : 674 running

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚙️   CPU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Usage           : [██████░░░░░░░░░░░░░░░░░░] 24%  🟢
  User            : 10.0%
  System          : 14.2%
  Idle            : 75.8%
  Frequency       : 3,204 MHz
  Per-Core        : C0: 16%  C1: 14%  C2: 19%  C3: 10%  C4: 29%  C5: 5%  C6: 10%  C7: 10%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📋  TOP PROCESSES  (by CPU usage)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PID       CPU%   MEM%  Process
  ───────  ─────  ─────  ───────────────────────────────────
  700       28.4    0.6  WindowServer
  557       14.8    1.1  Google Chrome Helper
  11115     12.9    4.2  Cursor Helper
  11109      8.8    0.6  Cursor Helper
  4593       2.3    0.2  duetexpertd

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💾  MEMORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Usage           : [█████████████████░░░░░░░] 72%  🟡  →  Moderate 🟡
  Total           : 16.0 GB
  Active          : 3.97 GB  (in use by apps)
  Wired           : 2.14 GB  (kernel, locked)
  Compressed      : 5.33 GB  (swapped via compressor)
  Inactive        : 3.93 GB  (reclaimable)
  Free            : 0.08 GB
  Swap            : 2.48 GB used / 4.00 GB total (encrypted)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💿  DISK  ( / )
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Storage         : APPLE SSD AP0256Q  (251 GB)
  Usage           : [█████████████████░░░░░░░] 72%  🟡
  Container Total : 245.1 GB  (physical SSD size)
  System Volume   : 11.2 GB  (macOS system files, read-only)
  Data Volume     : 154.2 GB  (apps, user files, documents)
  Container Free  : 67.1 GB  (available for new data)
  I/O (now)       : 2 tps · 0.02 MB/s  (disk0)
  Read (lifetime) : 2830.31 GB  |  Write: 1413.61 GB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🌐  NETWORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  IPv4  (en0)     : 192.168.1.56
  IPv6            : 2406:b400:75:218e:c19:286c:8474:b55c
  Public IP       : 183.82.xxx.xxx
  Wi-Fi SSID      : Not connected
  RX (since boot) : 301.63 GB
  TX (since boot) : 184.25 GB
  en0             : ↓ 0.33 GB  ↑ 0.85 GB

  [When Wi-Fi is connected, three extra lines appear:]
  Wi-Fi Channel   : 6 (2.4GHz, 20MHz)
  Signal/Noise    : -55 dBm / -95 dBm
  TX Rate         : 195.0 Mbps

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚙️   POWER MANAGEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Power Source    : Battery Power
  Sleep Timer     : 1 min
  Disk Sleep      : 10 min
  Half-dim        : disabled
  Lid Wake        : disabled
  Sleep prevented : Yes (assertion active)
  Low Power Mode  : On 🔋
```

---

## Field Glossary

### Machine
| Field | Meaning |
|-------|---------|
| Model | Full Apple marketing name |
| Model Identifier | Internal board ID (e.g. `MacBookAir10,1`) |
| Model Number | SKU/order number |
| Chip | SoC or CPU name + architecture |
| CPU Cores | Physical cores (efficiency + performance) |
| macOS | Version number, codename, and build |
| Python | Version of Python running the script |

### GPU & Display
| Field | Meaning |
|-------|---------|
| GPU | Integrated GPU name and core count |
| Metal | Metal API version (Apple's GPU compute API) |
| Display Type | Panel technology (LCD, OLED, etc.) |
| Resolution | Native pixel resolution |
| Connection | How display connects to GPU (Internal / DisplayPort / etc.) |

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
| Cell Voltages | Per-cell voltage; sum = pack voltage |
| Not charging reason 128 | macOS battery management optimized charging (normal) |

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
| Thermally ltd | Total seconds where charging was slowed due to heat (lifetime counter) |

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

### Top Processes
| Field | Meaning |
|-------|---------|
| CPU% | CPU utilisation of that process right now |
| MEM% | Percentage of total RAM used by this process |
| Process | Shortened binary name (full path stripped) |

### Memory
| Field | Meaning |
|-------|---------|
| Active | RAM in use by foreground applications |
| Wired | RAM locked by the kernel (cannot be swapped) |
| Compressed | Pages Apple's memory compressor has squashed; still in RAM, not on disk |
| Inactive | Pages not recently used; reclaimed first when RAM is needed |
| Swap | Overflow pages written to SSD (`sysctl vm.swapusage`); always encrypted on Apple Silicon |

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
| IPv4 / IPv6 | Local network address on the primary interface |
| Public IP | Your external/WAN IP fetched from `api.ipify.org` |
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
