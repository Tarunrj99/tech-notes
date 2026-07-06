#!/usr/bin/env python3
"""
battery_info.py — Comprehensive Mac Power, Battery & System Report
Fetches real-time data from ioreg, system_profiler, sysctl, pmset, and vm_stat.
macOS only (Apple Silicon + Intel).
"""

import subprocess
import re
import sys
import os
from datetime import datetime, timedelta


# ─────────────────────────── helpers ────────────────────────────

def run(cmd, default="N/A"):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return default


def run_list(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def ioreg_int(s, pattern, default=0):
    m = re.search(pattern, s)
    return int(m.group(1)) if m else default


def ioreg_str(s, pattern, default="N/A"):
    m = re.search(pattern, s)
    return m.group(1) if m else default


def ioreg_flag(s, pattern):
    m = re.search(pattern, s)
    if not m:
        return False
    return m.group(1).strip() in ("Yes", "true", "1")


def fmt_time(minutes):
    if minutes <= 0 or minutes >= 65535:
        return "calculating…"
    h, m = divmod(int(minutes), 60)
    if h:
        return f"{h}h {m:02d}m"
    return f"{m}m"


def fmt_uptime(seconds):
    td = timedelta(seconds=int(seconds))
    days = td.days
    hours, rem = divmod(td.seconds, 3600)
    mins = rem // 60
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    parts.append(f"{mins}m")
    return " ".join(parts)


def health_label(pct):
    if pct >= 90:
        return "Excellent ✅"
    if pct >= 80:
        return "Good 🟢"
    if pct >= 70:
        return "Fair 🟡"
    if pct >= 60:
        return "Degraded 🟠"
    return "Poor 🔴"


def charge_status_label(is_charging, fully_charged, bp_mw, soc):
    if fully_charged:
        return "Full ✅"
    if is_charging:
        return "Charging ⚡"
    if bp_mw > 0:
        return "Discharging 🔋"
    return "Idle / Standby 🔌"


def mem_pressure_label(free_mb, total_mb):
    used_pct = 100 - (free_mb / total_mb * 100)
    if used_pct < 60:
        return f"{used_pct:.0f}% (Normal ✅)"
    if used_pct < 80:
        return f"{used_pct:.0f}% (Moderate 🟡)"
    return f"{used_pct:.0f}% (High 🔴)"


# ─────────────────────────── gather data ────────────────────────────

ioreg_raw = run_list(["ioreg", "-r", "-c", "AppleSmartBattery"])

# ── Battery fields ──────────────────────────────────────────────
soc          = ioreg_int(ioreg_raw, r'"StateOfCharge"\s*=\s*(\d+)')
soc_fb       = ioreg_int(ioreg_raw, r'"CurrentCapacity"\s*=\s*(\d+)')
if soc == 0:
    soc = soc_fb

raw_max_cap  = ioreg_int(ioreg_raw, r'"AppleRawMaxCapacity"\s*=\s*(\d+)')
design_cap   = ioreg_int(ioreg_raw, r'"DesignCapacity"\s*=\s*(\d+)')
nominal_cap  = ioreg_int(ioreg_raw, r'"NominalChargeCapacity"\s*=\s*(\d+)')
raw_cur_cap  = ioreg_int(ioreg_raw, r'"AppleRawCurrentCapacity"\s*=\s*(\d+)')

max_pct      = ioreg_int(ioreg_raw, r'"MaxCapacity"\s*=\s*(\d+)')
design_cycle = ioreg_int(ioreg_raw, r'"DesignCycleCount9C"\s*=\s*(\d+)', 1000)
cycle_count  = ioreg_int(ioreg_raw, r'"CycleCount"\s*=\s*(\d+)')
bat_serial   = ioreg_str(ioreg_raw, r'"Serial"\s*=\s*"([^"]+)"')

is_charging  = ioreg_flag(ioreg_raw, r'"IsCharging"\s*=\s*(Yes|No|true|false)')
fully_chgd   = ioreg_flag(ioreg_raw, r'"FullyCharged"\s*=\s*(Yes|No|true|false)')
ext_conn     = ioreg_flag(ioreg_raw, r'"ExternalConnected"\s*=\s*(Yes|No|true|false)')

time_to_full  = ioreg_int(ioreg_raw, r'"AvgTimeToFull"\s*=\s*(\d+)', 65535)
time_to_empty = ioreg_int(ioreg_raw, r'"AvgTimeToEmpty"\s*=\s*(\d+)', 65535)
time_remain   = ioreg_int(ioreg_raw, r'"TimeRemaining"\s*=\s*(\d+)', 65535)

bat_voltage_mv = ioreg_int(ioreg_raw, r'"AppleRawBatteryVoltage"\s*=\s*(\d+)')
if bat_voltage_mv == 0:
    bat_voltage_mv = ioreg_int(ioreg_raw, r'"Voltage"\s*=\s*(\d+)')

amperage_ma  = ioreg_int(ioreg_raw, r'"InstantAmperage"\s*=\s*(\d+)')
if amperage_ma == 0:
    amperage_ma = ioreg_int(ioreg_raw, r'"Amperage"\s*=\s*(\d+)')

bat_temp_raw = ioreg_int(ioreg_raw, r'"Temperature"\s*=\s*(\d+)')
bat_temp_c   = bat_temp_raw / 100.0

not_charging_reason = ioreg_int(ioreg_raw, r'"NotChargingReason"\s*=\s*(\d+)')
charging_voltage_mv = ioreg_int(ioreg_raw, r'"ChargingVoltage"\s*=\s*(\d+)')
charging_current_ma = ioreg_int(ioreg_raw, r'"ChargingCurrent"\s*=\s*(\d+)')

# Lifetime stats from BatteryData block
total_op_time_h  = ioreg_int(ioreg_raw, r'"TotalOperatingTime"\s*=\s*(\d+)')
avg_temp_raw     = ioreg_int(ioreg_raw, r'"AverageTemperature"\s*=\s*(\d+)')
max_temp_raw     = ioreg_int(ioreg_raw, r'"MaximumTemperature"\s*=\s*(\d+)')
min_temp_raw     = ioreg_int(ioreg_raw, r'"MinimumTemperature"\s*=\s*(\d+)')
daily_max_soc    = ioreg_int(ioreg_raw, r'"DailyMaxSoc"\s*=\s*(\d+)')
daily_min_soc    = ioreg_int(ioreg_raw, r'"DailyMinSoc"\s*=\s*(\d+)')
max_charge_ever  = ioreg_int(ioreg_raw, r'"MaximumChargeCurrent"\s*=\s*(\d+)')

# ── Power telemetry ──────────────────────────────────────────────
sys_v_mv     = ioreg_int(ioreg_raw, r'"SystemVoltageIn"\s*=\s*(\d+)')
sys_i_ma     = ioreg_int(ioreg_raw, r'"SystemCurrentIn"\s*=\s*(\d+)')
sys_pw_mw    = ioreg_int(ioreg_raw, r'"SystemPowerIn"\s*=\s*(\d+)')
sys_load_mw  = ioreg_int(ioreg_raw, r'"SystemLoad"\s*=\s*(\d+)')
bat_pw_mw    = ioreg_int(ioreg_raw, r'"BatteryPower"\s*=\s*(\d+)')
eff_loss_mw  = ioreg_int(ioreg_raw, r'"AdapterEfficiencyLoss"\s*=\s*(\d+)')

if sys_pw_mw == 0 and sys_v_mv > 0 and sys_i_ma > 0:
    sys_pw_mw = sys_v_mv * sys_i_ma // 1000

# ── Adapter / charger ─────────────────────────────────────────────
adp_name     = ioreg_str(ioreg_raw, r'"Name"\s*=\s*"([^"]+)"')
adp_serial   = ioreg_str(ioreg_raw, r'"SerialString"\s*=\s*"([^"]+)"')
adp_mfg      = ioreg_str(ioreg_raw, r'"Manufacturer"\s*=\s*"([^"]+)"')
adp_model    = ioreg_str(ioreg_raw, r'"Model"\s*=\s*"([^"]+)"')
adp_fw       = ioreg_str(ioreg_raw, r'"FwVersion"\s*=\s*"([^"]+)"')
adp_hw       = ioreg_str(ioreg_raw, r'"HwVersion"\s*=\s*"([^"]+)"')
adp_watts    = ioreg_int(ioreg_raw, r'"Watts"\s*=\s*(\d+)')
adp_cur_ma   = ioreg_int(ioreg_raw, r'"Current"\s*=\s*(\d+)')
adp_volt_mv  = ioreg_int(ioreg_raw, r'"AdapterVoltage"\s*=\s*(\d+)')

# ── System / Hardware ─────────────────────────────────────────────
hw_raw   = run(["system_profiler", "SPHardwareDataType"])
model    = re.search(r"Model Name:\s*(.+)", hw_raw)
model    = model.group(1).strip() if model else "N/A"
chip     = re.search(r"Chip:\s*(.+)", hw_raw)
chip     = chip.group(1).strip() if chip else run(["sysctl", "-n", "machdep.cpu.brand_string"])
mem_str  = re.search(r"Memory:\s*(.+)", hw_raw)
mem_str  = mem_str.group(1).strip() if mem_str else "N/A"
mac_ser  = re.search(r"Serial Number.*?:\s*(\S+)", hw_raw)
mac_ser  = mac_ser.group(1).strip() if mac_ser else "N/A"

macos_ver  = run(["sw_vers", "-productVersion"])
macos_bld  = run(["sw_vers", "-buildVersion"])
hostname   = run(["hostname"])
arch       = run(["uname", "-m"])
pcpu       = run(["sysctl", "-n", "hw.physicalcpu"])
lcpu       = run(["sysctl", "-n", "hw.logicalcpu"])

# ── Uptime / load ─────────────────────────────────────────────────
uptime_raw  = run(["sysctl", "-n", "kern.boottime"])
boot_ts_m   = re.search(r"sec\s*=\s*(\d+)", uptime_raw)
if boot_ts_m:
    boot_ts  = int(boot_ts_m.group(1))
    now_ts   = int(datetime.now().timestamp())
    uptime_s = now_ts - boot_ts
    uptime_fmt = fmt_uptime(uptime_s)
else:
    uptime_fmt = run(["uptime"]).split(",")[0].split("up ")[-1].strip()

load_raw = run(["sysctl", "-n", "vm.loadavg"])
load_m   = re.findall(r"[\d.]+", load_raw)
load_str = "  ".join(load_m[:3]) if len(load_m) >= 3 else "N/A"

# ── Memory ────────────────────────────────────────────────────────
mem_bytes  = int(run(["sysctl", "-n", "hw.memsize"], "0"))
mem_total  = mem_bytes / (1024 ** 3)

vm_stat_raw = run_list(["vm_stat"])
page_size_m = re.search(r"page size of (\d+) bytes", vm_stat_raw)
page_size   = int(page_size_m.group(1)) if page_size_m else 16384

def vm_pages(label):
    m = re.search(rf"{label}:\s*([\d.]+)", vm_stat_raw)
    return int(float(m.group(1))) if m else 0

pages_free     = vm_pages("Pages free")
pages_active   = vm_pages("Pages active")
pages_inactive = vm_pages("Pages inactive")
pages_wired    = vm_pages("Pages wired down")
pages_compress = vm_pages("Pages occupied by compressor")

mem_free_gb    = pages_free * page_size / (1024 ** 3)
mem_active_gb  = pages_active * page_size / (1024 ** 3)
mem_inactive_gb = pages_inactive * page_size / (1024 ** 3)
mem_wired_gb   = pages_wired * page_size / (1024 ** 3)
mem_compress_gb = pages_compress * page_size / (1024 ** 3)
mem_used_gb    = mem_active_gb + mem_wired_gb + mem_compress_gb

# ── Disk ──────────────────────────────────────────────────────────
disk_raw = run(["df", "-g", "/"])
disk_m   = re.search(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)%", disk_raw)
if disk_m:
    disk_total = int(disk_m.group(1))
    disk_used  = int(disk_m.group(2))
    disk_free  = int(disk_m.group(3))
    disk_pct   = int(disk_m.group(4))
else:
    disk_total = disk_used = disk_free = disk_pct = 0

# ── pmset ─────────────────────────────────────────────────────────
pmset_raw         = run_list(["pmset", "-g", "batt"])
pmset_source_m    = re.search(r"Now drawing from '(.+)'", pmset_raw)
pmset_source      = pmset_source_m.group(1) if pmset_source_m else "Unknown"
pmset_pct_m       = re.search(r"(\d+)%;", pmset_raw)
pmset_pct         = int(pmset_pct_m.group(1)) if pmset_pct_m else soc

pmset_ps          = run_list(["pmset", "-g", "ps"])
sleep_m           = re.search(r"sleep\s+(\d+)", run_list(["pmset", "-g"]))
sleep_min         = int(sleep_m.group(1)) if sleep_m else 0

# ── Derived calculations ──────────────────────────────────────────
health_pct    = (raw_max_cap / design_cap * 100) if design_cap else 0
bat_power_w   = amperage_ma * bat_voltage_mv / 1_000_000
cycles_remain = max(0, design_cycle - cycle_count)
cycle_pct_used = (cycle_count / design_cycle * 100) if design_cycle else 0

sys_pw_w    = sys_pw_mw / 1000
sys_load_w  = sys_load_mw / 1000
bat_pw_w    = bat_pw_mw / 1000
eff_loss_w  = eff_loss_mw / 1000
adp_in_w    = sys_v_mv * sys_i_ma / 1_000_000

char_status = charge_status_label(is_charging, fully_chgd, bat_pw_mw, soc)

now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ─────────────────────────── render ────────────────────────────

print(f"""
╔══════════════════════════════════════════════════════════════════╗
║        🍎  Mac System & Battery Report  ·  {now_str}        ║
╚══════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🖥️   MACHINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Model           : {model}
  Chip            : {chip}  [{arch}]
  CPU Cores       : {pcpu} physical · {lcpu} logical
  RAM             : {mem_str}
  Serial          : {mac_ser}
  macOS           : {macos_ver}  (build {macos_bld})
  Hostname        : {hostname}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔌  CHARGER / ADAPTER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Name            : {adp_name.strip()}
  Manufacturer    : {adp_mfg}
  Model ID        : {adp_model}
  Serial          : {adp_serial}
  Firmware        : {adp_fw}  (HW: {adp_hw})
  Rated Power     : {adp_watts} W
  Max Voltage     : {adp_volt_mv/1000:.2f} V
  Max Current     : {adp_cur_ma/1000:.2f} A
  Protocol        : USB-C PD (auto-negotiated)
  Connected       : {"Yes ✅" if ext_conn else "No ❌"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚡  POWER FLOW  (real-time)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Power Source    : {pmset_source}
  Wall Input      : {adp_in_w:.2f} W  ({sys_v_mv/1000:.2f} V × {sys_i_ma/1000:.3f} A)
  System Receives : {sys_pw_w:.2f} W
  System Load     : {sys_load_w:.2f} W
  Battery Power   : {bat_pw_w:.2f} W  ({"charging" if is_charging else "discharging"})
  Adapter Loss    : {eff_loss_w:.2f} W  (efficiency overhead)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔋  BATTERY — STATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Level           : {soc}%  ({pmset_pct}% via pmset)
  Status          : {char_status}
  {"Time to Full   : " + fmt_time(time_to_full) if is_charging else "Time Remaining : " + fmt_time(time_to_empty)}
  Charging Speed  : {charging_current_ma/1000:.2f} A @ {charging_voltage_mv/1000:.2f} V  →  {charging_current_ma*charging_voltage_mv/1_000_000:.2f} W
  Battery Voltage : {bat_voltage_mv/1000:.3f} V
  Instantaneous I : {amperage_ma/1000:.3f} A  ({bat_power_w:.2f} W)
  Today Min/Max   : {daily_min_soc}% – {daily_max_soc}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔋  BATTERY — HEALTH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Health          : {health_pct:.1f}%  →  {health_label(health_pct)}
  Max Capacity    : {raw_max_cap} mAh  (design: {design_cap} mAh)
  Nominal Cap     : {nominal_cap} mAh
  Current Charge  : {raw_cur_cap} mAh
  Cycle Count     : {cycle_count}  /  {design_cycle}  ({cycle_pct_used:.1f}% used)
  Cycles Left     : ~{cycles_remain}
  Battery Serial  : {bat_serial}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🌡️   THERMAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Battery Temp    : {bat_temp_c:.1f} °C  (now)
  Lifetime Avg    : {avg_temp_raw/10:.1f} °C
  Lifetime Min    : {min_temp_raw/10:.1f} °C
  Lifetime Max    : {max_temp_raw/10:.1f} °C

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🏃  RUNTIME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Uptime          : {uptime_fmt}
  Total Op. Hours : {total_op_time_h:,} h  (lifetime battery usage)
  Load Avg        : {load_str}  (1m · 5m · 15m)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💾  MEMORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total           : {mem_total:.1f} GB
  Active          : {mem_active_gb:.2f} GB
  Wired           : {mem_wired_gb:.2f} GB
  Compressed      : {mem_compress_gb:.2f} GB
  Inactive        : {mem_inactive_gb:.2f} GB
  Free            : {mem_free_gb:.2f} GB
  Pressure        : {mem_pressure_label(mem_free_gb * 1024, mem_total * 1024)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💿  DISK  ( / )
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total           : {disk_total} GB
  Used            : {disk_used} GB  ({disk_pct}%)
  Free            : {disk_free} GB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚙️   POWER MANAGEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Sleep (idle)    : {sleep_min if sleep_min else "disabled"}{" min" if sleep_min else ""}
  Max Charge Ever : {max_charge_ever/1000:.2f} A  (lifetime peak)
""")
