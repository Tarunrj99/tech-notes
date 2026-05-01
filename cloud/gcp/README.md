# GCP

> GCP-specific setup guides and how-tos.

[Back to repo root](../../README.md) · [`cloud/`](../README.md) · [`cloud/aws/`](../aws/) · [Repo conventions](../../AGENTS.md)

---

## Notes

| Note | Topic | Status |
| --- | --- | --- |
| [GCS bucket — public file access & security setup](gcs-bucket-public-access-and-security-guide.md) | Make GCS files **publicly readable by URL** but the bucket **not listable**. Includes a Cloud Function (Gen 2) that auto-applies public-read ACL on every new upload. | stable |

> ℹ️ **GKE-related notes** live in [`/kubernetes/`](../../kubernetes/), not here. Only **GCP-platform** notes (GCS, IAM, networking, billing, etc.) belong in this folder.

*More GCP notes will be added here as they are published.*

---

## Conventions

- Project IDs → `<gcp-project-id>`
- Bucket names → `<your-bucket-name>`
- Cluster names → `<cluster-name>` (when referenced from GCP-side commands)
- Service account emails → `<sa-name>@<gcp-project-id>.iam.gserviceaccount.com`
- Region examples use `us-central1` unless the topic is region-specific

See [`../README.md`](../README.md) and [`AGENTS.md`](../../AGENTS.md) for the full conventions.
