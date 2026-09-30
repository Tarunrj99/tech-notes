# Accessing a Mac Remotely: Local Network & Anywhere via Tailscale

> A step-by-step guide to viewing and controlling one Mac from another, whether you're on the same Wi-Fi or on the other side of the world.

| Item | Value |
|---|---|
| OS / target | macOS Sonoma / Sequoia (host and client) |
| Tested on | Two MacBooks, built-in Screen Sharing + Tailscale |
| Time to complete | ~20 min |
| Difficulty | beginner |

---

## Prerequisites

- **Mac 1 (Host)**: the machine you want to connect *to* (must stay on and lid open)
- **Mac 2 (Client)**: the machine you connect *from*
- Both running macOS (tested on macOS Sonoma / Sequoia)

---

## Part 1: Configure Mac 1 (Host), One-Time Setup

These settings only need to be done once on the machine you want to access remotely.

### 1. Enable Remote Access

**Path:** System Settings → General → Sharing

1. Toggle **Remote Management** → ON
2. Toggle **Remote Login** → ON
3. Click the **ⓘ** icon next to Remote Management and set:
   - **VNC viewers may control screen with password** → ON (set a strong VNC password)
   - **Allow access for** → All users
4. Click **Options…** to expand the permissions panel and toggle all of the following ON:

   | Permission | Toggle |
   |---|---|
   | Observe | ON |
   | Control | ON |
   | Generate reports | ON |
   | Open and quit applications | ON |
   | Change settings | ON |
   | Delete and replace items | ON |
   | Start text chat or send messages | ON |
   | Restart and shutdown | ON |
   | Copy items | ON |

> **Find your exact username:** Open Terminal on Mac 1 and run `whoami`. Use this output as the username when connecting from Mac 2, paired with your normal login password.

---

### 2. Prevent the System from Sleeping

Without these settings, Mac 1 will sleep when unattended and drop all connections.

**Display timeout** (System Settings → Lock Screen):
- Turn display off on battery when inactive → **3 hours**
- Turn display off on power adapter when inactive → **3 hours**

> The screen will go dark to protect the panel, but the system process stays awake.

**Sleep prevention** (System Settings → Battery → Options):
- Prevent automatic sleeping on power adapter when display is off → **ON**
- Wake for network access → **Always**
- Optimized Battery Charging → **ON** (leave this active, it caps charge at 80% while perpetually plugged in, protecting long-term battery health; the Mac stays fully functional for remote access at 80%)

> **Important: Lid must stay open.** Closing the lid triggers a hardware sleep sensor that shuts down the Wi-Fi card and drops all connections, regardless of any software setting. The screen will lock itself automatically; the lid must physically remain open.

#### Alternative: `caffeinate` (No Settings Change Required)

If you prefer not to modify system settings permanently, macOS has a built-in terminal command for this:

1. Open **Terminal** on Mac 1
2. Run:
   ```bash
   caffeinate -s
   ```
3. Leave the Terminal window open: the system cannot enter deep sleep while it is running
4. Close the window when you no longer need the Mac to stay awake

> `-s` keeps the system awake only while on AC power. This is a lightweight, reversible alternative to the Battery settings above.

---

## Part 2: Connect Over Local Wi-Fi (Same Network)

No extra software needed when both Macs are on the same Wi-Fi router.

1. On **Mac 2**, open **Screen Sharing** via Spotlight (`⌘ Space` → type "Screen Sharing")
2. In the address bar, enter Mac 1's local hostname:
   ```
   your-mac-hostname.local
   ```
   Find it by running `hostname` in Terminal on Mac 1. Alternatively, use its local IP address (e.g. `192.168.x.x`), visible under System Settings → Network on Mac 1.
3. Click **Connect**
4. Enter credentials:
   - **Username:** output of `whoami` on Mac 1
   - **Password:** Mac 1's login password, or the VNC password set in Part 1

---

## Part 3: Connect from Anywhere via Tailscale

Use this when both Macs are on different networks (travelling, different offices, mobile hotspot). Tailscale creates a private encrypted tunnel between devices without any router or firewall configuration.

### 3.1 Install & Configure Tailscale on Both Macs

1. Download and install Tailscale on both Mac 1 and Mac 2 from `tailscale.com/download`
2. On **each machine**, open Tailscale → **Settings** and apply the following:

**General tab:**

| Setting | Value |
|---|---|
| Allow incoming connections | ON |
| Use Tailscale DNS settings | ON |
| Use Tailscale subnets | ON |
| Launch Tailscale at login | ON |

**VPN On Demand** → click **Manage…:**

| Setting | Value |
|---|---|
| VPN On Demand (master toggle) | ON |
| Connect automatically on Wi-Fi | Always |
| Connect automatically on Ethernet | Always |
| Detect MagicDNS hostnames | ON |

> **Why Detect MagicDNS hostnames?** With this on, Tailscale auto-connects the moment any app (including Screen Sharing) tries to reach a `.ts.net` address, even if Tailscale was not already active. Without it, you would need to open Tailscale manually before Screen Sharing can find the host.

With all of the above set, the tunnel comes up automatically on every boot and reconnects on every network change. No manual action is needed.

---

### 3.2 Share Mac 1 Across Different Tailscale Accounts (Node Sharing)

Only needed if Mac 1 and Mac 2 are signed into **different** Tailscale accounts. If both use the same account, skip to 3.3.

1. On **Mac 1**, log into the Tailscale Admin Console (`login.tailscale.com`) with Mac 1's account
2. Go to **Machines** → find Mac 1 → click **⋯** → **Share this machine…**
3. Copy the generated invite link
4. Open the invite link on **Mac 2** and click **Accept Share**

---

### 3.3 Connect Remotely

1. On **Mac 2**, open **Screen Sharing**
2. Enter Mac 1's Tailscale address (either format works):
   - **FQDN:** `hostname.tailnet-name.ts.net` (shown in the Tailscale admin panel)
   - **Tailscale IP:** `100.x.x.x` (visible in the Tailscale menu bar app on Mac 1)
3. Click **Connect**
4. Enter the same credentials as in Part 2 (username + login password)

You now have full screen control from anywhere in the world.

---

## Keeping Mac 1 Reachable Long-Term (Days or Weeks)

### Auto Login After a Restart

For Mac 1 to come back online automatically after a restart, without someone physically typing a password, enable Auto Login:

**System Settings → Users & Groups → Automatically log in as** → select your user

However, Auto Login may not be available on your machine for one or both of the following reasons:

**1. FileVault is enabled**
FileVault encrypts the entire disk. Apple disables Auto Login when FileVault is on because the disk encryption key must be unlocked by a user password at every boot. This is a security requirement and cannot be bypassed.
To check: System Settings → Privacy & Security → FileVault

**2. A device management profile is restricting it**
If your Mac is managed by an organisation (employer, school, etc.), a configuration profile may have locked this setting. You will see *"This setting has been configured by a profile"* next to the option. This cannot be changed without the organisation modifying or removing the profile.

If either of these applies, **Auto Login is not possible**. After any restart, someone must physically enter the password at the login screen before remote access works again.

---

### Strategy: Prevent Restarts Entirely

If Auto Login is blocked, the best approach is to keep the system running continuously and avoid restarts altogether.

**1. Prevent sleep**

Use **Amphetamine** (free, Mac App Store): it runs silently in the menu bar, survives reboots, and can keep the system awake indefinitely or on a schedule. More reliable than leaving a terminal window open.

Or use the built-in terminal command (see Part 1 Section 2 for details):
```bash
caffeinate -s
```

**2. Disable automatic update restarts**

> System Settings → General → Software Update → turn off **"Install updates automatically"**

This prevents macOS from rebooting in the background to apply updates. You can still update manually at a time of your choosing.

> **Note:** If your Mac is managed by a device profile, Software Update settings may also be locked by your organisation. In that case, automatic updates cannot be disabled and you should plan for periodic restarts outside of critical remote-access periods.

**3. Stay on power adapter**

Keep Mac 1 plugged in at all times with the sleep prevention settings from Part 1 active.

With all three in place, Mac 1 can run continuously for weeks without a restart and Tailscale will stay connected throughout.

---

## Optional: Tailscale Exit Node

Not required for screen sharing. An Exit Node routes **all internet traffic** from Mac 2 through Mac 1, turning it into a personal VPN gateway.

**When useful:**
- Travelling and want your browsing to appear as if it is coming from Mac 1's home/office network
- Need access to region-restricted content or services only available on Mac 1's network

**How to enable (on Mac 1):**
1. Tailscale Settings → **Exit Nodes** → toggle **Run as exit node** → ON
2. Approve it in the Tailscale Admin Console under Machines (required for activation)
3. On Mac 2, click the Tailscale menu bar icon → **Exit Node** → select Mac 1

> Enable **Allow local network access** alongside it if you also want Mac 2 to reach devices on Mac 1's local network (printers, NAS drives, etc.) while routing through the exit node.

**For screen sharing only:** Leave Exit Node OFF. It is not needed.

---

## Quick Reference

| Scenario | Address to enter in Screen Sharing | Extra software |
|---|---|---|
| Same Wi-Fi network | `your-mac-hostname.local` or `192.168.x.x` | None (built-in Screen Sharing) |
| Different networks (anywhere) | `100.x.x.x` or `hostname.tailnet-name.ts.net` | Tailscale on both Macs |

---

## Things to Keep in Mind

| Topic | Detail |
|---|---|
| **Lid must stay open** | Closing Mac 1's lid forces a hardware sleep that cuts Wi-Fi and drops all connections, regardless of software settings |
| **Stay on power adapter** | Sleep prevention settings only apply reliably when plugged in |
| **Tailscale auto-reconnects** | VPN On Demand ensures the tunnel reconnects automatically after any network change or wake from sleep |
| **VNC password vs login** | The VNC password is quicker for screen-only access; use system login credentials for full access including SSH |
| **After a restart** | If Auto Login is blocked (FileVault or MDM profile), remote access resumes only after someone types the password at the login screen |

---

_Tested: 2026-09-30_
