# GKE Kubernetes RBAC — DevOps User Access Setup Guide

> Grant a user **operational (DevOps) access** on a GKE cluster — port-forward, log view, exec, pod delete, deployment restart, Helm release management — **without** giving them full admin or any application creation/modification rights. Includes a complete drop-in `ClusterRole` + `ClusterRoleBinding` and a full RBAC reference for extending it.

**Purpose:** Provide read + targeted-write Kubernetes access scoped to debugging, restart, and Helm-uninstall operations only.
**Target:** GKE clusters using Google IAM identities (Workload Identity not required for this — IAM principal is the user's Google account).
**Tested on:** GKE on `gcloud container clusters get-credentials`, kubectl 1.28+, RBAC API `rbac.authorization.k8s.io/v1`.

[Back to repo root](../README.md) · [`kubernetes/`](./README.md) · [Repo conventions](../AGENTS.md)

---

## Table of contents

1. [The two access layers (IAM vs RBAC)](#the-two-access-layers-iam-vs-rbac)
2. [GCP IAM layer — what's needed](#gcp-iam-layer--whats-needed)
3. [The two YAML manifests](#the-two-yaml-manifests)
4. [Apply commands](#apply-commands)
5. [What the user CAN do](#what-the-user-can-do)
6. [What the user CANNOT do](#what-the-user-cannot-do)
7. [Optional permission add-ons (by scenario)](#optional-permission-add-ons-by-scenario)
8. [Complete RBAC parameters reference](#complete-rbac-parameters-reference)
9. [Modifying permissions](#modifying-permissions)
10. [Revoking access](#revoking-access)
11. [Verification & audit commands](#verification--audit-commands)

---

## The two access layers (IAM vs RBAC)

Kubernetes on GCP uses two independent access-control layers — **both must be configured** for a user to do anything inside the cluster. Removing either blocks access.

| Layer | System | Controls | Where configured |
| --- | --- | --- | --- |
| **Layer 1** | GCP IAM | **Who** can authenticate and connect to the cluster | GCP Console / `gcloud` CLI |
| **Layer 2** | Kubernetes RBAC | **What** an authenticated user can do inside the cluster | `kubectl apply` (ClusterRole + ClusterRoleBinding) |

> **Mental model:** IAM is the **door** (authentication). RBAC is **which rooms the user can enter** (authorization).

---

## GCP IAM layer — what's needed

The user must have an IAM role at the project level that lets them call `gcloud container clusters get-credentials`. The minimum is `roles/viewer`:

| IAM role | Key permissions (GCP level) | Status |
| --- | --- | --- |
| `roles/viewer` | `container.clusters.get` (fetch credentials) · `container.clusters.list` (list clusters) | ✓ Sufficient |

> ✅ **No IAM changes needed** if the user already has `roles/viewer` (or stronger) on the GCP project. All Kubernetes-level permissions are controlled by RBAC below.

### How the user fetches their kubeconfig

```bash
gcloud container clusters get-credentials <cluster-name> \
  --region <region> \
  --project <gcp-project-id>
```

After running this, `kubectl` is configured to talk to the target cluster as the user's Google account.

---

## The two YAML manifests

Splitting the role and the binding into **two separate files** keeps them independently manageable — you can re-bind the same role to a different user without touching the role file.

| File | Kind | Purpose |
| --- | --- | --- |
| `custom-devops-rule.yaml` | `ClusterRole` | Defines what actions are permitted |
| `custom-devops-binding.yaml` | `ClusterRoleBinding` | Binds the role to a specific user's Google account |

### File 1 — `custom-devops-rule.yaml`

```yaml
# ──────────────────────────────────────────────────────────────────────
# File: custom-devops-rule.yaml
# Kind: ClusterRole
# Purpose: Operational DevOps access — no application creation rights
# ──────────────────────────────────────────────────────────────────────
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: custom-devops-rule
  labels:
    managed-by: manual
    purpose: devops-ops-access
rules:

  # ── Pod operations ──────────────────────────────────────────────────
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch", "delete"]

  - apiGroups: [""]
    resources: ["pods/log"]
    verbs: ["get", "list", "watch"]

  - apiGroups: [""]
    resources: ["pods/exec"]
    verbs: ["create", "get"]

  - apiGroups: [""]
    resources: ["pods/portforward"]
    verbs: ["create", "get"]

  # ── Deployment restart (kubectl rollout restart → PATCH) ─────────────
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch", "patch"]

  # ── Read-only workload visibility ────────────────────────────────────
  - apiGroups: ["apps"]
    resources: ["replicasets", "statefulsets", "daemonsets"]
    verbs: ["get", "list", "watch"]

  # ── Services and Endpoints (port-forward targets) ────────────────────
  - apiGroups: [""]
    resources: ["services", "endpoints"]
    verbs: ["get", "list", "watch"]

  # ── Namespace listing ────────────────────────────────────────────────
  - apiGroups: [""]
    resources: ["namespaces"]
    verbs: ["get", "list", "watch"]

  # ── Events (debugging) ──────────────────────────────────────────────
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["get", "list", "watch"]

  # ── ConfigMaps (read-only) ───────────────────────────────────────────
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list", "watch"]

  # ── Helm 3 release secrets (get/list = helm list; delete = helm uninstall) ──
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get", "list", "watch", "delete"]

  # ── Resources helm uninstall cleans up ──────────────────────────────
  - apiGroups: [""]
    resources: ["services", "persistentvolumeclaims", "serviceaccounts"]
    verbs: ["delete"]

  - apiGroups: ["apps"]
    resources: ["deployments", "statefulsets", "daemonsets"]
    verbs: ["delete"]

  - apiGroups: ["networking.k8s.io"]
    resources: ["ingresses", "ingressclasses"]
    verbs: ["get", "list", "watch", "delete"]

  - apiGroups: ["autoscaling"]
    resources: ["horizontalpodautoscalers"]
    verbs: ["get", "list", "watch", "delete"]

  - apiGroups: ["policy"]
    resources: ["poddisruptionbudgets"]
    verbs: ["get", "list", "watch", "delete"]
```

### File 2 — `custom-devops-binding.yaml`

```yaml
# ──────────────────────────────────────────────────────────────────────
# File: custom-devops-binding.yaml
# Kind: ClusterRoleBinding
# Binds: custom-devops-rule → <user-email>
# ──────────────────────────────────────────────────────────────────────
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: <user-id>-custom-devops-binding   # e.g. jane-doe-custom-devops-binding
  labels:
    managed-by: manual
    purpose: devops-ops-access
subjects:
  - kind: User
    name: <user-email>                    # e.g. jane.doe@example.com — Google account email
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: custom-devops-rule                # must match the ClusterRole name above
  apiGroup: rbac.authorization.k8s.io
```

> **Why separate files?** To grant the same role to another user later, create a new binding file (`<other-user-id>-custom-devops-binding.yaml`) and apply it — you do not need to re-apply (or even open) the ClusterRole file.

---

## Apply commands

### 1. Authenticate as cluster admin

You need cluster-admin (or an equivalent role like `roles/container.admin`) to apply RBAC.

```bash
gcloud container clusters get-credentials <cluster-name> \
  --region <region> \
  --project <gcp-project-id>
```

### 2. Apply the ClusterRole

```bash
kubectl apply -f k8s-rbac/custom-devops-rule.yaml
# Expected: clusterrole.rbac.authorization.k8s.io/custom-devops-rule created
```

### 3. Apply the ClusterRoleBinding

```bash
kubectl apply -f k8s-rbac/custom-devops-binding.yaml
# Expected: clusterrolebinding.rbac.authorization.k8s.io/<user-id>-custom-devops-binding created
```

### 4. Verify

```bash
kubectl describe clusterrole custom-devops-rule
kubectl describe clusterrolebinding <user-id>-custom-devops-binding
```

### 5. Test effective permissions

```bash
# List ALL allowed actions for the user
kubectl auth can-i --list --as=<user-email>

# Test specific actions
kubectl auth can-i get pods --as=<user-email>           # expect: yes
kubectl auth can-i create deployments --as=<user-email> # expect: no
```

---

## What the user CAN do

| Action | `kubectl` / `helm` command | Resource → Verbs |
| --- | --- | --- |
| ✓ View all pods | `kubectl get pods -A` | `pods → get, list, watch` |
| ✓ Check pod logs | `kubectl logs <pod> -n <ns>` | `pods/log → get, watch` |
| ✓ Follow live logs | `kubectl logs -f <pod> -n <ns>` | `pods/log → watch` |
| ✓ Exec into pod shell | `kubectl exec -it <pod> -n <ns> -- /bin/sh` | `pods/exec → create, get` |
| ✓ Port forward to pod | `kubectl port-forward <pod> 8080:80 -n <ns>` | `pods/portforward → create, get` |
| ✓ Port forward to service | `kubectl port-forward svc/<name> 8080:80 -n <ns>` | `pods/portforward + services → get` |
| ✓ Delete a pod | `kubectl delete pod <pod> -n <ns>` | `pods → delete` |
| ✓ Restart a deployment | `kubectl rollout restart deployment/<name> -n <ns>` | `deployments → patch` |
| ✓ Check rollout status | `kubectl rollout status deployment/<name>` | `deployments → get, watch` |
| ✓ List Helm releases | `helm list -A` | `secrets → get, list` |
| ✓ Helm release status | `helm status <release> -n <ns>` | `secrets → get` |
| ✓ Helm release history | `helm history <release> -n <ns>` | `secrets → get, list` |
| ✓ Uninstall Helm release | `helm uninstall <release> -n <ns>` | `secrets, deployments, services → delete` |
| ✓ View deployments | `kubectl get deploy -A` | `deployments → get, list` |
| ✓ View statefulsets / daemonsets | `kubectl get sts,ds -A` | `statefulsets, daemonsets → get, list` |
| ✓ View services & endpoints | `kubectl get svc,ep -A` | `services, endpoints → get, list` |
| ✓ View ingresses | `kubectl get ingress -A` | `ingresses → get, list` |
| ✓ View events (debug) | `kubectl get events -n <ns>` | `events → get, list` |
| ✓ View configmaps (read-only) | `kubectl get configmap -n <ns>` | `configmaps → get, list` |
| ✓ List namespaces | `kubectl get namespaces` | `namespaces → get, list` |
| ✓ Read secrets (Helm releases) | `kubectl get secret -n <ns>` | `secrets → get, list` |
| ✓ Delete HPA / PDB (helm cleanup) | via `helm uninstall` | `horizontalpodautoscalers, poddisruptionbudgets → delete` |

---

## What the user CANNOT do

| Blocked action | Attempted command | Reason / missing permission |
| --- | --- | --- |
| ✗ Create a new deployment | `kubectl create deployment ...` | No `create` verb on `deployments` |
| ✗ Edit deployment spec | `kubectl edit deployment ...` | No `update` verb on `deployments` |
| ✗ Manually scale deployment | `kubectl scale deployment ...` | No `update` on `deployments/scale` |
| ✗ Apply manifests | `kubectl apply -f ...` | No `create`/`update` on most resource types |
| ✗ Create / update secrets | `kubectl create secret ...` | No `create`/`update` verb on `secrets` |
| ✗ Create / edit configmaps | `kubectl create configmap ...` | No `create`/`update` verb on `configmaps` |
| ✗ Install new Helm chart | `helm install ...` | No `create` on `deployments`, `services`, `secrets` |
| ✗ Upgrade a Helm release | `helm upgrade ...` | No `update`/`create` on `deployments`, `services`, `secrets` |
| ✗ Create / delete namespaces | `kubectl create namespace ...` | No `create`/`delete` on `namespaces` |
| ✗ Manage RBAC roles / bindings | `kubectl create clusterrole ...` | No access to `rbac.authorization.k8s.io` resources |
| ✗ View / manage cluster nodes | `kubectl get nodes` | No `nodes` resource permissions |
| ✗ View persistent volumes (PV) | `kubectl get pv` | Only PVC `delete` granted, not cluster-level PV |
| ✗ Manage storage classes | `kubectl get storageclasses` | Not in ClusterRole rules |
| ✗ Manage CRDs / webhooks | `kubectl get crd` | Not in ClusterRole rules |
| ✗ Access GCP IAM / billing | `gcloud iam ...` | GCP `roles/viewer` is read-only at GCP level |
| ✗ View resource metrics | `kubectl top pods` | No `metrics.k8s.io` API group access |
| ✗ Create / manage jobs / cronjobs | `kubectl create job ...` | No `batch` API group access |

---

## Optional permission add-ons (by scenario)

Append the following blocks to the `rules:` section of the `ClusterRole` and re-apply with `kubectl apply -f`. Each block is independent.

### A — Allow Helm install / upgrade

> ⚠️ **Use with caution** — this grants application creation rights.

```yaml
- apiGroups: [""]
  resources: ["services", "configmaps", "secrets", "serviceaccounts", "persistentvolumeclaims"]
  verbs: ["create", "update", "patch"]

- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets", "daemonsets"]
  verbs: ["create", "update", "patch"]

- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["create", "update", "patch"]

- apiGroups: ["autoscaling"]
  resources: ["horizontalpodautoscalers"]
  verbs: ["create", "update", "patch"]
```

### B — Allow manual scaling

```yaml
- apiGroups: ["apps"]
  resources: ["deployments/scale", "statefulsets/scale"]
  verbs: ["get", "update", "patch"]
```

### C — Restrict to a single namespace (recommended over cluster-wide)

Replace the `ClusterRole` + `ClusterRoleBinding` with a namespace-scoped `Role` + `RoleBinding`:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: custom-devops-rule
  namespace: <your-namespace>      # target namespace
rules:
  # ... same rules block as the ClusterRole above ...
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: <user-id>-custom-devops-binding
  namespace: <your-namespace>      # same namespace
subjects:
  - kind: User
    name: <user-email>
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: custom-devops-rule
  apiGroup: rbac.authorization.k8s.io
```

### D — Read-only node info

```yaml
- apiGroups: [""]
  resources: ["nodes", "nodes/status"]
  verbs: ["get", "list", "watch"]

- apiGroups: [""]
  resources: ["nodes/metrics", "nodes/stats", "nodes/proxy"]
  verbs: ["get"]
```

### E — Full configmap management

```yaml
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

### F — `kubectl top` (metrics server)

```yaml
- apiGroups: ["metrics.k8s.io"]
  resources: ["pods", "nodes"]
  verbs: ["get", "list", "watch"]
```

### G — Manage Jobs / CronJobs

```yaml
- apiGroups: ["batch"]
  resources: ["jobs", "cronjobs", "jobs/status"]
  verbs: ["get", "list", "watch", "delete"]

# To also manually trigger a job:
- apiGroups: ["batch"]
  resources: ["jobs"]
  verbs: ["create"]
```

### H — Read PV / PVC for storage debugging

```yaml
- apiGroups: [""]
  resources: ["persistentvolumes", "persistentvolumeclaims", "persistentvolumeclaims/status"]
  verbs: ["get", "list", "watch"]
```

### I — View cert-manager TLS resources

```yaml
- apiGroups: ["cert-manager.io"]
  resources: ["certificates", "certificaterequests", "issuers", "clusterissuers"]
  verbs: ["get", "list", "watch"]
```

### J — Manage network policies

```yaml
# View
- apiGroups: ["networking.k8s.io"]
  resources: ["networkpolicies"]
  verbs: ["get", "list", "watch"]

# Create / edit
- apiGroups: ["networking.k8s.io"]
  resources: ["networkpolicies"]
  verbs: ["create", "update", "patch", "delete"]
```

### K — View / impersonate service accounts (Workload Identity debugging)

```yaml
- apiGroups: [""]
  resources: ["serviceaccounts"]
  verbs: ["get", "list", "watch"]

- apiGroups: [""]
  resources: ["serviceaccounts/token"]
  verbs: ["create"]
```

### L — `kubectl attach` to running container processes

```yaml
- apiGroups: [""]
  resources: ["pods/attach"]
  verbs: ["create", "get"]
```

### M — `kubectl drain` (graceful pod eviction for node maintenance)

```yaml
- apiGroups: [""]
  resources: ["pods/eviction"]
  verbs: ["create"]
```

### N — Bind to a Google Workspace Group instead of a single user

```yaml
subjects:
  - kind: Group
    name: <devops-team-group@example.com>   # Google Workspace Group email
    apiGroup: rbac.authorization.k8s.io
```

> **Note:** Groups for RBAC must be enabled on the GKE cluster. Verify with:
> `gcloud container clusters describe <cluster-name> --region <region> | grep securityGroup`

---

## Complete RBAC parameters reference

Use this when designing custom roles. Each entry shows: the `apiGroup`, the resource, common sub-resources, and the verbs typically used.

> Use `""` (empty string) for the **core** API group.

### Core API Group — `apiGroups: [""]`

| Resource | Sub-resources | Common verbs | Used for |
| --- | --- | --- | --- |
| `pods` | `pods/log`, `pods/exec`, `pods/portforward`, `pods/attach`, `pods/eviction`, `pods/binding`, `pods/proxy`, `pods/status` | get, list, watch, delete | Core workload unit |
| `nodes` | `nodes/status`, `nodes/proxy`, `nodes/metrics`, `nodes/stats` | get, list, watch | Cluster infrastructure |
| `services` | `services/proxy`, `services/status` | get, list, watch, create, update, delete | Network exposure |
| `endpoints` | — | get, list, watch | Service backend IPs |
| `namespaces` | `namespaces/status`, `namespaces/finalize` | get, list, watch, create, delete | Logical isolation |
| `configmaps` | — | get, list, watch, create, update, patch, delete | Non-secret config |
| `secrets` | — | get, list, watch, create, update, patch, delete | Sensitive config, Helm releases |
| `serviceaccounts` | `serviceaccounts/token` | get, list, watch, create, delete | Pod identity |
| `persistentvolumes` | `persistentvolumes/status` | get, list, watch, delete | Cluster storage |
| `persistentvolumeclaims` | `persistentvolumeclaims/status` | get, list, watch, create, delete | Pod storage requests |
| `replicationcontrollers` | `replicationcontrollers/status`, `replicationcontrollers/scale` | get, list, watch | Legacy workloads |
| `resourcequotas` | `resourcequotas/status` | get, list, watch | Namespace quotas |
| `limitranges` | — | get, list, watch | Container resource limits |
| `events` | — | get, list, watch, create, patch | Cluster event log |
| `bindings` | — | create | Pod scheduling binding (admin) |
| `componentstatuses` | — | get, list | Cluster component health |

### Apps API Group — `apiGroups: ["apps"]`

| Resource | Sub-resources | Common verbs | Used for |
| --- | --- | --- | --- |
| `deployments` | `deployments/status`, `deployments/scale` | get, list, watch, create, update, patch, delete | Stateless apps |
| `replicasets` | `replicasets/status`, `replicasets/scale` | get, list, watch, delete | Pod replica mgmt |
| `statefulsets` | `statefulsets/status`, `statefulsets/scale` | get, list, watch, create, update, patch, delete | Stateful apps |
| `daemonsets` | `daemonsets/status` | get, list, watch, create, update, patch, delete | Node-level agents |
| `controllerrevisions` | — | get, list, watch, delete | StatefulSet rollback history |

### Batch API Group — `apiGroups: ["batch"]`

| Resource | Sub-resources | Common verbs | Used for |
| --- | --- | --- | --- |
| `jobs` | `jobs/status` | get, list, watch, create, delete | One-time tasks |
| `cronjobs` | `cronjobs/status` | get, list, watch, create, update, patch, delete | Scheduled tasks |

### Autoscaling API Group — `apiGroups: ["autoscaling"]`

| Resource | Sub-resources | Common verbs | Used for |
| --- | --- | --- | --- |
| `horizontalpodautoscalers` | `horizontalpodautoscalers/status` | get, list, watch, create, update, patch, delete | HPA |
| `verticalpodautoscalers` | — | get, list, watch, create, update, delete | VPA |

### Networking API Group — `apiGroups: ["networking.k8s.io"]`

| Resource | Sub-resources | Common verbs | Used for |
| --- | --- | --- | --- |
| `ingresses` | `ingresses/status` | get, list, watch, create, update, patch, delete | HTTP/HTTPS routing |
| `ingressclasses` | — | get, list, watch | Ingress controller class |
| `networkpolicies` | — | get, list, watch, create, update, patch, delete | Pod-level firewall rules |

### Policy API Group — `apiGroups: ["policy"]`

| Resource | Sub-resources | Common verbs | Used for |
| --- | --- | --- | --- |
| `poddisruptionbudgets` | `poddisruptionbudgets/status` | get, list, watch, create, update, patch, delete | Min pod availability during disruptions |

### RBAC API Group — `apiGroups: ["rbac.authorization.k8s.io"]`

> 🚨 **Admin-only — never grant to regular users.**

| Resource | Common verbs | Used for |
| --- | --- | --- |
| `roles` | get, list, watch, create, update, patch, delete | Namespace permission sets |
| `rolebindings` | get, list, watch, create, update, patch, delete | Bind roles in a namespace |
| `clusterroles` | get, list, watch, create, update, patch, delete | Cluster permission sets |
| `clusterrolebindings` | get, list, watch, create, update, patch, delete | Bind cluster roles |

### Storage API Group — `apiGroups: ["storage.k8s.io"]`

| Resource | Common verbs | Used for |
| --- | --- | --- |
| `storageclasses` | get, list, watch, create, delete | Disk provisioner config |
| `volumeattachments` | get, list, watch | Volume-to-node attachments |
| `csidrivers`, `csinodes`, `csistoragecapacities` | get, list, watch | CSI driver registration / node info |

### Coordination — `apiGroups: ["coordination.k8s.io"]`

| Resource | Common verbs | Used for |
| --- | --- | --- |
| `leases` | get, list, watch, create, update, patch, delete | Leader election |

### Discovery — `apiGroups: ["discovery.k8s.io"]`

| Resource | Common verbs | Used for |
| --- | --- | --- |
| `endpointslices` | get, list, watch | Scalable service endpoints |

### Scheduling — `apiGroups: ["scheduling.k8s.io"]`

| Resource | Common verbs | Used for |
| --- | --- | --- |
| `priorityclasses` | get, list, watch, create, delete | Pod scheduling priority |

### Node — `apiGroups: ["node.k8s.io"]`

| Resource | Common verbs | Used for |
| --- | --- | --- |
| `runtimeclasses` | get, list, watch | Container runtime selection (e.g. gVisor) |

### Admission Registration — `apiGroups: ["admissionregistration.k8s.io"]`

> 🚨 **Admin-only** — webhooks can intercept or block all API requests.

| Resource | Common verbs | Used for |
| --- | --- | --- |
| `mutatingwebhookconfigurations` | get, list, watch, create, update, delete | Auto-modify resources on creation |
| `validatingwebhookconfigurations` | get, list, watch, create, update, delete | Validate resources on creation |
| `validatingadmissionpolicies` | get, list, watch, create, update, delete | CEL-based admission (v1.28+) |

### API Extensions — `apiGroups: ["apiextensions.k8s.io"]`

| Resource | Common verbs | Used for |
| --- | --- | --- |
| `customresourcedefinitions` | get, list, watch, create, update, delete | Define CRDs |

### Metrics — `apiGroups: ["metrics.k8s.io"]`

| Resource | Common verbs | Used for |
| --- | --- | --- |
| `pods` | get, list | `kubectl top pods` |
| `nodes` | get, list | `kubectl top nodes` |

### Cert-Manager (third-party) — `apiGroups: ["cert-manager.io"]`

| Resource | Common verbs | Used for |
| --- | --- | --- |
| `certificates` | get, list, watch, create, delete | TLS certificate mgmt |
| `certificaterequests` | get, list, watch | Certificate request lifecycle |
| `issuers` | get, list, watch, create, update, delete | Namespace cert issuers |
| `clusterissuers` | get, list, watch, create, update, delete | Cluster cert issuers |

### Vault Secrets Operator (third-party, if installed) — `apiGroups: ["secrets.hashicorp.com"]`

| Resource | Common verbs | Used for |
| --- | --- | --- |
| `vaultstaticsecrets` | get, list, watch | Vault-synced static secrets |
| `vaultdynamicsecrets` | get, list, watch | Vault-synced dynamic secrets |
| `vaultauths` | get, list, watch | Vault auth config |
| `vaultconnections` | get, list, watch | Vault connection config |

### Complete verb reference

| Verb | `kubectl` equivalent | HTTP method | Description | Risk |
| --- | --- | --- | --- | --- |
| `get` | `kubectl get <res> <name>` | GET | Read a single resource | Low |
| `list` | `kubectl get <res>` | GET (collection) | List all of a type | Low |
| `watch` | `kubectl get -w` | GET + `?watch=true` | Stream real-time changes | Low |
| `create` | `kubectl create` / `apply` | POST | Create new | Medium |
| `update` | `kubectl replace` | PUT | Replace entire resource | Medium |
| `patch` | `kubectl patch` / `rollout restart` | PATCH | Partial update | Medium |
| `delete` | `kubectl delete` | DELETE | Delete one | Medium |
| `deletecollection` | `kubectl delete --all` | DELETE (bulk) | Delete all of a type | High |
| `impersonate` | `--as=user` flag | special | Act as another user/group | High (admin) |
| `bind` | (RBAC internal) | special | Bind roles (privilege-escalation guard) | High |
| `escalate` | (RBAC internal) | special | Grant verbs the grantor doesn't have | High |
| `*` | all `kubectl` commands | ALL | Wildcard — admin only | Admin only |

---

## Modifying permissions

### Option A — Edit YAML and re-apply (recommended)

To change **what** the user can do — edit `custom-devops-rule.yaml` and re-apply only the role file:

```bash
kubectl apply -f k8s-rbac/custom-devops-rule.yaml
# clusterrole.rbac.authorization.k8s.io/custom-devops-rule configured
```

To change **who** has access — edit `custom-devops-binding.yaml` and re-apply only the binding file:

```bash
kubectl apply -f k8s-rbac/custom-devops-binding.yaml
# clusterrolebinding.rbac.authorization.k8s.io/<user-id>-custom-devops-binding configured
```

### Option B — Edit directly in the cluster (quick, not recommended for prod)

```bash
kubectl edit clusterrole custom-devops-rule
```

> ⚠️ Always copy any `kubectl edit` change back to the YAML file in source control.

### Option C — Add a single rule via JSON patch

```bash
kubectl patch clusterrole custom-devops-rule \
  --type=json \
  -p '[{"op":"add","path":"/rules/-","value":{"apiGroups":[""],"resources":["configmaps"],"verbs":["create","update","delete"]}}]'
```

### Convert to namespace-scoped access

```bash
# 1. Remove cluster-wide binding
kubectl delete clusterrolebinding <user-id>-custom-devops-binding

# 2. Remove ClusterRole
kubectl delete clusterrole custom-devops-rule

# 3. Apply namespace-scoped Role + RoleBinding (see optional add-on C)
kubectl apply -f k8s-rbac/custom-devops-rule-namespaced.yaml
```

### Add another user to the same role

```bash
kubectl patch clusterrolebinding <user-id>-custom-devops-binding \
  --type=json \
  -p '[{"op":"add","path":"/subjects/-","value":{"kind":"User","name":"<another-user-email>","apiGroup":"rbac.authorization.k8s.io"}}]'
```

---

## Revoking access

### Option A — Remove only the binding (recommended)

Cuts off access without deleting the role definition. The role can be re-bound later.

```bash
kubectl delete clusterrolebinding <user-id>-custom-devops-binding
# Expected: clusterrolebinding.rbac.authorization.k8s.io "<user-id>-custom-devops-binding" deleted
```

### Option B — Remove role and binding (full cleanup)

```bash
kubectl delete clusterrolebinding <user-id>-custom-devops-binding
kubectl delete clusterrole custom-devops-rule
```

### Option C — Remove via YAML files

```bash
kubectl delete -f k8s-rbac/custom-devops-binding.yaml          # binding only
kubectl delete -f k8s-rbac/custom-devops-rule.yaml             # role
```

### Option D — Revoke GCP IAM (full lockout from the cluster)

```bash
gcloud projects remove-iam-policy-binding <gcp-project-id> \
  --member="user:<user-email>" \
  --role="roles/viewer"
```

> 🚨 Revoking IAM prevents the user from authenticating entirely — RBAC deletion becomes redundant (but still good practice). If you only want to restrict Kubernetes actions, **delete the ClusterRoleBinding instead** — do NOT touch IAM.

### Verify access is revoked

```bash
kubectl get clusterrolebinding <user-id>-custom-devops-binding
# Expected: Error from server (NotFound)

kubectl auth can-i --list --as=<user-email>
# Expected: only basic API discovery (no cluster resource actions)

kubectl auth can-i get pods --as=<user-email>
# Expected: no
```

---

## Verification & audit commands

| Purpose | Command |
| --- | --- |
| List all custom ClusterRoles | `kubectl get clusterroles | grep -v "^system:"` |
| Describe the custom role | `kubectl describe clusterrole custom-devops-rule` |
| Describe the binding | `kubectl describe clusterrolebinding <user-id>-custom-devops-binding` |
| List all permissions for a user | `kubectl auth can-i --list --as=<user-email>` |
| Test a specific permission | `kubectl auth can-i get pods --as=<user-email>` |
| Test in a specific namespace | `kubectl auth can-i exec pods --as=<user-email> -n <namespace>` |
| Find all bindings for a user | `kubectl get clusterrolebindings -o wide | grep <user-id>` |
| Find namespace bindings for a user | `kubectl get rolebindings -A -o wide | grep <user-id>` |
| Export role as YAML | `kubectl get clusterrole custom-devops-rule -o yaml` |
| Export binding as YAML | `kubectl get clusterrolebinding <user-id>-custom-devops-binding -o yaml` |
| View project IAM policy | `gcloud projects get-iam-policy <gcp-project-id> --format=table` |
| Find a user in GCP IAM | `gcloud projects get-iam-policy <gcp-project-id> --format=json | grep <user-id>` |
| List all cluster resource types | `kubectl api-resources --verbs=list -o name` |
| List all API groups available | `kubectl api-versions` |

---

## Reference

- [Kubernetes — Using RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [GKE — RBAC overview](https://cloud.google.com/kubernetes-engine/docs/best-practices/rbac)
- [Helm 3 — Release storage in secrets](https://helm.sh/docs/topics/advanced/#storage-backends)
