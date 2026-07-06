#!/usr/bin/env python3
"""
battery_info.py — Comprehensive Mac Power, Battery & System Report

Data sources:
  - ioreg (AppleSmartBattery)   : battery, adapter, power telemetry
  - system_profiler             : hardware, GPU/display, storage model
  - sysctl                      : CPU cores, memory, boot time, load, swap
  - pmset                       : power source, sleep settings, assertions
  - vm_stat                     : memory pages breakdown
  - top / ps                    : real-time CPU usage, top processes
  - diskutil                    : accurate APFS container disk space
  - networksetup / scutil       : WiFi SSID, IP addresses
  - netstat                     : network I/O bytes per interface
  - iostat                      : real-time disk I/O (tps, throughput)
  - psutil (optional, pip)      : CPU per-core %, enhanced I/O counters

macOS only (Apple Silicon + Intel). Core features work with no pip packages.
psutil adds per-core CPU % and richer I/O stats — auto-installed by run.sh.

Usage:
  python3 battery_info.py                          # print to terminal
  python3 battery_info.py --export                 # save to ~/Desktop/battery-report-<timestamp>.txt
  python3 battery_info.py --export /path/file.txt  # save to custom path

One-liner (fetch + auto-install deps + run):
  curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/run.sh | bash
"""

import subprocess, re, sys, os
from datetime import datetime, timedelta

# ── Optional: psutil for enhanced CPU / I/O stats ──────────────────────────
try:
    import psutil as _psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


# ───────────────────────────── CLI args ────────────────────────────────────────

_args      = sys.argv[1:]
_do_export = "--export" in _args
_export_path = None
if _do_export:
    idx = _args.index("--export")
    if idx + 1 < len(_args) and not _args[idx + 1].startswith("--"):
        _export_path = _args[idx + 1]
    else:
        ts = datetime.now().strftime("%Y-%m-%d-%H-%M")
        _export_path = os.path.expanduser(f"~/Desktop/battery-report-{ts}.txt")


# ───────────────────────────── helpers ─────────────────────────────────────────

def run(cmd, default="N/A"):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return default


def ioreg_int(s, pattern, default=0):
    m = re.search(pattern, s)
    return int(m.group(1)) if m else default


def ioreg_str(s, pattern, default="N/A"):
    m = re.search(pattern, s)
    return m.group(1) if m else default


def ioreg_flag(s, pattern):
    m = re.search(pattern, s)
    return m.group(1).strip() in ("Yes", "true", "1") if m else False


def signed64(val):
    """Two's complement: convert ioreg unsigned uint64 → signed Python int."""
    return val - (1 << 64) if val >= (1 << 63) else val


def fmt_time(minutes):
    if minutes <= 0 or minutes >= 65535:
        return "calculating…"
    h, m = divmod(int(minutes), 60)
    return f"{h}h {m:02d}m" if h else f"{m}m"


def fmt_uptime(boot_ts):
    td = timedelta(seconds=int(datetime.now().timestamp()) - int(boot_ts))
    d, rem = td.days, td.seconds
    h, m   = divmod(rem, 3600)
    return f"{d}d {h}h {m // 60:02d}m"


def bar(pct, width=24, reverse=False, neutral=False):
    """Render a Unicode progress bar.
    reverse=True  → high % is bad  (disk used, adapter load, cycles used)
    neutral=True  → no colour judgement (just a progress indicator)
    """
    pct  = max(0, min(100, pct))
    full = round(pct / 100 * width)
    if neutral:
        color = "⬜"
    elif reverse:
        color = "🔴" if pct >= 80 else "🟡" if pct >= 50 else "🟢"
    else:
        color = "🟢" if pct >= 80 else "🟡" if pct >= 50 else "🔴"
    return f"[{'█' * full}{'░' * (width - full)}] {pct:.0f}%  {color}"


def health_label(pct):
    if pct >= 90: return "Excellent ✅"
    if pct >= 80: return "Good 🟢"
    if pct >= 70: return "Fair 🟡"
    if pct >= 60: return "Degraded 🟠"
    return "Poor 🔴"


def mem_label(used_pct):
    if used_pct < 60: return "Normal ✅"
    if used_pct < 80: return "Moderate 🟡"
    return "High pressure 🔴"


def strip_ansi(text):
    """Remove ANSI color/format escape sequences for clean file export."""
    return re.sub(r'\x1b\[[0-9;]*[mGKHF]', '', text)


def shorten_proc(path):
    """Return a short human-readable process name from a full binary path."""
    name = os.path.basename(path)
    # Strip common macOS helper suffixes for readability
    name = re.sub(r'\s*\(.*\)$', '', name)
    if len(name) > 35:
        name = name[:32] + "…"
    return name


# ───────────────────────────── gather data ─────────────────────────────────────

ioreg_raw = run(["ioreg", "-r", "-c", "AppleSmartBattery"])

# ── Battery ─────────────────────────────────────────────────────────
soc          = ioreg_int(ioreg_raw, r'"StateOfCharge"\s*=\s*(\d+)')
if soc == 0:
    soc      = ioreg_int(ioreg_raw, r'"CurrentCapacity"\s*=\s*(\d+)')

raw_max_cap  = ioreg_int(ioreg_raw, r'"AppleRawMaxCapacity"\s*=\s*(\d+)')
design_cap   = ioreg_int(ioreg_raw, r'"DesignCapacity"\s*=\s*(\d+)')
nominal_cap  = ioreg_int(ioreg_raw, r'"NominalChargeCapacity"\s*=\s*(\d+)')
raw_cur_cap  = ioreg_int(ioreg_raw, r'"AppleRawCurrentCapacity"\s*=\s*(\d+)')
design_cycle = ioreg_int(ioreg_raw, r'"DesignCycleCount9C"\s*=\s*(\d+)', 1000)
cycle_count  = ioreg_int(ioreg_raw, r'"CycleCount"\s*=\s*(\d+)')
bat_serial   = ioreg_str(ioreg_raw, r'"Serial"\s*=\s*"([^"]+)"')

is_charging  = ioreg_flag(ioreg_raw, r'"IsCharging"\s*=\s*(Yes|No|true|false)')
fully_chgd   = ioreg_flag(ioreg_raw, r'"FullyCharged"\s*=\s*(Yes|No|true|false)')
ext_conn     = ioreg_flag(ioreg_raw, r'"ExternalConnected"\s*=\s*(Yes|No|true|false)')

time_to_full  = ioreg_int(ioreg_raw, r'"AvgTimeToFull"\s*=\s*(\d+)',  65535)
time_to_empty = ioreg_int(ioreg_raw, r'"AvgTimeToEmpty"\s*=\s*(\d+)', 65535)

bat_volt_mv  = ioreg_int(ioreg_raw, r'"AppleRawBatteryVoltage"\s*=\s*(\d+)')
if bat_volt_mv == 0:
    bat_volt_mv = ioreg_int(ioreg_raw, r'"Voltage"\s*=\s*(\d+)')

# Amperage: signed (+ = charging, - = discharging). ioreg returns uint64.
_amp_raw     = ioreg_int(ioreg_raw, r'"InstantAmperage"\s*=\s*(\d+)')
if _amp_raw == 0:
    _amp_raw = ioreg_int(ioreg_raw, r'"Amperage"\s*=\s*(\d+)')
amp_ma       = signed64(_amp_raw)          # signed mA
amp_abs_ma   = abs(amp_ma)

bat_temp_c   = ioreg_int(ioreg_raw, r'"Temperature"\s*=\s*(\d+)') / 100.0

# Cell voltages (3 cells in series for 12V pack)
cell_v       = re.search(r'"CellVoltage"\s*=\s*\(([^)]+)\)', ioreg_raw)
cell_volts   = [int(v.strip()) for v in cell_v.group(1).split(",")] if cell_v else []

# Qmax (true measured capacity per cell from coulomb counting)
qmax_v       = re.search(r'"Qmax"\s*=\s*\(([^)]+)\)', ioreg_raw)
qmax_vals    = [int(v.strip()) for v in qmax_v.group(1).split(",")] if qmax_v else []

# ChargerData (cell-level — NOT used for pack power calculation)
chg_inhibit  = ioreg_int(ioreg_raw, r'"ChargerInhibitReason"\s*=\s*(\d+)')
not_chg_rsn  = ioreg_int(ioreg_raw, r'"NotChargingReason"\s*=\s*(\d+)')
slow_chg_rsn = ioreg_int(ioreg_raw, r'"SlowChargingReason"\s*=\s*(\d+)')
chg_therml_s = ioreg_int(ioreg_raw, r'"TimeChargingThermallyLimited"\s*=\s*(\d+)')

# Lifetime stats
total_op_h   = ioreg_int(ioreg_raw, r'"TotalOperatingTime"\s*=\s*(\d+)')
avg_temp_raw = ioreg_int(ioreg_raw, r'"AverageTemperature"\s*=\s*(\d+)')
max_temp_raw = ioreg_int(ioreg_raw, r'"MaximumTemperature"\s*=\s*(\d+)')
min_temp_raw = ioreg_int(ioreg_raw, r'"MinimumTemperature"\s*=\s*(\d+)')
daily_max    = ioreg_int(ioreg_raw, r'"DailyMaxSoc"\s*=\s*(\d+)')
daily_min    = ioreg_int(ioreg_raw, r'"DailyMinSoc"\s*=\s*(\d+)')
max_chg_ever = ioreg_int(ioreg_raw, r'"MaximumChargeCurrent"\s*=\s*(\d+)')
min_volt_ever= ioreg_int(ioreg_raw, r'"MinimumPackVoltage"\s*=\s*(\d+)')
max_volt_ever= ioreg_int(ioreg_raw, r'"MaximumPackVoltage"\s*=\s*(\d+)')

# ── Power telemetry ──────────────────────────────────────────────────────────
# All values are real-time snapshots from the PMU hardware.
sys_v_mv     = ioreg_int(ioreg_raw, r'"SystemVoltageIn"\s*=\s*(\d+)')
sys_i_ma     = ioreg_int(ioreg_raw, r'"SystemCurrentIn"\s*=\s*(\d+)')
sys_pw_mw    = ioreg_int(ioreg_raw, r'"SystemPowerIn"\s*=\s*(\d+)')
sys_load_mw  = ioreg_int(ioreg_raw, r'"SystemLoad"\s*=\s*(\d+)')
eff_loss_mw  = ioreg_int(ioreg_raw, r'"AdapterEfficiencyLoss"\s*=\s*(\d+)')

# BatteryPower: signed mW. Positive → charging into battery; negative → draining.
_bp_raw      = ioreg_int(ioreg_raw, r'"BatteryPower"\s*=\s*(\d+)')
bat_pw_mw    = signed64(_bp_raw)
bat_chg_mw   = bat_pw_mw if bat_pw_mw > 0 else 0
bat_drain_mw = abs(bat_pw_mw) if bat_pw_mw < 0 else 0

# Wall input: SystemVoltageIn × SystemCurrentIn gives wall-side draw.
# SystemPowerIn is what the system actually receives (after adapter conversion).
wall_mw = sys_v_mv * sys_i_ma // 1000 if sys_v_mv and sys_i_ma else sys_pw_mw

# Battery pack power (correct): Amperage × Pack Voltage (both measured at pack terminals).
pack_pw_mw   = amp_abs_ma * bat_volt_mv // 1000

# ── Adapter / USB-C PD ───────────────────────────────────────────────────────
adp_name     = ioreg_str(ioreg_raw, r'"Name"\s*=\s*"([^"]+)"')
adp_serial   = ioreg_str(ioreg_raw, r'"SerialString"\s*=\s*"([^"]+)"')
adp_mfg      = ioreg_str(ioreg_raw, r'"Manufacturer"\s*=\s*"([^"]+)"')
adp_model    = ioreg_str(ioreg_raw, r'"Model"\s*=\s*"([^"]+)"')
adp_fw       = ioreg_str(ioreg_raw, r'"FwVersion"\s*=\s*"([^"]+)"')
adp_hw       = ioreg_str(ioreg_raw, r'"HwVersion"\s*=\s*"([^"]+)"')
adp_watts    = ioreg_int(ioreg_raw, r'"Watts"\s*=\s*(\d+)')
adp_cur_ma   = ioreg_int(ioreg_raw, r'"Current"\s*=\s*(\d+)')
adp_volt_mv  = ioreg_int(ioreg_raw, r'"AdapterVoltage"\s*=\s*(\d+)')

# PD negotiated profile: UsbHvcHvcIndex tells which entry in UsbHvcMenu is active.
pd_idx       = ioreg_int(ioreg_raw, r'"UsbHvcHvcIndex"\s*=\s*(\d+)')
pd_menus     = re.findall(r'"Index"\s*=\s*(\d+)[^}]*?"MaxCurrent"\s*=\s*(\d+)[^}]*?"MaxVoltage"\s*=\s*(\d+)', ioreg_raw)
pd_contract  = None
for (idx_s, cur_s, volt_s) in pd_menus:
    if int(idx_s) == pd_idx:
        pd_contract = (int(volt_s), int(cur_s))  # (mV, mA)
        break
if pd_contract:
    pd_neg_v, pd_neg_a = pd_contract[0] / 1000, pd_contract[1] / 1000
    pd_max_w = pd_neg_v * pd_neg_a
else:
    pd_neg_v  = adp_volt_mv / 1000
    pd_neg_a  = adp_cur_ma / 1000
    pd_max_w  = adp_watts or pd_neg_v * pd_neg_a

wall_w       = wall_mw / 1000
pd_util_pct  = (wall_w / pd_max_w * 100) if pd_max_w else 0
pd_headroom  = max(0, pd_max_w - wall_w)

# ── System / Hardware ────────────────────────────────────────────────────────
hw_raw  = run(["system_profiler", "SPHardwareDataType"])

def hw(pattern, fallback="N/A"):
    m = re.search(pattern, hw_raw)
    return m.group(1).strip() if m else fallback

model      = hw(r"Model Name:\s*(.+)")
model_id   = hw(r"Model Identifier:\s*(.+)")
model_num  = hw(r"Model Number:\s*(.+)", "")
chip       = hw(r"Chip:\s*(.+)", run(["sysctl", "-n", "machdep.cpu.brand_string"]))
mem_str    = hw(r"Memory:\s*(.+)")
mac_serial = hw(r"Serial Number.*?:\s*(\S+)")

macos_ver  = run(["sw_vers", "-productVersion"])
macos_bld  = run(["sw_vers", "-buildVersion"])
hostname   = run(["hostname"])
arch       = run(["uname", "-m"])
pcpu       = run(["sysctl", "-n", "hw.physicalcpu"])
lcpu       = run(["sysctl", "-n", "hw.logicalcpu"])

# macOS version → friendly codename
_macos_codenames = {
    "15": "Sequoia", "14": "Sonoma", "13": "Ventura",
    "12": "Monterey", "11": "Big Sur", "10.15": "Catalina",
    "10.14": "Mojave", "10.13": "High Sierra", "10.12": "Sierra",
}
_major = macos_ver.split(".")[0]
_minor_key = ".".join(macos_ver.split(".")[:2])
macos_codename = _macos_codenames.get(_major) or _macos_codenames.get(_minor_key, "")

# Python runtime version
py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

# ── GPU & Display ────────────────────────────────────────────────────────────
gpu_raw       = run(["system_profiler", "SPDisplaysDataType"])
gpu_model     = (re.search(r"Chipset Model:\s*(.+)", gpu_raw) or type('', (), {'group': lambda s, n: "N/A"})()).group(1).strip()
gpu_cores_m   = re.search(r"Total Number of Cores:\s*(\d+)", gpu_raw)
gpu_cores     = gpu_cores_m.group(1) if gpu_cores_m else "N/A"
gpu_metal     = (re.search(r"Metal Support:\s*(.+)", gpu_raw) or type('', (), {'group': lambda s, n: "N/A"})()).group(1).strip()
disp_type_m   = re.search(r"Display Type:\s*(.+)", gpu_raw)
disp_type     = disp_type_m.group(1).strip() if disp_type_m else "N/A"
disp_res_m    = re.search(r"Resolution:\s*(.+)", gpu_raw)
disp_res      = disp_res_m.group(1).strip() if disp_res_m else "N/A"
disp_conn_m   = re.search(r"Connection Type:\s*(.+)", gpu_raw)
disp_conn     = disp_conn_m.group(1).strip() if disp_conn_m else "N/A"

# ── Storage model (NVMe/SSD) ─────────────────────────────────────────────────
nvme_raw      = run(["system_profiler", "SPNVMeDataType"])
ssd_model_m   = re.search(r"Model:\s*(.+)", nvme_raw)
ssd_model     = ssd_model_m.group(1).strip() if ssd_model_m else "N/A"
ssd_cap_m     = re.search(r"Capacity:\s*([\d,.]+ [GT]B)", nvme_raw)
ssd_capacity  = ssd_cap_m.group(1).strip() if ssd_cap_m else "N/A"

# ── Uptime / load ────────────────────────────────────────────────────────────
boot_raw   = run(["sysctl", "-n", "kern.boottime"])
boot_m     = re.search(r"sec\s*=\s*(\d+)", boot_raw)
uptime_fmt = fmt_uptime(boot_m.group(1)) if boot_m else "N/A"

load_raw   = run(["sysctl", "-n", "vm.loadavg"])
load_vals  = re.findall(r"[\d.]+", load_raw)
load_str   = "  ".join(load_vals[:3]) if len(load_vals) >= 3 else "N/A"

# ── Memory ───────────────────────────────────────────────────────────────────
mem_bytes    = int(run(["sysctl", "-n", "hw.memsize"], "0"))
mem_total_gb = mem_bytes / (1024 ** 3)

vm_raw       = run(["vm_stat"])
pg_sz_m      = re.search(r"page size of (\d+) bytes", vm_raw)
pg_sz        = int(pg_sz_m.group(1)) if pg_sz_m else 16384

def vm_pg(label):
    m = re.search(rf"{label}:\s*([\d.]+)", vm_raw)
    return int(float(m.group(1))) if m else 0

pg_free     = vm_pg("Pages free")
pg_active   = vm_pg("Pages active")
pg_inactive = vm_pg("Pages inactive")
pg_wired    = vm_pg("Pages wired down")
pg_comp     = vm_pg("Pages occupied by compressor")
pg_spec     = vm_pg("Pages speculative")

gb = lambda pg: pg * pg_sz / (1024 ** 3)
mem_free_gb = gb(pg_free + pg_spec)
mem_act_gb  = gb(pg_active)
mem_inact_gb= gb(pg_inactive)
mem_wired_gb= gb(pg_wired)
mem_comp_gb = gb(pg_comp)
mem_used_gb = mem_act_gb + mem_wired_gb + mem_comp_gb
mem_used_pct= mem_used_gb / mem_total_gb * 100

# Swap (compressed memory overflow to disk)
swap_raw    = run(["sysctl", "vm.swapusage"])
# e.g. "vm.swapusage: total = 4096.00M  used = 2536.25M  free = 1559.75M  (encrypted)"
swap_total_m = re.search(r"total\s*=\s*([\d.]+)M", swap_raw)
swap_used_m  = re.search(r"used\s*=\s*([\d.]+)M", swap_raw)
swap_free_m  = re.search(r"free\s*=\s*([\d.]+)M", swap_raw)
swap_enc     = "(encrypted)" in swap_raw
swap_total_gb = float(swap_total_m.group(1)) / 1024 if swap_total_m else 0
swap_used_gb  = float(swap_used_m.group(1))  / 1024 if swap_used_m  else 0
swap_pct      = (swap_used_gb / swap_total_gb * 100) if swap_total_gb else 0

# ── Disk ─────────────────────────────────────────────────────────────────────
# macOS APFS splits into a read-only System volume and a writable Data volume.
# We query both so that "used" reflects actual combined consumption.
def _diskutil_gb(path, key):
    raw = run(["diskutil", "info", path])
    m = re.search(rf"{key}:\s*([\d.]+) GB", raw)
    return float(m.group(1)) if m else 0.0

disk_sys_gb   = _diskutil_gb("/", "Volume Used Space")           # macOS system files
disk_data_gb  = _diskutil_gb("/System/Volumes/Data", "Volume Used Space")  # user data
disk_total_gb = _diskutil_gb("/", "Container Total Space")
disk_free_gb  = _diskutil_gb("/", "Container Free Space")

if disk_total_gb == 0:
    # Fallback: df -g
    disk_raw = run(["df", "-g", "/"])
    disk_m   = re.search(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)%", disk_raw)
    if disk_m:
        _dt, _du, _df, _dp = [int(x) for x in disk_m.groups()]
        disk_total_gb = float(_dt); disk_free_gb = float(_df)
        disk_sys_gb = float(_du); disk_data_gb = 0.0
    else:
        disk_total_gb = disk_free_gb = disk_sys_gb = disk_data_gb = 0.0

disk_pct = int(((disk_total_gb - disk_free_gb) / disk_total_gb * 100) if disk_total_gb else 0)

# ── Network ──────────────────────────────────────────────────────────────────
# Try both en0 and en1 for WiFi SSID
wifi_ssid = ""
wifi_iface = ""
for iface in ["en0", "en1", "en2"]:
    _w = run(["networksetup", "-getairportnetwork", iface])
    if "Current Wi-Fi Network:" in _w:
        wifi_ssid = _w.replace("Current Wi-Fi Network:", "").strip()
        wifi_iface = iface
        break
wifi_connected = bool(wifi_ssid)

ipv4 = run(["ipconfig", "getifaddr", "en0"])
if ipv4 == "N/A":
    ipv4 = run(["ipconfig", "getifaddr", "en1"])

# IPv6 from scutil — match only proper IPv6 (contains at least one colon group)
nwi_raw  = run(["scutil", "--nwi"])
ipv6_m   = re.search(r"address\s*:\s*((?:[0-9a-fA-F]{1,4}:){2,}[0-9a-fA-F:]+)", nwi_raw)
ipv6     = ipv6_m.group(1) if ipv6_m else "N/A"

# Public IP (optional, requires network — safe no-op if offline)
pub_ip = run(["curl", "-s", "--max-time", "3", "https://api.ipify.org"], "unavailable")

# WiFi signal quality — only parse when actually connected
wifi_info = run(["system_profiler", "SPAirPortDataType"]) if wifi_connected else ""
rssi_str  = "N/A"
wifi_ch   = "N/A"
tx_rate   = "N/A"
if wifi_connected and wifi_info:
    rssi_m    = re.search(r"Signal / Noise.*?(-\d+)\s*/\s*(-\d+)", wifi_info)
    rssi_str  = f"{rssi_m.group(1)} dBm / {rssi_m.group(2)} dBm" if rssi_m else "N/A"
    channel_m = re.search(r"Channel:\s*(.+)", wifi_info)
    wifi_ch   = channel_m.group(1).strip() if channel_m else "N/A"
    tx_rate_m = re.search(r"Tx Rate:\s*([\d.]+)", wifi_info)
    tx_rate   = f"{tx_rate_m.group(1)} Mbps" if tx_rate_m else "N/A"

# ── pmset ────────────────────────────────────────────────────────────────────
pmset_batt      = run(["pmset", "-g", "batt"])
pmset_src_m     = re.search(r"Now drawing from '(.+)'", pmset_batt)
pmset_source    = pmset_src_m.group(1) if pmset_src_m else "Unknown"

pmset_all       = run(["pmset", "-g"])
sleep_m         = re.search(r"^\s*sleep\s+(\d+)", pmset_all, re.MULTILINE)
sleep_min       = int(sleep_m.group(1)) if sleep_m else 0
disksleep_m     = re.search(r"disksleep\s+(\d+)", pmset_all)
disksleep_min   = int(disksleep_m.group(1)) if disksleep_m else 0
halfdim_m       = re.search(r"halfdim\s+(\d+)", pmset_all)
halfdim         = int(halfdim_m.group(1)) if halfdim_m else 0
lidwake_m       = re.search(r"lidwake\s+(\d+)", pmset_all)
lidwake         = int(lidwake_m.group(1)) if lidwake_m else 0
lowpwrm_m       = re.search(r"lowpowermode\s+(\d+)", pmset_all)
low_power_mode  = int(lowpwrm_m.group(1)) if lowpwrm_m else 0

pmset_assert    = run(["pmset", "-g", "assertions"])
idle_prevented  = "PreventUserIdleSystemSleep" in pmset_assert and re.search(r"PreventUserIdleSystemSleep\s+1", pmset_assert)

# ── CPU usage (from top — always available) ──────────────────────────────────
top_raw    = run(["top", "-l", "1", "-n", "0"])
cpu_usr_m  = re.search(r"CPU usage:\s*([\d.]+)%\s*user", top_raw)
cpu_sys_m  = re.search(r"([\d.]+)%\s*sys", top_raw)
cpu_idle_m = re.search(r"([\d.]+)%\s*idle", top_raw)
cpu_usr    = float(cpu_usr_m.group(1))  if cpu_usr_m  else 0.0
cpu_sys    = float(cpu_sys_m.group(1))  if cpu_sys_m  else 0.0
cpu_idle   = float(cpu_idle_m.group(1)) if cpu_idle_m else 0.0
cpu_used   = cpu_usr + cpu_sys

# CPU per-core (psutil) or N/A
cpu_per_core = []
cpu_freq_mhz = 0
if HAS_PSUTIL:
    try:
        cpu_per_core = _psutil.cpu_percent(interval=0.2, percpu=True)
    except Exception:
        pass
    try:
        _freq = _psutil.cpu_freq()
        cpu_freq_mhz = int(_freq.current) if _freq else 0
    except Exception:
        pass

# ── Top processes by CPU usage ────────────────────────────────────────────────
proc_raw  = run(["ps", "-Ao", "pid,%cpu,%mem,comm", "-r"])
proc_lines = proc_raw.splitlines()[1:] if proc_raw != "N/A" else []
# Total running processes (subtract 1 for header line)
total_procs = max(0, len(proc_raw.splitlines()) - 1) if proc_raw != "N/A" else 0

top_procs = []
for line in proc_lines[:6]:
    parts = line.split(None, 3)
    if len(parts) == 4:
        try:
            pid, cpu_p, mem_p, comm = parts
            top_procs.append((float(cpu_p), float(mem_p), int(pid), shorten_proc(comm)))
        except (ValueError, IndexError):
            pass

# ── Disk I/O — 2-sample iostat for real-time reading ─────────────────────────
# First sample = cumulative average since boot; second sample = last 1-second interval.
try:
    _iostat_out = subprocess.check_output(
        ["iostat", "-d", "disk0", "1", "2"], text=True, stderr=subprocess.DEVNULL
    ).strip()
    _iostat_lines = [l for l in _iostat_out.splitlines() if re.search(r"[\d.]+\s+[\d.]+\s+[\d.]+", l)]
    # Use last data line (second sample = live interval)
    _last = _iostat_lines[-1] if _iostat_lines else ""
    iostat_m = re.search(r"([\d.]+)\s+([\d.]+)\s+([\d.]+)", _last)
except Exception:
    iostat_m = None

disk_kbt  = float(iostat_m.group(1)) if iostat_m else 0.0
disk_tps  = float(iostat_m.group(2)) if iostat_m else 0.0
disk_mbs  = float(iostat_m.group(3)) if iostat_m else 0.0

# Disk I/O lifetime counters (psutil — cumulative since boot)
disk_read_gb = disk_write_gb = 0.0
if HAS_PSUTIL:
    try:
        _dio = _psutil.disk_io_counters()
        if _dio:
            disk_read_gb  = _dio.read_bytes  / (1024**3)
            disk_write_gb = _dio.write_bytes / (1024**3)
    except Exception:
        pass

# ── Network I/O (netstat — always available) ──────────────────────────────────
net_raw   = run(["netstat", "-ib"])
net_rx_bytes = net_tx_bytes = 0
for line in net_raw.splitlines():
    parts = line.split()
    # netstat -ib columns: Name MTU Network Address Ipkts Ierrs Ibytes Opkts Oerrs Obytes Coll
    if len(parts) >= 10 and re.match(r"^en\d", parts[0]) and parts[3] not in ("<Link#", "N/A"):
        try:
            net_rx_bytes += int(parts[6])
            net_tx_bytes += int(parts[9])
        except (ValueError, IndexError):
            pass

net_rx_gb = net_rx_bytes / (1024**3)
net_tx_gb = net_tx_bytes / (1024**3)

# Per-interface I/O (psutil)
net_per_iface = {}
if HAS_PSUTIL:
    try:
        _nics = _psutil.net_io_counters(pernic=True)
        for iface, counters in _nics.items():
            if re.match(r"^en\d", iface) and (counters.bytes_recv + counters.bytes_sent) > 0:
                net_per_iface[iface] = (counters.bytes_recv / (1024**3),
                                        counters.bytes_sent / (1024**3))
    except Exception:
        pass


# ───────────────────────────── derived values ──────────────────────────────────

health_pct     = (raw_max_cap / design_cap * 100) if design_cap else 0
cycles_remain  = max(0, design_cycle - cycle_count)
cycle_pct_used = (cycle_count / design_cycle * 100) if design_cycle else 0

# True battery power at the pack terminals (most accurate):
display_bat_pw = bat_chg_mw if is_charging else bat_drain_mw
if display_bat_pw == 0:
    display_bat_pw = pack_pw_mw

display_bat_w  = display_bat_pw / 1000
sys_load_w     = sys_load_mw / 1000
sys_pw_w       = sys_pw_mw / 1000
eff_loss_w     = eff_loss_mw / 1000

# Charging status label
if fully_chgd:
    status_str = "Full ✅"
elif is_charging:
    status_str = "Charging ⚡"
elif ext_conn:
    status_str = "Plugged in — not charging 🔌"
else:
    status_str = "Discharging 🔋"

now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ───────────────────────────── render ──────────────────────────────────────────

def section(title):
    return f"\n{'━'*66}\n  {title}\n{'━'*66}"


lines = []
lines.append(f"""
╔══════════════════════════════════════════════════════════════════╗
║     🍎  Mac System & Battery Report  ·  {now_str}     ║
╚══════════════════════════════════════════════════════════════════╝""")

# ── 1. MACHINE ────────────────────────────────────────────────────────────────
_codename_str = f" {macos_codename}" if macos_codename else ""
lines.append(section("🖥️   MACHINE"))
lines.append(f"""  Model           : {model}  ({model_id}){"  [" + model_num + "]" if model_num else ""}
  Chip            : {chip}  [{arch}]
  CPU Cores       : {pcpu} physical · {lcpu} logical
  RAM             : {mem_str}
  Serial          : {mac_serial}
  macOS           : {macos_ver}{_codename_str}  (build {macos_bld})
  Hostname        : {hostname}
  Python          : {py_ver}""")

# ── 2. GPU & DISPLAY ──────────────────────────────────────────────────────────
lines.append(section("🎮  GPU & DISPLAY"))
lines.append(f"""  GPU             : {gpu_model}  ({gpu_cores}-core GPU)
  Metal           : {gpu_metal}
  Display Type    : {disp_type}
  Resolution      : {disp_res}
  Connection      : {disp_conn}""")

# ── 3. CHARGER / ADAPTER ──────────────────────────────────────────────────────
lines.append(section("🔌  CHARGER / ADAPTER"))
if ext_conn:
    lines.append(f"""  Connected       : Yes ✅
  Name            : {adp_name.strip()}
  Manufacturer    : {adp_mfg}
  Model ID        : {adp_model}
  Serial          : {adp_serial}
  Firmware        : {adp_fw}  (HW rev: {adp_hw})
  Adapter Rating  : {adp_watts} W  (rated max)
  Negotiated PD   : {pd_neg_v:.0f} V × {pd_neg_a:.1f} A = {pd_max_w:.0f} W  (USB-C PD profile {pd_idx})
  Wall Draw Now   : {wall_w:.2f} W  ({sys_v_mv/1000:.2f} V × {sys_i_ma/1000:.3f} A)
  Adapter Usage   : {bar(pd_util_pct, 20, neutral=True)}
  Headroom Left   : {pd_headroom:.1f} W  (unused capacity)""")
else:
    lines.append(f"""  Connected       : No ❌  (running on internal battery)
  Last known      : {adp_name.strip() if adp_name != "N/A" else "—"}""")

# ── 4. POWER FLOW ─────────────────────────────────────────────────────────────
lines.append(section("⚡  POWER FLOW  (real-time, from PMU telemetry)"))
if ext_conn:
    lines.append(f"""  Power Source    : {pmset_source}
  ┌─ Wall Input    : {wall_w:.2f} W  ← from wall outlet
  │  Adapter Loss  : {eff_loss_w:.2f} W  ← conversion overhead
  │  System Gets   : {sys_pw_w:.2f} W  ← delivered to Mac
  ├─ System Load   : {sys_load_w:.2f} W  ← CPU + GPU + peripherals
  └─ Battery In    : {display_bat_w:.2f} W  ← going into battery pack
  ─────────────────────────────────────────────────────────────────
  Balance check   : {sys_load_w:.2f} + {display_bat_w:.2f} = {sys_load_w + display_bat_w:.2f} W  (should ≈ {wall_w:.2f} W)""")
else:
    lines.append(f"""  Power Source    : {pmset_source}
  System Load     : {sys_load_w:.2f} W  ← CPU + GPU + peripherals
  Battery Out     : {display_bat_w:.2f} W  ← draining from pack
  ─────────────────────────────────────────────────────────────────
  Drain rate      : {amp_abs_ma/1000:.3f} A × {bat_volt_mv/1000:.3f} V = {pack_pw_mw/1000:.2f} W""")

# ── 5. BATTERY — STATE ────────────────────────────────────────────────────────
lines.append(section("🔋  BATTERY — STATE"))
time_line = f"  Time to Full    : {fmt_time(time_to_full)}" if is_charging else f"  Time Remaining  : {fmt_time(time_to_empty)}"
lines.append(f"""  Level           : {bar(soc)}
  Status          : {status_str}
{time_line}
  Battery Voltage : {bat_volt_mv/1000:.3f} V  (pack)
  Current Now     : {amp_abs_ma/1000:.3f} A  ({"+" if is_charging else "-"}, {"charging" if is_charging else "discharging"})
  Pack Power      : {display_bat_w:.2f} W  ({"charging into" if is_charging else "draining from"} pack)
  Low Power Mode  : {"On 🔋" if low_power_mode else "Off"}
  Today Range     : {daily_min}% – {daily_max}%  (min/max SOC today)""")

if cell_volts:
    cell_str = "  ".join(f"Cell{i+1}: {v/1000:.3f}V" for i, v in enumerate(cell_volts))
    pack_sum = sum(cell_volts)
    lines.append(f"  Cell Voltages   : {cell_str}  (pack sum: {pack_sum/1000:.3f} V)")

if not_chg_rsn:
    lines.append(f"  ⚠ Not charging reason code: {not_chg_rsn}")
if slow_chg_rsn:
    lines.append(f"  ⚠ Slow charging reason code: {slow_chg_rsn}")
if chg_therml_s:
    lines.append(f"  ⚠ Thermally limited: {chg_therml_s}s total")

# ── 6. BATTERY — HEALTH ───────────────────────────────────────────────────────
lines.append(section("🔋  BATTERY — HEALTH"))
lines.append(f"""  Health          : {bar(health_pct)}  →  {health_label(health_pct)}
  Max Capacity    : {raw_max_cap:,} mAh  ←  design was {design_cap:,} mAh  (lost {design_cap - raw_max_cap:,} mAh)
  Nominal Cap     : {nominal_cap:,} mAh
  Current Charge  : {raw_cur_cap:,} mAh  ({raw_cur_cap/raw_max_cap*100:.0f}% of max)
  Qmax (cells)    : {", ".join(str(q) + " mAh" for q in qmax_vals) if qmax_vals else "N/A"}
  Cycle Count     : {bar(cycle_pct_used, 20, reverse=True)}
                    {cycle_count} used  /  {design_cycle} rated  (~{cycles_remain} remaining)
  Battery Serial  : {bat_serial}
  Peak V ever     : {max_volt_ever/1000:.3f} V  |  Low V ever : {min_volt_ever/1000:.3f} V
  Peak charge I   : {max_chg_ever/1000:.3f} A  (lifetime max)""")

# ── 7. THERMAL ────────────────────────────────────────────────────────────────
lines.append(section("🌡️   THERMAL"))
lines.append(f"""  Battery Temp    : {bat_temp_c:.1f} °C  (right now)
  Lifetime Avg    : {avg_temp_raw/10:.1f} °C
  Lifetime Min    : {min_temp_raw/10:.1f} °C
  Lifetime Max    : {max_temp_raw/10:.1f} °C
  Thermally ltd   : {chg_therml_s} s  (total charging time throttled by heat)""")

# ── 8. RUNTIME ────────────────────────────────────────────────────────────────
lines.append(section("🏃  RUNTIME"))
lines.append(f"""  Uptime          : {uptime_fmt}
  Total Op. Hours : {total_op_h:,} h  (cumulative lifetime battery active hours)
  Load Avg        : {load_str}  (1m · 5m · 15m)
  Processes       : {total_procs} running""")

# ── 9. CPU ────────────────────────────────────────────────────────────────────
lines.append(section("⚙️   CPU"))
_psutil_note = "" if HAS_PSUTIL else "  (install psutil for per-core breakdown)"
lines.append(f"""  Usage           : {bar(cpu_used, reverse=True)}{_psutil_note}
  User            : {cpu_usr:.1f}%
  System          : {cpu_sys:.1f}%
  Idle            : {cpu_idle:.1f}%""")
if cpu_freq_mhz:
    lines.append(f"  Frequency       : {cpu_freq_mhz:,} MHz")
if cpu_per_core:
    core_bars = "  ".join(f"C{i}: {p:.0f}%" for i, p in enumerate(cpu_per_core))
    lines.append(f"  Per-Core        : {core_bars}")

# ── 10. TOP PROCESSES ─────────────────────────────────────────────────────────
lines.append(section("📋  TOP PROCESSES  (by CPU usage)"))
if top_procs:
    lines.append(f"  {'PID':<7}  {'CPU%':>5}  {'MEM%':>5}  Process")
    lines.append(f"  {'─'*7}  {'─'*5}  {'─'*5}  {'─'*35}")
    for _cpu_p, _mem_p, _pid, _name in top_procs[:5]:
        lines.append(f"  {_pid:<7}  {_cpu_p:>5.1f}  {_mem_p:>5.1f}  {_name}")
else:
    lines.append("  (unable to read process list)")

# ── 11. MEMORY ─────────────────────────────────────────────────────────────────
lines.append(section("💾  MEMORY"))
_swap_note = " (encrypted)" if swap_enc else ""
lines.append(f"""  Usage           : {bar(mem_used_pct, reverse=True)}  →  {mem_label(mem_used_pct)}
  Total           : {mem_total_gb:.1f} GB
  Active          : {mem_act_gb:.2f} GB  (in use by apps)
  Wired           : {mem_wired_gb:.2f} GB  (kernel, locked)
  Compressed      : {mem_comp_gb:.2f} GB  (swapped via compressor)
  Inactive        : {mem_inact_gb:.2f} GB  (reclaimable)
  Free            : {mem_free_gb:.2f} GB
  Swap            : {swap_used_gb:.2f} GB used / {swap_total_gb:.2f} GB total{_swap_note}""")

# ── 12. DISK ──────────────────────────────────────────────────────────────────
lines.append(section("💿  DISK  ( / )"))
_io_lifetime = ""
if disk_read_gb or disk_write_gb:
    _io_lifetime = f"\n  Read (lifetime) : {disk_read_gb:.2f} GB  |  Write: {disk_write_gb:.2f} GB"
lines.append(f"""  Storage         : {ssd_model}  ({ssd_capacity})
  Usage           : {bar(disk_pct, reverse=True)}
  Container Total : {disk_total_gb:.1f} GB  (physical SSD)
  System Volume   : {disk_sys_gb:.1f} GB  (macOS system, read-only sealed snapshot)
  Data Volume     : {disk_data_gb:.1f} GB  (apps, user files, documents)
  Container Free  : {disk_free_gb:.1f} GB  (raw unallocated blocks)
  ⓘ System Settings may show ~5-10 GB more free — it adds purgeable caches
  I/O (now)       : {disk_tps:.0f} tps · {disk_mbs:.2f} MB/s  (disk0){_io_lifetime}""")

# ── 13. NETWORK ───────────────────────────────────────────────────────────────
lines.append(section("🌐  NETWORK"))
_wifi_status = wifi_ssid if wifi_connected else "Not connected"
lines.append(f"""  IPv4  (en0)     : {ipv4}
  IPv6            : {ipv6}
  Public IP       : {pub_ip}
  Wi-Fi SSID      : {_wifi_status}""")
if wifi_connected:
    lines.append(f"""  Wi-Fi Channel   : {wifi_ch}
  Signal/Noise    : {rssi_str}
  TX Rate         : {tx_rate}""")
lines.append(f"""  RX (since boot) : {net_rx_gb:.2f} GB
  TX (since boot) : {net_tx_gb:.2f} GB""")
if net_per_iface:
    for _iface, (_rx, _tx) in sorted(net_per_iface.items()):
        if _rx + _tx > 0.01:
            lines.append(f"  {_iface:<15} : ↓ {_rx:.2f} GB  ↑ {_tx:.2f} GB")

# ── 14. POWER MANAGEMENT ──────────────────────────────────────────────────────
lines.append(section("⚙️   POWER MANAGEMENT"))
lines.append(f"""  Power Source    : {pmset_source}
  Sleep Timer     : {"disabled" if not sleep_min else str(sleep_min) + " min"}
  Disk Sleep      : {"disabled" if not disksleep_min else str(disksleep_min) + " min"}
  Half-dim        : {"enabled" if halfdim else "disabled"}
  Lid Wake        : {"enabled" if lidwake else "disabled"}
  Sleep prevented : {"Yes (assertion active)" if idle_prevented else "No"}
  Low Power Mode  : {"On 🔋" if low_power_mode else "Off"}""")

lines.append("")

report = "\n".join(lines)

# ── Export ───────────────────────────────────────────────────────────────────
if _do_export:
    _export_dir = os.path.dirname(os.path.abspath(_export_path))
    if _export_dir:
        os.makedirs(_export_dir, exist_ok=True)
    clean_report = strip_ansi(report)
    with open(_export_path, "w", encoding="utf-8") as f:
        f.write(clean_report)
    print(report)
    print(f"\n{'━'*66}")
    print(f"  ✅  Report exported to:")
    print(f"      {_export_path}")
    print(f"{'━'*66}\n")
else:
    print(report)
    if not HAS_PSUTIL:
        print("  💡  Tip: run via run.sh for auto-install of psutil (adds per-core CPU stats)")
        print(f"  {'─'*62}\n")
