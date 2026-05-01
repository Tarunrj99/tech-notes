# Kubernetes

> Setup guides and how-tos for **Kubernetes** — installs, RBAC, security integrations, troubleshooting. Cloud-distribution-specific notes (GKE / EKS / AKS) live here too, since Kubernetes is the primary subject and the cloud is just where the cluster runs.

[Back to repo root](../README.md) · [Repo conventions](../AGENTS.md) · [`cloud/`](../cloud/) · [`linux/`](../linux/) · [`tools/`](../tools/) · [`ai-prompts/`](../ai-prompts/)

---

## Notes

| Note | What you'll set up | Cluster | Status |
| --- | --- | --- | --- |
| [GKE RBAC — DevOps user access setup](gke-rbac-devops-user-access-guide.md) | A custom `ClusterRole` + `ClusterRoleBinding` granting operational (port-forward, log view, exec, restart, Helm uninstall) access **without** giving full admin or app-creation rights. Plus a complete RBAC parameter reference for extending. | GKE | stable |
| [GKE + AccuKnox CNAPP — integration & onboarding](gke-accuknox-cnapp-integration-guide.md) | End-to-end onboarding of a GKE cluster to AccuKnox CNAPP — GCP IAM, custom role, VPC egress firewall (the #1 failure point), KubeArmor + agents via Helm, multi-cluster, GAR image scanning, real troubleshooting. | GKE | stable |

*More Kubernetes notes (EKS, kubeadm, Helm, operators, networking) will be added here as they are published.*

---

## Conventions

- Cluster names → `<cluster-name>`
- Namespaces → `<namespace>` or the actual namespace if it's a Kubernetes-defined one (`kube-system`, `agents`, etc.)
- User identities → `<user-email>` (e.g. `<jane.doe@example.com>`) and `<user-id>` (e.g. `<jane-doe>`) for binding names
- GCP project IDs → `<gcp-project-id>`
- Service account emails → `<sa-name>@<gcp-project-id>.iam.gserviceaccount.com`
- Apply-order: **always** `ClusterRole` (or `Role`) before `ClusterRoleBinding` (or `RoleBinding`)
- YAML samples are drop-in — replace placeholders, then `kubectl apply -f`

See [`AGENTS.md`](../AGENTS.md) for the full conventions.
