# Setting up GUI mode in Ubuntu Linux 26.04 through CLI

A complete, copy-paste ready guide to install a graphical desktop (XFCE) on a headless Ubuntu Linux VM and access it remotely over RDP.

Works on **any Ubuntu 26.04 VM** — local (VirtualBox / VMware / Hyper-V), bare-metal, or cloud (AWS EC2, GCP Compute Engine, Azure VM, DigitalOcean, Linode, Hetzner, etc.). Only the SSH connection method differs by environment.

| Item | Value |
|---|---|
| OS | Ubuntu 26.04 LTS (Resolute Raccoon) |
| Desktop | XFCE 4.20 (lightweight, works flawlessly with xrdp) |
| Remote access | RDP (port 3389) via Microsoft Remote Desktop / Windows App |

---

# PART 1 — CONNECT TO THE VM (admin / installer)

All install commands below run on the VM as a sudo-capable user. Connect via whichever method matches your setup:

### Option A — Standard SSH (any cloud or local VM)

```bash
ssh -i <path-to-private-key> <username>@<vm-public-ip>
```

### Option B — GCP (Google Cloud) with `gcloud` CLI authenticated

```bash
gcloud compute ssh --zone "<zone>" "<vm-name>" --project "<gcp-project-id>"
```

### Option C — AWS EC2 with `.pem` key

```bash
ssh -i <path-to-key>.pem ubuntu@<ec2-public-ip>
```

### Option D — Azure VM with `az ssh`

```bash
az ssh vm --resource-group <rg-name> --name <vm-name>
```

### Option E — Local VM (VirtualBox / VMware / Hyper-V)

```bash
ssh <username>@<vm-ip-on-host-network>
```

You're now in a shell on the VM. Continue with the steps below.

---

# PART 2 — INSTALL XFCE + xrdp (the GUI)

> Why XFCE: GNOME on Ubuntu 26.04 uses systemd-managed sessions (`gnome-session@ubuntu.target`) that exit immediately when launched by xrdp, causing instant disconnect. XFCE has no such issue and is the standard production-grade desktop for xrdp.

```bash
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y

# Install XFCE desktop, xrdp, and required helpers
sudo apt-get install -y xfce4 xfce4-goodies xfce4-terminal dbus-x11 xrdp

# Make sure no display manager auto-starts at boot (avoids session conflict with xrdp)
sudo systemctl set-default multi-user.target

# Enable + start xrdp
sudo systemctl enable --now xrdp
sudo adduser xrdp ssl-cert || true

# Make XFCE the system-wide xrdp session (every user gets XFCE)
sudo cp /etc/xrdp/startwm.sh /etc/xrdp/startwm.sh.bak.$(date +%s)
sudo tee /etc/xrdp/startwm.sh >/dev/null <<'EOF'
#!/bin/sh
if test -r /etc/profile; then . /etc/profile; fi
if test -r ~/.profile; then . ~/.profile; fi
exec /usr/bin/startxfce4
EOF
sudo chmod +x /etc/xrdp/startwm.sh

# Per-user .xsession fallback for every existing and future user
echo "xfce4-session" | sudo tee /etc/skel/.xsession
for u in $(awk -F: '($3>=1000)&&($3<65000){print $1}' /etc/passwd); do
  home=$(getent passwd "$u" | cut -d: -f6)
  if [ -d "$home" ]; then
    echo "xfce4-session" | sudo tee "$home/.xsession" >/dev/null
    sudo chown "$u":"$u" "$home/.xsession"
    sudo chmod +x "$home/.xsession"
  fi
done

sudo systemctl restart xrdp
```

After this, RDP on port 3389 works for any user with a Linux password.

---

# PART 3 — INSTALL APPLICATIONS

> **Mandatory** for the basic use case (RDP + Chrome + VS Code + Claude): **3.1, 3.2, 3.4**
> **Recommended:** 3.5
> **Optional** (only if your team needs cloud/k8s/container work): **3.3**


## 3.1 Google Chrome (default browser)

```bash
export DEBIAN_FRONTEND=noninteractive
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | \
  sudo gpg --dearmor --yes -o /etc/apt/keyrings/google-chrome.gpg
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] https://dl.google.com/linux/chrome/deb/ stable main" | \
  sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update -y
sudo apt-get install -y google-chrome-stable

# Set Chrome as system default browser
sudo update-alternatives --install /usr/bin/x-www-browser x-www-browser /usr/bin/google-chrome-stable 200
sudo update-alternatives --install /usr/bin/gnome-www-browser gnome-www-browser /usr/bin/google-chrome-stable 200
sudo update-alternatives --set x-www-browser /usr/bin/google-chrome-stable
xdg-mime default google-chrome.desktop x-scheme-handler/http x-scheme-handler/https
```

## 3.2 VS Code + Cloud Code extension

```bash
export DEBIAN_FRONTEND=noninteractive
sudo apt-get install -y wget gpg apt-transport-https
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | \
  sudo gpg --dearmor --yes -o /usr/share/keyrings/packages.microsoft.gpg
echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | \
  sudo tee /etc/apt/sources.list.d/vscode.list
sudo apt-get update -y
sudo apt-get install -y code

# Install Cloud Code extension for the current user
# (run as the user who will use VS Code; pulls Gemini Code Assist as dependency)
code --install-extension googlecloudtools.cloudcode --force
```

## 3.3 Google Cloud SDK + kubectl + skaffold + minikube + Docker — *Optional*

> **Skip this section unless your team needs cloud / Kubernetes / container work on the VM.**
> None of these are required for RDP, VS Code, or Claude Code. Install only if needed:
> - `gcloud` — to run Google Cloud commands from inside the VM
> - `kubectl` — to manage Kubernetes clusters
> - `skaffold` — for Cloud Code's "Deploy & Run on Kubernetes" feature
> - `minikube` — to run a local Kubernetes cluster on the VM
> - `docker` — to build / run containers on the VM

```bash
export DEBIAN_FRONTEND=noninteractive
sudo install -m 0755 -d /etc/apt/keyrings

# Google Cloud SDK repo
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
  sudo gpg --dearmor --yes -o /etc/apt/keyrings/cloud.google.gpg
echo "deb [signed-by=/etc/apt/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
  sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list

# Kubernetes apt repo
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | \
  sudo gpg --dearmor --yes -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /" | \
  sudo tee /etc/apt/sources.list.d/kubernetes.list

# Docker apt repo
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu resolute stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list

sudo apt-get update -y
sudo apt-get install -y \
  google-cloud-cli \
  google-cloud-cli-gke-gcloud-auth-plugin \
  kubectl \
  docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# Skaffold (latest binary)
curl -fsSLo /tmp/skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
sudo install -m 0755 /tmp/skaffold /usr/local/bin/skaffold
rm -f /tmp/skaffold

# Minikube (latest binary)
curl -fsSLo /tmp/minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install -m 0755 /tmp/minikube /usr/local/bin/minikube
rm -f /tmp/minikube

# Add active user to docker group (no sudo needed for docker after re-login)
sudo usermod -aG docker $USER
```

## 3.4 Claude Code (system-wide)

```bash
# Install for the current user
curl -fsSL https://claude.ai/install.sh | bash

# Make it available to ALL users on the VM
CLAUDE_BIN=$(readlink -f ~/.local/bin/claude)
sudo install -m 0755 -o root -g root "$CLAUDE_BIN" /usr/local/bin/claude
sudo chmod a+rx /usr/local/bin/claude
```

## 3.5 Supporting developer packages — *Recommended*

> Useful CLI tools (git, tmux, jq, ripgrep, Node.js, Python, etc.). Recommended but not strictly required for the GUI / Claude / VS Code use case.

```bash
export DEBIAN_FRONTEND=noninteractive
sudo apt-get install -y \
  git git-lfs build-essential \
  python3-pip python3-venv pipx \
  tmux htop vim jq tree unzip zip \
  ripgrep fd-find bat fzf zsh \
  terminator firefox xclip xsel \
  net-tools dnsutils ca-certificates

# Node.js 20 (LTS) from NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt-get install -y nodejs

# Global JS package managers
sudo npm install -g yarn pnpm
```

---

# PART 4 — END-USER ACCESS GUIDE

## To access the VM in GUI Mode

1. **Set a Linux password** (one-time, only if you don't already have one) — in your SSH terminal, run:

   ```
   sudo passwd $USER
   ```

2. **Install an RDP client on your computer** (free):

   - **Mac:** Windows App → https://apps.apple.com/us/app/windows-app/id1295203466?mt=12
   - **Windows:** built-in **Remote Desktop Connection** (search `mstsc`)
   - **Linux:** Remmina (`sudo apt install remmina remmina-plugin-rdp`)

3. **Add a new connection** in your RDP client:

   - Host / PC name: `<vm-public-ip>`
   - Username: `<your-username>`
   - Password: `<the password you set in step 1>`

4. **Connect → Continue on certificate warning → desktop opens.**

---

## After connecting to VM via Windows App

### To Open / Access Chrome

- Top-left menu (mouse icon) → **Internet → Google Chrome**
- Or: right-click desktop → **Open Terminal Here** → type: `google-chrome &`

### To Open / Access VS Code

- Top-left menu → **Development → Visual Studio Code**
- Or in terminal: `code &`
- Open your project: **File → Open Folder**

### Access Claude in VS Code (extension already installed)

1. Click the **Claude icon** in the left sidebar (Anthropic logo)
2. First time: click **Sign in** → Chrome opens → log in to Anthropic → approve → comes back to VS Code
3. Chat panel opens on the right side
4. Type your prompt → press **Enter**
5. Claude can read/edit files in the open project automatically

### Access Claude in Terminal (CLI)

```
claude
```

First time only: copy the URL → open in Chrome → log in to Anthropic → paste back the code.

---

# PART 5 — ADMIN: ONBOARDING A NEW USER

For each new user who needs RDP access:

```bash
# 1. Create the user (skip if they already exist)
sudo adduser <username>

# 2. Set a password (this is what they type in Windows App)
sudo passwd <username>

# 3. (Optional) Give them sudo
sudo usermod -aG sudo <username>

# 4. Add to docker group so they can run docker without sudo
sudo usermod -aG docker <username>
```

Each user automatically gets:

- XFCE desktop on RDP login (system-wide `/etc/xrdp/startwm.sh`)
- Claude Code (`/usr/local/bin/claude`)
- All cloud / dev tools
- Their own isolated home directory and Anthropic auth

---

# PART 6 — FIREWALL / NETWORK

Whichever environment you're in, **TCP port 3389 must be reachable** from your laptop to the VM for RDP to work.

| Port | Purpose | Required |
|---|---|---|
| 22 | SSH (admin access) | yes |
| 3389 | RDP (GUI access) | yes |

### Open port 3389 — by environment

#### GCP (Compute Engine)

```bash
gcloud compute firewall-rules create allow-rdp \
  --project <gcp-project-id> \
  --direction INGRESS --priority 1000 --network default \
  --allow tcp:3389 --source-ranges <your-public-ip>/32
```

#### AWS EC2

In the EC2 console → Security Group → **Add inbound rule** → Type: RDP, Source: `<your-public-ip>/32`.

Or via CLI:

```bash
aws ec2 authorize-security-group-ingress \
  --group-id <sg-id> --protocol tcp --port 3389 --cidr <your-public-ip>/32
```

#### Azure

```bash
az network nsg rule create \
  --resource-group <rg-name> --nsg-name <nsg-name> --name allow-rdp \
  --priority 1000 --direction Inbound --access Allow \
  --protocol Tcp --destination-port-ranges 3389 \
  --source-address-prefixes <your-public-ip>/32
```

#### Local VM / on-prem

Configure your home router or `iptables` / `ufw` on the host to forward / allow TCP 3389.

```bash
sudo ufw allow from <your-public-ip>/32 to any port 3389 proto tcp
```

> **Security note:** Always scope the source to your specific IP (`<your-public-ip>/32`). Find your IP with `curl -4 ifconfig.me`. Never expose RDP to `0.0.0.0/0` — it's a primary brute-force target.

---

# PART 7 — INSTALLED SOFTWARE SUMMARY

| Category | Tool | Version |
|---|---|---|
| Desktop | XFCE + goodies | 4.20.1 |
| | xrdp | active |
| | Google Chrome | 147.0.7727.137 |
| | Firefox | (default Ubuntu) |
| Editors | VS Code | 1.118.1 |
| | Cloud Code extension | 2.39.0 |
| | Gemini Code Assist | 2.79.0 |
| AI CLI | Claude Code | 2.1.123 |
| Cloud SDKs | gcloud | 566.0.0 |
| | gke-gcloud-auth-plugin | 566.0.0 |
| | kubectl | v1.35.3 |
| | skaffold | v2.19.0 |
| | minikube | v1.38.1 |
| Containers | Docker CE + Buildx + Compose | 29.4.1 |
| | containerd | 2.2.3 |
| Languages | Node.js | 20.20.2 |
| | npm + yarn + pnpm | 10.8.2 / latest |
| | Python + pip + pipx + venv | 3.14.4 |
| Dev tools | git, git-lfs, build-essential, jq, ripgrep, fd-find, bat, fzf, tmux, htop, vim, tree, zsh, xclip, terminator | latest |
| Network debug | net-tools, dnsutils | latest |

---

# PART 8 — TROUBLESHOOTING

## RDP disconnects right after the cert warning

Most common cause: wrong username (must match your Linux account exactly).
Second cause: a leftover GNOME / GDM session is conflicting. Run:

```bash
sudo systemctl stop gdm3 2>/dev/null || true
sudo systemctl disable gdm3 2>/dev/null || true
sudo systemctl set-default multi-user.target
sudo systemctl restart xrdp
```

## `claude: command not found` in VS Code terminal

Should be at `/usr/local/bin/claude`. If a new terminal still doesn't pick it up:

```bash
~/.local/bin/claude         # quick fix
# or
source ~/.bashrc && claude  # reload PATH
```

## Docker requires sudo

```bash
sudo usermod -aG docker $USER
# then log out and log back in
```

## Reset xrdp / inspect logs

```bash
sudo systemctl restart xrdp
sudo tail -50 /var/log/xrdp.log
sudo tail -50 /var/log/xrdp-sesman.log
tail -50 ~/.xsession-errors
```

---

# PART 9 — KEY FILE LOCATIONS

| File | Purpose |
|---|---|
| `/etc/xrdp/startwm.sh` | Launches XFCE for every RDP session |
| `/etc/xrdp/startwm.sh.bak.*` | Backup of original script |
| `/etc/skel/.xsession` | Default session for new users |
| `~/.xsession` | Per-user session override |
| `/usr/local/bin/claude` | System-wide Claude Code binary |
| `~/.claude/` | Per-user Claude auth + history |
| `/etc/apt/keyrings/` | Third-party APT GPG keys |
| `/var/log/xrdp.log` + `/var/log/xrdp-sesman.log` | xrdp diagnostics |
| `~/.xsession-errors` | Per-user X session error log |

---

_Setup completed: April 30, 2026_
_Last updated: May 1, 2026_
