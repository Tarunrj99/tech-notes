#!/usr/bin/env python3
"""
battery_live.py — Real-time Mac Battery & System Live Monitor

Refreshes key metrics every 3 seconds, rewriting in-place.
Press Ctrl+C to exit.

One-liner (once added to run.sh):
  curl -fsSL https://raw.githubusercontent.com/Tarunrj99/tech-notes/main/tools/mac/battery-info/run.sh | bash -s -- --live

Local run:
  python3 tools/mac/battery-info/scripts/battery_live.py
"""

import subprocess, re, sys, os, time
from datetime import datetime

# ── Optional psutil (faster CPU / IO readings) ──────────────────────────────
try:
    import psutil as _psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

REFRESH_SECS = 3
WIDTH        = 68

# ─────────────────────────── helpers ────────────────────────────────────────

def run(cmd, default=""):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return default

def ri(s, pat, default=0):
    m = re.search(pat, s); return int(m.group(1)) if m else default

def rf(s, pat, default=0.0):
    m = re.search(pat, s); return float(m.group(1)) if m else default

def flag(s, pat):
    m = re.search(pat, s)
    return m.group(1).strip() in ("Yes", "true", "1") if m else False

def signed64(v):
    return v - (1 << 64) if v >= (1 << 63) else v

def fmt_time(mins):
    if mins <= 0 or mins >= 65535: return "—"
    h, m = divmod(int(mins), 60)
    return f"{h}h {m:02d}m" if h else f"{m}m"

def bar(pct, width=24, reverse=False):
    pct = max(0.0, min(100.0, float(pct)))
    filled = int(pct * width / 100)
    b = "█" * filled + "░" * (width - filled)
    if reverse:
        dot = "🟢" if pct < 60 else ("🟡" if pct < 85 else "🔴")
    else:
        dot = "🟢" if pct > 40 else ("🟡" if pct > 20 else "🔴")
    return f"[{b}] {pct:5.1f}%  {dot}"

SEP = "━" * WIDTH

# ─────────────────────────── data collection ────────────────────────────────

def collect(prev_net, prev_disk):
    raw = run(["ioreg", "-r", "-c", "AppleSmartBattery"])

    # ── battery ──
    soc = ri(raw, r'"CurrentCapacity"\s*=\s*(\d+)') or ri(raw, r'"StateOfCharge"\s*=\s*(\d+)')
    is_chg  = flag(raw, r'"IsCharging"\s*=\s*(Yes|No|true|false)')
    full    = flag(raw, r'"FullyCharged"\s*=\s*(Yes|No|true|false)')
    ext     = flag(raw, r'"ExternalConnected"\s*=\s*(Yes|No|true|false)')
    voltage = ri(raw, r'"Voltage"\s*=\s*(\d+)') / 1000
    temp    = ri(raw, r'"Temperature"\s*=\s*(\d+)') / 100
    amp_raw = ri(raw, r'"Amperage"\s*=\s*(\d+)')
    amp     = signed64(amp_raw) / 1000   # A, +charging / -discharging

    # ── power telemetry ──
    ptd_m = re.search(r'"PowerTelemetryData"\s*=\s*\{([^}]+)\}', raw)
    ptd   = ptd_m.group(1) if ptd_m else ""
    wall_w   = ri(ptd, r'"SystemPowerIn"\s*=\s*(\d+)')   / 1000
    sys_load = ri(ptd, r'"SystemLoad"\s*=\s*(\d+)')      / 1000
    batt_pwr = signed64(ri(ptd, r'"BatteryPower"\s*=\s*(\d+)')) / 1000
    v_in     = ri(ptd, r'"SystemVoltageIn"\s*=\s*(\d+)') / 1000
    a_in     = ri(ptd, r'"SystemCurrentIn"\s*=\s*(\d+)') / 1000
    adp_w    = ri(raw, r'"Watts"\s*=\s*(\d+)')

    # ── time to full / empty ──
    ttf = ri(raw, r'"AvgTimeToFull"\s*=\s*(\d+)',  65535)
    tte = ri(raw, r'"AvgTimeToEmpty"\s*=\s*(\d+)', 65535)
    pmset_batt = run(["pmset", "-g", "batt"])
    pm_m = re.search(r'(\d+):(\d+)\s+remaining', pmset_batt)
    if pm_m:
        pm_mins = int(pm_m.group(1)) * 60 + int(pm_m.group(2))
        if is_chg: ttf = pm_mins
        else:      tte = pm_mins

    # ── CPU ──
    if HAS_PSUTIL:
        ct       = _psutil.cpu_times_percent(interval=1)
        cpu_user = ct.user
        cpu_sys  = ct.system
        pct      = cpu_user + cpu_sys
        freq     = getattr(_psutil.cpu_freq(), 'current', 0)
        per_core = _psutil.cpu_percent(percpu=True)
    else:
        top_out  = run(["top", "-l", "2", "-n", "0"])
        top_lines = [l for l in top_out.splitlines() if "CPU usage" in l]
        last     = top_lines[-1] if top_lines else ""
        cpu_user = rf(last, r'([\d.]+)%\s*user')
        cpu_sys  = rf(last, r'([\d.]+)%\s*sys')
        pct      = cpu_user + cpu_sys
        freq     = 0
        per_core = []

    # ── load averages ──
    load_raw = run(["sysctl", "-n", "vm.loadavg"])
    load_m   = re.search(r'\{?\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)', load_raw)
    l1 = float(load_m.group(1)) if load_m else 0
    l5 = float(load_m.group(2)) if load_m else 0
    l15= float(load_m.group(3)) if load_m else 0

    # ── memory ──
    if HAS_PSUTIL:
        vm = _psutil.virtual_memory()
        mem_total   = vm.total / 1e9
        active_gb   = getattr(vm, 'active',   0) / 1e9
        wired_gb    = getattr(vm, 'wired',    0) / 1e9
        inactive_gb = getattr(vm, 'inactive', 0) / 1e9
        free_gb     = vm.available / 1e9
        mem_pct     = vm.percent
        sw = _psutil.swap_memory()
        swap_used   = sw.used / 1e9
        swap_total  = sw.total / 1e9
        comp_gb     = max(0.0, mem_total - active_gb - wired_gb - inactive_gb - free_gb)
    else:
        PAGE = 16384
        vm_s = run(["vm_stat"])
        def vp(pat): return ri(vm_s, pat) * PAGE / 1e9
        mem_total   = int(run(["sysctl", "-n", "hw.memsize"]) or 0) / 1e9
        active_gb   = vp(r"Pages active:\s+(\d+)")
        wired_gb    = vp(r"Pages wired down:\s+(\d+)")
        comp_gb     = vp(r"Pages occupied by compressor:\s+(\d+)")
        inactive_gb = vp(r"Pages inactive:\s+(\d+)")
        free_gb     = vp(r"Pages free:\s+(\d+)")
        mem_pct     = (active_gb + wired_gb + comp_gb) / mem_total * 100 if mem_total else 0
        sw_m        = re.search(r'used\s*=\s*([\d.]+)M.*total\s*=\s*([\d.]+)M',
                                run(["sysctl", "vm.swapusage"]))
        swap_used   = float(sw_m.group(1)) / 1024 if sw_m else 0
        swap_total  = float(sw_m.group(2)) / 1024 if sw_m else 0

    # ── top processes ──
    top_procs = []
    ps_out = run(["ps", "aux"])
    for line in ps_out.splitlines()[1:]:
        parts = line.split(None, 10)
        if len(parts) >= 11:
            try:
                cpu_p = float(parts[2])
                mem_p = float(parts[3])
                pid   = parts[1]
                name  = os.path.basename(parts[10].split()[0])[:34]
                top_procs.append((cpu_p, mem_p, pid, name))
            except (ValueError, IndexError):
                pass
    top_by_cpu = sorted(top_procs, key=lambda x: x[0], reverse=True)[:3]
    top_by_mem = sorted(top_procs, key=lambda x: x[1], reverse=True)[:3]

    # ── cpu count (for load-avg bar) ──
    if HAS_PSUTIL:
        num_cpus = _psutil.cpu_count(logical=True) or 8
    else:
        try:
            num_cpus = int(run(["sysctl", "-n", "hw.logicalcpu"]) or 8)
        except Exception:
            num_cpus = 8

    # ── network I/O delta ──
    now_net_rx, now_net_tx = 0, 0
    if HAS_PSUTIL:
        nio = _psutil.net_io_counters(pernic=False)
        now_net_rx, now_net_tx = nio.bytes_recv, nio.bytes_sent
    else:
        for line in run(["netstat", "-ib"]).splitlines():
            if "<Link#" in line:
                parts = line.split()
                if len(parts) >= 10:
                    try: now_net_rx += int(parts[6]); now_net_tx += int(parts[9])
                    except (ValueError, IndexError): pass

    rx_delta = max(0, now_net_rx - prev_net[0])
    tx_delta = max(0, now_net_tx - prev_net[1])

    # ── disk I/O delta ──
    now_disk_r, now_disk_w = 0, 0
    if HAS_PSUTIL:
        dio = _psutil.disk_io_counters(perdisk=False)
        now_disk_r = dio.read_bytes if dio else 0
        now_disk_w = dio.write_bytes if dio else 0
    disk_r_delta = max(0, now_disk_r - prev_disk[0])
    disk_w_delta = max(0, now_disk_w - prev_disk[1])

    return {
        "soc": soc, "is_chg": is_chg, "full": full, "ext": ext,
        "voltage": voltage, "temp": temp, "amp": amp,
        "wall_w": wall_w, "sys_load": sys_load, "batt_pwr": batt_pwr,
        "v_in": v_in, "a_in": a_in, "adp_w": adp_w,
        "ttf": ttf, "tte": tte,
        "cpu_pct": pct, "cpu_user": cpu_user, "cpu_sys": cpu_sys,
        "freq": freq, "per_core": per_core,
        "top_by_cpu": top_by_cpu,
        "top_by_mem": top_by_mem,
        "num_cpus": num_cpus,
        "l1": l1, "l5": l5, "l15": l15,
        "mem_pct": mem_pct, "mem_total": mem_total,
        "active_gb": active_gb, "wired_gb": wired_gb,
        "comp_gb": comp_gb, "swap_used": swap_used, "swap_total": swap_total,
        "rx_delta": rx_delta, "tx_delta": tx_delta,
        "disk_r_delta": disk_r_delta, "disk_w_delta": disk_w_delta,
        "net_rx_total": now_net_rx, "net_tx_total": now_net_tx,
        "disk_r_total": now_disk_r, "disk_w_total": now_disk_w,
    }, (now_net_rx, now_net_tx), (now_disk_r, now_disk_w)


# ─────────────────────────── render ─────────────────────────────────────────

def render(d, model, interval):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title_left  = f"🍎  Live Monitor  ·  {model}"
    title_right = f"↺ {interval}s"
    pad = WIDTH - 2 - len(title_left) - len(title_right)
    title_line = f"║ {title_left}{' ' * max(0, pad)}{title_right} ║"

    # Battery state
    if d["full"]:
        status = "Full ✅"
    elif d["is_chg"]:
        status = "Charging ⚡"
    elif d["ext"]:
        status = "Plugged in — not charging 🔌"
    else:
        status = "Discharging 🔋"

    # Time label
    if d["is_chg"]:
        t = fmt_time(d["ttf"])
        t_val = "Topping off" if d["soc"] >= 100 and t == "—" else t
        t_label = f"Time to Full    : {t_val}"
    else:
        t_label = f"Time Remaining  : {fmt_time(d['tte'])}"

    # Power flow
    src = "AC Power" if d["ext"] else "Battery Power"
    if d["ext"]:
        pwr_line = (f"  Wall Input      : {d['wall_w']:.2f} W  "
                    f"({d['v_in']:.2f} V × {d['a_in']:.3f} A)")
        batt_line = (f"  Battery {'In ' if d['is_chg'] else 'Out'}     : "
                     f"{abs(d['batt_pwr']):.2f} W  ·  "
                     f"System: {d['sys_load']:.2f} W")
    else:
        pwr_line  = f"  System Load     : {d['sys_load']:.2f} W"
        batt_line = f"  Battery Out     : {abs(d['batt_pwr']):.2f} W  (draining)"

    # Network delta
    rx_kb = d["rx_delta"] / 1024
    tx_kb = d["tx_delta"] / 1024
    if rx_kb >= 1024: rx_str = f"{rx_kb/1024:.2f} MB/s ↓"
    else:             rx_str = f"{rx_kb:.1f} KB/s ↓"
    if tx_kb >= 1024: tx_str = f"{tx_kb/1024:.2f} MB/s ↑"
    else:             tx_str = f"{tx_kb:.1f} KB/s ↑"

    # Disk delta
    dr_kb = d["disk_r_delta"] / 1024
    dw_kb = d["disk_w_delta"] / 1024
    if dr_kb >= 1024: dr_str = f"{dr_kb/1024:.2f} MB/s R"
    else:             dr_str = f"{dr_kb:.1f} KB/s R"
    if dw_kb >= 1024: dw_str = f"{dw_kb/1024:.2f} MB/s W"
    else:             dw_str = f"{dw_kb:.1f} KB/s W"

    freq_str = f"  ·  {d['freq']:.0f} MHz" if d["freq"] else ""

    # Load avg bar (1m relative to cpu count = 100%)
    load_bar_pct = min(100.0, d["l1"] / max(1, d["num_cpus"]) * 100)
    # Trend: compare 1m to 5m
    if   d["l1"] > d["l5"] + 0.05: load_trend = "↑"
    elif d["l1"] < d["l5"] - 0.05: load_trend = "↓"
    else:                           load_trend = "→"

    lines = [
        "",
        f"╔{'═' * (WIDTH - 2)}╗",
        title_line,
        f"║  {now:^{WIDTH - 4}}  ║",
        f"╚{'═' * (WIDTH - 2)}╝",
        "",
        SEP,
        "  🔋  BATTERY",
        SEP,
        f"  Level          : {bar(d['soc'])}",
        f"  Status         : {status}",
        f"  {t_label}",
        f"  Voltage        : {d['voltage']:.3f} V  ·  Temp : {d['temp']:.1f} °C",
        f"  Current        : {abs(d['amp']):.3f} A  ({'+ charging' if d['amp'] > 0 else '- discharging'})",
        "",
        SEP,
        "  ⚡  POWER FLOW",
        SEP,
        f"  Source         : {src}",
        pwr_line,
        batt_line,
        "",
        SEP,
        "  ⚙️   CPU",
        SEP,
        f"  Usage          : {bar(d['cpu_pct'], reverse=True)}{freq_str}",
        f"  User / System  : {d['cpu_user']:.1f}%  /  {d['cpu_sys']:.1f}%",
        f"  Load Avg       : {bar(load_bar_pct, width=16, reverse=True)}  {d['l1']:.2f} {load_trend} {d['l5']:.2f} → {d['l15']:.2f}  (1m/5m/15m)",
        *([f"  Per-Core       : " + "  ".join(
            f"C{i}:{v:.0f}%" for i, v in enumerate(d["per_core"])
        )] if d["per_core"] else []),
        "",
        SEP,
        "  💾  MEMORY",
        SEP,
        f"  Usage          : {bar(d['mem_pct'], reverse=True)}",
        f"  Active / Wired : {d['active_gb']:.2f} GB  /  {d['wired_gb']:.2f} GB",
        f"  Compressed     : {d['comp_gb']:.2f} GB  ·  Swap : {d['swap_used']:.2f} / {d['swap_total']:.2f} GB",
        "",
        SEP,
        "  📋  TOP PROCESSES",
        SEP,
        "  ── By CPU ──────────────────────────────────────────────────────",
        f"  {'PID':<7}  {'CPU%':>5}  {'MEM%':>5}  Process",
        f"  {'─'*7}  {'─'*5}  {'─'*5}  {'─'*34}",
        *[f"  {pid:<7}  {cpu:>5.1f}  {mem:>5.1f}  {name}"
          for cpu, mem, pid, name in d["top_by_cpu"]],
        "  ── By Memory ────────────────────────────────────────────────────",
        f"  {'PID':<7}  {'CPU%':>5}  {'MEM%':>5}  Process",
        f"  {'─'*7}  {'─'*5}  {'─'*5}  {'─'*34}",
        *[f"  {pid:<7}  {cpu:>5.1f}  {mem:>5.1f}  {name}"
          for cpu, mem, pid, name in d["top_by_mem"]],
        "",
        SEP,
        "  🌐  NETWORK  (since last refresh)",
        SEP,
        f"  Download  : {rx_str}",
        f"  Upload    : {tx_str}",
        "",
        SEP,
        "  💿  DISK  (since last refresh)",
        SEP,
        f"  Read      : {dr_str}",
        f"  Write     : {dw_str}",
        "",
        f"  Press Ctrl+C to exit",
        "",
    ]
    return lines


# ─────────────────────────── main ───────────────────────────────────────────

def main():
    # Static info — collected once
    hw = run(["system_profiler", "SPHardwareDataType"])
    chip_m  = re.search(r"Chip:\s+(.+)",       hw)
    model_m = re.search(r"Model Name:\s+(.+)", hw)
    chip  = chip_m.group(1).strip()  if chip_m  else "Mac"
    model = model_m.group(1).strip() if model_m else "Mac"
    short = f"{model} ({chip})"

    # Prime counters so first displayed delta is meaningful (not total-since-boot)
    _prime, prev_net, prev_disk = collect((0, 0), (0, 0))

    # Switch to alternate screen buffer (like htop/top) so the frame can be any
    # height, the main terminal history is never touched, and Ctrl+C restores
    # everything exactly as the user left it.
    sys.stdout.write("\033[?1049h"   # enter alt screen
                     "\033[?25l"     # hide cursor
                     "\033[2J"       # clear alt screen
                     "\033[H")       # move to top-left
    sys.stdout.flush()

    try:
        while True:
            t_start = time.monotonic()

            d, prev_net, prev_disk = collect(prev_net, prev_disk)
            lines = render(d, short, REFRESH_SECS)

            sys.stdout.write("\033[H")          # jump to top-left each refresh
            for line in lines:
                sys.stdout.write(f"\033[K{line}\n")   # clear-to-eol then print
            sys.stdout.flush()

            sleep_for = max(0.1, REFRESH_SECS - (time.monotonic() - t_start))
            time.sleep(sleep_for)

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h"     # restore cursor
                         "\033[?1049l")  # leave alt screen → main screen restored
        sys.stdout.flush()
        print("\n  Live monitor stopped.")


if __name__ == "__main__":
    main()
