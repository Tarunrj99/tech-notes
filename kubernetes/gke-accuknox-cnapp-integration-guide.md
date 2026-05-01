# GKE + AccuKnox CNAPP — Integration & Onboarding Guide

> Onboard a Google Kubernetes Engine cluster to **AccuKnox CNAPP** end-to-end: GCP IAM, custom role, service account, VPC egress firewall (the #1 failure point), KubeArmor + agent install via Helm, multi-cluster onboarding, GCP Artifact Registry image scanning, and a real troubleshooting playbook for the common breakages.

**Purpose:** Get a GKE cluster fully reporting to AccuKnox SaaS — runtime security via KubeArmor, CIS / KIEM / risk-assessment scans, and Artifact Registry image scanning — with the firewall and agent steps that the vendor docs gloss over.
**Target:** GKE (standard or autopilot) on GCP, AccuKnox SaaS, Helm v3, `gcloud` CLI, `kubectl`.
**Tested with:** AccuKnox `kspm-runtime` chart `v0.1.25`.

[Back to repo root](../README.md) · [`kubernetes/`](./README.md) · [Repo conventions](../AGENTS.md)

---

## Table of contents

1. [Overview & architecture](#overview--architecture)
2. [Prerequisites](#prerequisites)
3. [Phase 1 — GCP account setup](#phase-1--gcp-account-setup)
4. [Phase 2 — Firewall configuration (the critical step)](#phase-2--firewall-configuration-the-critical-step)
5. [Phase 3 — GKE cluster onboarding](#phase-3--gke-cluster-onboarding)
6. [Multi-cluster onboarding](#multi-cluster-onboarding)
7. [GCP Artifact Registry integration](#gcp-artifact-registry-integration)
8. [Agent reference (what each pod does)](#agent-reference-what-each-pod-does)
9. [Troubleshooting](#troubleshooting)
10. [Quick reference commands](#quick-reference-commands)

---

## Overview & architecture

AccuKnox is a **Cloud-Native Application Protection Platform (CNAPP)** that provides:

- **Runtime security** — KubeArmor-based LSM enforcement at the kernel level
- **Policy discovery** — Auto-discovers least-permissive security policies
- **CIS benchmarking** — Automated CIS Kubernetes benchmark scans
- **KIEM scanning** — Kubernetes Infrastructure Exposure Mapping
- **Risk assessment** — Kubescape-based risk scoring
- **Container image scanning** — Vulnerability scanning via KubeShield

### High-level integration

| Layer | Component | Details |
| --- | --- | --- |
| GKE Cluster | AccuKnox agents (namespace: `agents`) | 10+ pods deployed and managed by `agents-operator` |
| Identity Layer | SPIRE mTLS | `spire.demo.accuknox.com` — `tcp:8081` (gRPC) / `tcp:9090` (health) |
| AccuKnox SaaS | CNAPP backend | `demo.accuknox.com` / `cspm.demo.accuknox.com` / `knox-gw.demo.accuknox.com` |

### Communication flow

```
GKE Cluster
   │
   │  tcp:8081 (gRPC)
   ▼
SPIRE Server (spire.demo.accuknox.com)
   │
   │  SVID Attestation
   ▼
mTLS Established
   │
   │  tcp:443
   ▼
AccuKnox SaaS (demo.accuknox.com)
```

> **Key fact:** the `agents-operator` runs an **embedded SPIRE agent** that must successfully attest to the AccuKnox SPIRE server at `spire.demo.accuknox.com:8081` before any other agent will become healthy. **This is the most common failure point** — see [Phase 2](#phase-2--firewall-configuration-the-critical-step).

---

## Prerequisites

| Requirement | Details | Verification |
| --- | --- | --- |
| AccuKnox SaaS account | Active account at `demo.accuknox.com` | Login to the portal |
| GCP project | Project with billing enabled | `gcloud projects list` |
| GKE cluster | Running cluster (standard or autopilot) | `gcloud container clusters list` |
| `kubectl` | Configured, pointing to target cluster | `kubectl cluster-info` |
| Helm v3 | Version 3.x or above | `helm version` |
| `gcloud` CLI | Authenticated as project owner / editor | `gcloud auth list` |
| GCP IAM permissions | Create Service Accounts, custom Roles, Firewall rules | IAM Admin role on project |

---

## Phase 1 — GCP account setup

> Skip Phase 1 entirely if your GCP project is already connected to AccuKnox SaaS — go straight to [Phase 2](#phase-2--firewall-configuration-the-critical-step).

### Step 1 — Enable required GCP APIs

Console: **APIs & Services → Library** → enable:

| # | API | Purpose |
| --- | --- | --- |
| 1 | Compute Engine API | VM and node management |
| 2 | Identity and Access Management (IAM) API | Service account management |
| 3 | Cloud Resource Manager API | Project-level resource access |
| 4 | Cloud Functions API | Serverless function scanning |
| 5 | Cloud KMS API | Key management visibility |
| 6 | Kubernetes Engine API | GKE cluster access |
| 7 | Cloud SQL Admin API | SQL instance visibility |

Or all at once via CLI:

```bash
gcloud services enable \
  compute.googleapis.com \
  iam.googleapis.com \
  cloudresourcemanager.googleapis.com \
  cloudfunctions.googleapis.com \
  cloudkms.googleapis.com \
  container.googleapis.com \
  sqladmin.googleapis.com \
  --project=<gcp-project-id>
```

### Step 2 — Create a custom IAM role

AccuKnox needs `storage.buckets.getIamPolicy` to audit GCS bucket policies. Create a custom role just for this.

Console: **IAM & Admin → Roles → Create Role**

- Name: `<accuknox-custom-role>` (e.g. `AccuKnoxCustomRole`)
- Add Permission → filter by Service: `storage` → add `storage.buckets.getIamPolicy`
- Click **Add**, then **Create**.

### Step 3 — Create the AccuKnox service account + JSON key

Console: **IAM & Admin → Service Accounts → Create Service Account**

1. Name: `<accuknox-reader-sa>` (e.g. `accuknox-reader`) → Continue
2. Assign **two** roles:
   - `Project → Viewer`
   - `Custom → <accuknox-custom-role>` (the role from Step 2)
3. Click **Continue → Done**
4. Open the SA → **Keys** tab → **Add Key → Create new key → JSON → Create**
5. The JSON key file downloads automatically — **store it in a secure secret manager**.

> ⚠️ **Security:** This JSON key grants read access to your GCP project. **Never commit to source control. Never share publicly.**

### Step 4 — Connect GCP to AccuKnox SaaS

In AccuKnox SaaS at `demo.accuknox.com`:

1. **Settings → Cloud Accounts → Add Account**
2. Select platform: **GCP**
3. Create a **Label** (e.g. `<your-org>-gcp-prod`) to identify assets in this account
4. Enter the following from the downloaded JSON key:
   - **Project ID**
   - **Client Email** (the SA email)
   - **Private Key** (paste the entire JSON file content)
5. Click **Connect**

> ✅ Once connected, AccuKnox will start discovering cloud assets (VMs, buckets, SQL instances, GKE clusters).

---

## Phase 2 — Firewall configuration (the critical step)

> 🔴 **Most common cause of integration failure.**
> AccuKnox agents inside GKE must connect to AccuKnox SPIRE for identity attestation. Production VPCs typically have a **default deny-all egress** policy. If port `8081` (SPIRE gRPC) is blocked, **every agent fails** — including cascade failures in `kubeshield` and all scan jobs.

### Step 5 — Required ports

| Destination host | Port | Protocol | Purpose | Required |
| --- | --- | --- | --- | --- |
| `spire.demo.accuknox.com` | `9090` | TCP | SPIRE server health check | Yes |
| `spire.demo.accuknox.com` | `8081` | TCP (gRPC) | SPIRE agent ↔ server attestation — **ROOT CAUSE if blocked** | Yes (critical) |
| `knox-gw.demo.accuknox.com` | `3000` | TCP | Knox Gateway — kubeshield data relay | Yes |
| `cspm.demo.accuknox.com` | `443` | HTTPS | Scan results upload (CIS, KIEM, risk) | Usually open |
| `demo.accuknox.com` | `443` | HTTPS | Agent registration | Usually open |

### Step 6 — Inspect your existing egress rules first

```bash
# List all egress firewall rules
gcloud compute firewall-rules list \
  --filter="direction=EGRESS" \
  --format="table(name,direction,allowed[].map().firewall_rule().list():label=ALLOW,destinationRanges,priority,targetServiceAccounts)" \
  --project=<gcp-project-id>

# Find which service account your GKE nodes use
gcloud container clusters describe <cluster-name> \
  --region=<region> \
  --project=<gcp-project-id> \
  --format="value(nodeConfig.serviceAccount)"

# Find your VPC name (important for custom VPCs)
gcloud compute networks list --project=<gcp-project-id>

# Resolve current AccuKnox SPIRE IPs (these can rotate)
dig +short spire.demo.accuknox.com
```

### Step 7 — Create the AccuKnox egress firewall rule

Create a dedicated, narrowly-scoped egress rule. Replace placeholders with values from Step 6 — including the **current** SPIRE IPs (from `dig`).

```bash
gcloud compute firewall-rules create allow-egress-accuknox-spire \
  --project=<gcp-project-id> \
  --network=<your-vpc-name> \
  --direction=EGRESS \
  --action=ALLOW \
  --rules=tcp:9090,tcp:8081,tcp:3000 \
  --destination-ranges=<accuknox-spire-ip-1>/32,<accuknox-spire-ip-2>/32,<accuknox-spire-ip-3>/32 \
  --target-service-accounts=<gke-node-sa>@<gcp-project-id>.iam.gserviceaccount.com \
  --priority=1000 \
  --description="Allow AccuKnox SPIRE and Knox Gateway from GKE nodes"
```

> ⚠️ **Custom VPC:** If your project uses a custom VPC (not `default`), you **must** include `--network=<your-vpc-name>`. Omitting causes:
> ```
> ERROR: The resource 'projects/.../global/networks/default' was not found
> ```

> 📌 **Production best practice:**
> - Scope to `--target-service-accounts` (not `--target-tags`) for precise control.
> - Scope `--destination-ranges` to specific AccuKnox IPs rather than `0.0.0.0/0`.
> - Re-run `dig +short spire.demo.accuknox.com` periodically — IPs can change. Update the rule when they do.
> - If multiple clusters in the same VPC use the same node SA, **one rule covers all of them**.

---

## Phase 3 — GKE cluster onboarding

### Step 8 — Register the cluster in AccuKnox SaaS

In AccuKnox SaaS:

1. **Settings → Manage Cluster → Onboard Now**
2. Enter a unique cluster name (e.g. `<cluster-name>` or `<cluster-name>-<region>`)
3. Copy the generated **Join Token** — it is used **once** for SPIRE attestation.

> ⚠️ Join tokens are **cluster-specific** and **single-use**. Each GKE cluster requires its own unique join token. Never reuse a join token across clusters.

### Step 9 — Get kubectl context for the target cluster

```bash
gcloud container clusters get-credentials <cluster-name> \
  --region=<region> \
  --project=<gcp-project-id>

kubectl config current-context
kubectl get nodes
```

### Step 10 — Check for KubeArmor conflicts (important)

The AccuKnox Helm chart installs its own KubeArmor operator. If KubeArmor was previously installed standalone (via `karmor install`), it must be uninstalled first to avoid Helm ownership conflicts.

```bash
helm list -A | grep kubearmor

# If found, uninstall it
helm uninstall kubearmor-operator -n kubearmor
```

> 🔴 If you skip this step, Helm fails with:
> ```
> ClusterRole "kubearmor-operator-clusterrole" exists and cannot be imported
> into the current release: invalid ownership metadata
> ```

### Step 11 — Install the AccuKnox agents via Helm

Replace every `<placeholder>`. The chart installs ~10 pods into the `agents` namespace.

```bash
helm upgrade --install agents oci://public.ecr.aws/k9v9d5v2/kspm-runtime \
  -n agents --create-namespace \
  --set global.agents.enabled=true \
  --set global.agents.joinToken="<join-token-from-accuknox>" \
  --set global.agents.url="demo.accuknox.com" \
  --set kubearmor-operator.enabled=true \
  --set kubearmor-operator.autoDeploy=true \
  --set global.enableJobsUrl=true \
  --set global.kiem.enabled=true \
  --set global.riskassessment.enabled=true \
  --set global.cis.enabled=true \
  --set global.tenantId="<accuknox-tenant-id>" \
  --set global.authToken="<accuknox-auth-token>" \
  --set global.clusterName="<cluster-name>" \
  --set global.cronTab="57 11 * * *" \
  --set global.label="<your-label>" \
  --set global.inClusterScan.enabled=true \
  --version v0.1.25
```

### Helm parameter reference

| Parameter | Description | Where to find it |
| --- | --- | --- |
| `global.agents.joinToken` | One-time SPIRE join token for **this** cluster | AccuKnox SaaS → Settings → Manage Cluster → Onboard Now |
| `global.authToken` | JWT bearer token for AccuKnox API authentication | AccuKnox SaaS → Settings → Access Keys |
| `global.tenantId` | Your AccuKnox tenant ID (numeric) | AccuKnox SaaS → Settings → Profile |
| `global.clusterName` | Unique cluster name in the AccuKnox dashboard | The name you chose in Step 8 |
| `global.label` | Label for grouping/filtering assets | AccuKnox SaaS → Labels (or create new) |
| `global.cronTab` | Cron schedule for periodic scans (CIS / KIEM / risk) | Set based on your scan-frequency requirement |
| `global.authToken` (empty) | If left empty, all scan jobs fail with HTTP 400 | Always provide a valid token |

### Step 12 — Verify the installation

```bash
# Watch pods come up in real time
kubectl get po -n agents -w

# Static snapshot after 2–3 minutes
kubectl get po -n agents
```

### Expected final pod state

| Pod name pattern | Status | Purpose |
| --- | --- | --- |
| `agents-operator-*` | `Running 1/1` | Core operator — manages all agents, runs SPIRE agent on port 9091 |
| `discovery-engine-*` | `Running 2/2` | Auto-generates least-permissive security policies |
| `feeder-service-*` | `Running 1/1` | Collects KubeArmor runtime events and relays to AccuKnox |
| `shared-informer-agent-*` | `Running 1/1` | Watches Kubernetes API — gathers cluster metadata |
| `policy-enforcement-agent-*` | `Running 1/1` | Applies AccuKnox policies to cluster workloads |
| `kubeshield-controller-manager-*` | `Running 1/1` | Container image vulnerability scanning coordinator |
| `kubearmor-operator-*` | `Running 1/1` | Manages KubeArmor DaemonSet lifecycle |
| `kubearmor-relay-*` | `Running 1/1` | Aggregates KubeArmor events from all nodes |
| `kubearmor-controller-*` | `Running 1/1` | Webhook controller for KubeArmor policy annotations |
| `kubearmor-bpf-containerd-*` | `Running 1/1` (one per node) | Per-node BPF-based runtime enforcement engine |
| `cis-k8s-job-*` | `Completed` | CIS Kubernetes benchmark scan |
| `kiem-job-*` | `Completed` | Kubernetes Infrastructure Exposure Map scan |
| `k8s-risk-assessment-job-*` | `Completed` | Kubescape risk assessment |
| `kubearmor-snitch-*` | `Completed` | One-time per-node LSM type detection |

### Confirm SPIRE registration

```bash
kubectl logs -n agents -l app=agents-operator | grep -E "(spire|SVID|live)"
```

Expected success messages:

```
"Spire server is live at spire.demo.accuknox.com"
"Starting spire-agent with join_token: ..."
"SVID loaded spiffe_id=\"spiffe://accuknox.com/spire/agent/join_token/...\""
"Starting Workload and SDS APIs address=\"0.0.0.0:9091\""
```

### Verify in the AccuKnox dashboard

**AccuKnox SaaS → Inventory → Clusters** — your cluster should appear with:

- ✅ Cluster name visible, status active
- ✅ Node count matches your GKE cluster
- ✅ Workloads (pods, namespaces, deployments) listed
- ✅ CIS benchmark results populated
- ✅ Risk assessment score available
- ✅ KIEM network exposure map available

> ✅ **Integration complete.** Runtime security is active via KubeArmor; periodic scans run on the configured cron.

---

## Multi-cluster onboarding

To onboard additional GKE clusters (e.g. same cluster name in different regions), repeat **Steps 8–12** for each cluster. Each cluster needs its **own** join token but can share the same auth token, tenant ID, and label.

### Switch kubectl context to the new cluster

```bash
gcloud container clusters get-credentials <new-cluster-name> \
  --region=<new-region> \
  --project=<gcp-project-id>

kubectl config current-context

# Confirm agents namespace is empty before installing
kubectl get po -n agents

# Run the same Helm install — NEW join token, DIFFERENT clusterName
helm upgrade --install agents oci://public.ecr.aws/k9v9d5v2/kspm-runtime \
  -n agents --create-namespace \
  --set global.agents.joinToken="<new-join-token-for-this-cluster>" \
  --set global.clusterName="<unique-name-for-this-region-cluster>" \
  # ... all other params identical to first cluster ...
  --version v0.1.25
```

> ℹ️ **Firewall rule coverage:** if both clusters use the same GCP service account and VPC, the firewall rule from Step 7 already covers them — no additional firewall changes needed.

### Fix RBAC for multi-cluster (KubeArmor snitch)

When onboarding a second cluster where a previous standalone `karmor install` was done and removed, the `kubearmor-snitch-binding` ClusterRoleBinding may still point to the old `kubearmor` namespace instead of `agents`.

**Symptom in pod logs:**

```
Error: nodes "<gke-node-name>" is forbidden:
User "system:serviceaccount:agents:kubearmor-snitch"
cannot patch resource "nodes" in API group "" at the cluster scope
```

**Fix — add the `agents` namespace to the binding:**

```bash
kubectl patch clusterrolebinding kubearmor-snitch-binding \
  --type='json' \
  -p='[{"op": "add", "path": "/subjects/-", "value": {"kind": "ServiceAccount", "name": "kubearmor-snitch", "namespace": "agents"}}]'

# Force-restart the crashing snitch pods so they pick up the new permissions
kubectl get pods -n agents | grep snitch | awk '{print $1}' \
  | xargs kubectl delete pod -n agents
```

---

## GCP Artifact Registry integration

AccuKnox can scan container images stored in **GCP Artifact Registry (GAR)** for CVEs, misconfigurations, and vulnerabilities. This section covers wiring up GAR using the existing AccuKnox SA, **scoped to scan only `:latest` images** so the license cost stays sane.

> 💰 **Cost control:** Scanning all tags across large repositories (multi-TB backend, multi-GB frontend, etc.) consumes significant license credits. The `*:latest` pattern restricts AccuKnox to only the most recent image per repository — typically a handful of images instead of thousands.

### Step 1 — Grant Artifact Registry Reader role to the AccuKnox SA

```bash
gcloud projects add-iam-policy-binding <gcp-project-id> \
  --member="serviceAccount:<accuknox-reader-sa>@<gcp-project-id>.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.reader" \
  --condition=None
```

### Step 2 — Generate a service-account JSON key (or reuse the existing one)

If the SA you connected in Phase 1 doesn't already have a JSON key you can use, generate one:

```bash
gcloud iam service-accounts keys create accuknox-gar-key.json \
  --iam-account=<accuknox-reader-sa>@<gcp-project-id>.iam.gserviceaccount.com \
  --project=<gcp-project-id>
```

> ⚠️ Treat the resulting JSON key as a secret. Store in a secret manager. Never commit.

### Step 3 — Configure the registry in AccuKnox SaaS

**AccuKnox SaaS → Settings → Integrations → Registry → Add**

| Field | Value | Notes |
| --- | --- | --- |
| Registry Name | `<your-registry-name>` | Unique name in AccuKnox |
| Label | `<your-label>` | Link to the existing GCP cloud-account label |
| Registry Type | **Google Artifact Registry (GAR)** | Select from dropdown |
| Description | `<short description of what this registry holds>` | Free text |
| GAR Region | `us` (or whatever multi-region your repos live in) | Must match repo location |
| Service Account JSON Key | Paste the full contents of `accuknox-gar-key.json` | The JSON key from Step 2 |

### Step 4 — Advanced settings — scan strategy

| Setting | Value | Reason |
| --- | --- | --- |
| Name / Tag Pattern | `*:latest` | Only `:latest` images scanned — prevents license-cost explosion |
| Schedule | `06 03 * * *` (or similar off-peak cron) | Daily, off-peak |
| Trigger scan on save | ✅ Enabled | Runs an immediate scan on first save to validate connectivity |

> ⚠️ **Tag pattern warning:** Do **NOT** change `*:latest` to `*:*` or remove the pattern. Scanning all tags across large repositories scans thousands of historical image versions, consuming massive license credits.

### IAM permissions summary for the AccuKnox SA

| Role | Purpose | Scope |
| --- | --- | --- |
| `roles/viewer` | Read access to all GCP project resources | Project |
| `roles/artifactregistry.reader` | Pull / read container images for scanning | Project |
| `<accuknox-custom-role>` | `storage.buckets.getIamPolicy` — GCS bucket IAM audit | Project |

Results appear under **AccuKnox → Inventory → Container Images** once the first scan completes.

---

## Agent reference (what each pod does)

| Agent | Type | Replicas | Purpose |
| --- | --- | --- | --- |
| `agents-operator` | Deployment | 1 | Core operator. Bootstraps embedded SPIRE agent, manages lifecycle of all other agents. Exposes SPIRE workload API on `:9091`. |
| `discovery-engine` | Deployment | 1 (2 containers) | Analyzes workloads and auto-discovers least-permissive KubeArmor policy sets from runtime data. |
| `feeder-service` | Deployment | 1 | Subscribes to `kubearmor-relay` gRPC stream and feeds runtime security events to AccuKnox SaaS and `discovery-engine`. |
| `shared-informer-agent` | Deployment | 1 | Watches Kubernetes API server for state changes — pods/nodes/namespaces/services — and syncs metadata to AccuKnox. |
| `policy-enforcement-agent` | Deployment | 1 | Receives security policies from AccuKnox SaaS and applies KubeArmor labels and CRD-based policies. |
| `kubeshield-controller-manager` | Deployment | 1 | Orchestrates container image vulnerability scanning. Uses SPIRE mTLS (via `agents-operator:9091`) and Knox Gateway (`:3000`). |
| `kubearmor-operator` | Deployment | 1 | Manages KubeArmor DaemonSet lifecycle — deploys, upgrades, configures KubeArmor based on node capabilities. |
| `kubearmor-relay` | Deployment | 1 | Central relay aggregating KubeArmor audit/enforcement events from all nodes; exposes consolidated gRPC stream. |
| `kubearmor-controller` | Deployment | 1 | Admission webhook controller for KubeArmor policy annotations, mutations, CRD validation. |
| `kubearmor-bpf-containerd` | DaemonSet | 1 per node | Per-node BPF-based enforcement engine. Uses LSM (BPF/AppArmor/SELinux) to enforce process, file, network restrictions at kernel level. |
| `cis-k8s-job` | CronJob | scheduled | Runs `kube-bench` CIS benchmark; uploads results to `cspm.demo.accuknox.com`. |
| `kiem-job` | CronJob | scheduled | Kubernetes Infrastructure Exposure Map — maps network exposure of all workloads. |
| `k8s-risk-assessment-job` | CronJob | scheduled | Runs Kubescape risk assessment; uploads scored findings. |
| `kubearmor-snitch` | DaemonSet Job | 1 per node (once) | One-time per-node job. Detects LSM capabilities and patches node labels for KubeArmor. |

---

## Troubleshooting

### Issue 1 — `agents-operator` repeatedly fails SPIRE health check

**Symptom:**

```
"Failed to get spire agent status. Attempt 1 failed..."
"health check failed, spire server might not be ready"
```

**Cause:** Port `8081` (SPIRE gRPC) and/or `9090` (SPIRE health) blocked by VPC egress firewall.

**Fix:**

```bash
gcloud compute firewall-rules describe allow-egress-accuknox-spire
# Verify tcp:8081, tcp:9090, tcp:3000 are listed in the ALLOW column

kubectl rollout restart deployment agents-operator -n agents

kubectl logs -n agents -l app=agents-operator | grep "spire server is live"
```

### Issue 2 — `kubeshield-controller-manager` in CrashLoopBackOff

**Symptom in logs:**

```
"SPIRE: unable to create X509Source: context deadline exceeded"
```

**Cause:** kubeshield tries to get an SVID from the SPIRE workload API at `tcp://<agents-operator-ip>:9091`. This fails because `agents-operator` hasn't completed SPIRE registration (root cause: blocked port 8081).

**Fix:** Resolve **Issue 1** first. kubeshield auto-stabilizes once `agents-operator` successfully bootstraps the SPIRE agent.

### Issue 3 — Scan jobs fail with `unexpected status code: 400`

**Symptom in `kiem-job` / `cis-k8s-job` / `k8s-risk-assessment-job` logs:**

```
level=error msg="failed to publish report" error="unexpected status code: 400"
level=fatal msg="unexpected status code: 400"
```

**Cause A:** `global.authToken` was empty/missing in the Helm install.
**Fix A:**

```bash
helm upgrade agents oci://public.ecr.aws/k9v9d5v2/kspm-runtime \
  -n agents \
  --set global.authToken="<valid-auth-token>" \
  --reuse-values \
  --version v0.1.25
```

**Cause B:** Cluster SPIRE registration hasn't completed — cluster/label doesn't exist in AccuKnox yet.
**Fix B:** Resolve the SPIRE port issue (Issue 1). Jobs succeed on next cron run after SPIRE registration completes.

### Issue 4 — Helm install fails with ClusterRole ownership conflict

**Error:**

```
Error: Unable to continue with install: ClusterRole "kubearmor-operator-clusterrole"
exists and cannot be imported into the current release: invalid ownership metadata;
annotation validation error: key "meta.helm.sh/release-name" must equal "agents"
```

**Cause:** KubeArmor was previously installed via standalone `karmor install` as a separate Helm release.

**Fix:**

```bash
helm list -A | grep kubearmor
helm uninstall kubearmor-operator -n kubearmor

# Re-run the AccuKnox Helm install
```

### Issue 5 — `kubearmor-snitch` pods in CrashLoopBackOff (`cannot patch nodes`)

**Error in pod logs:**

```
nodes is forbidden: User system:serviceaccount:agents:kubearmor-snitch
cannot patch resource nodes in API group at the cluster scope
```

**Cause:** `kubearmor-snitch-binding` ClusterRoleBinding still points to the `kubearmor` namespace SA instead of the `agents` namespace.

**Fix:**

```bash
kubectl patch clusterrolebinding kubearmor-snitch-binding \
  --type='json' \
  -p='[{"op": "add", "path": "/subjects/-", "value": {"kind": "ServiceAccount", "name": "kubearmor-snitch", "namespace": "agents"}}]'

kubectl get pods -n agents | grep snitch | awk '{print $1}' \
  | xargs kubectl delete pod -n agents
```

### Issue 6 — `gcloud` firewall create fails — `networks/default not found`

**Error:**

```
ERROR: The resource 'projects/.../global/networks/default' was not found
```

**Cause:** Project uses a custom VPC; `--network` flag was omitted.

**Fix:**

```bash
gcloud compute networks list --project=<gcp-project-id>

# Then re-run the firewall command with --network=<your-custom-vpc>
gcloud compute firewall-rules create allow-egress-accuknox-spire \
  --network=<your-custom-vpc> \
  ...
```

---

## Quick reference commands

### Cluster context

```bash
gcloud container clusters list --project=<gcp-project-id>

gcloud container clusters get-credentials <cluster-name> \
  --region=<region> \
  --project=<gcp-project-id>

kubectl config current-context
```

### Agent health checks

```bash
kubectl get po -n agents
kubectl get po -n agents -w

kubectl logs -n agents -l app=agents-operator | grep -iE "(spire|live|SVID|failed)"

kubectl logs -n agents -l app=kubeshield-controller-manager --previous

kubectl logs -n agents -l job-name=kiem-job
kubectl logs -n agents -l job-name=cis-k8s-job
kubectl logs -n agents -l job-name=k8s-risk-assessment-job
```

### Helm operations

```bash
helm list -n agents

helm upgrade agents oci://public.ecr.aws/k9v9d5v2/kspm-runtime \
  -n agents \
  --set global.authToken="<new-token>" \
  --reuse-values \
  --version v0.1.25

helm uninstall agents -n agents
```

### Firewall verification

```bash
gcloud compute firewall-rules list \
  --filter="direction=EGRESS" \
  --project=<gcp-project-id>

gcloud compute firewall-rules describe allow-egress-accuknox-spire \
  --project=<gcp-project-id>

dig +short spire.demo.accuknox.com
```

### Restart after fixes

```bash
kubectl rollout restart deployment agents-operator -n agents
kubectl rollout restart deployment kubeshield-controller-manager -n agents

# Delete failed jobs (cron will re-create on next schedule)
kubectl delete jobs -n agents --all
```

---

## Reference

- [AccuKnox documentation](https://help.accuknox.com/)
- [KubeArmor — runtime security](https://kubearmor.io/)
- [SPIRE / SPIFFE — workload identity](https://spiffe.io/)
- [GCP — Artifact Registry IAM roles](https://cloud.google.com/artifact-registry/docs/access-control)
- [GCP — VPC firewall rules](https://cloud.google.com/firewall/docs/firewalls)
