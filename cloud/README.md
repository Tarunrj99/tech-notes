# Cloud

> Setup guides and how-tos for **public-cloud** services — AWS, GCP, Azure. Only provider-specific notes live here. Anything cloud-agnostic (RDP, VPN, Linux, etc.) lives in its own top-level folder.

[Back to repo root](../README.md) · [Repo conventions](../AGENTS.md) · [`linux/`](../linux/) · [`kubernetes/`](../kubernetes/) · [`tools/`](../tools/) · [`ai-prompts/`](../ai-prompts/)

---

## Sub-folders

| Folder | Scope |
| --- | --- |
| [`aws/`](aws/) | AWS-specific setup guides — IAM, SES, CloudWatch, etc. |
| [`gcp/`](gcp/) | GCP-specific setup guides — GCS, IAM, GKE infra, etc. |
| `azure/` *(future)* | Azure-specific setup guides |

---

## How notes are organised here

- **One note per scenario.** Don't lump "SES setup + CloudWatch alarms + dashboard" into one mega-note — split it.
- **One cloud per folder.** If a guide truly spans two clouds, write a tool-agnostic version in the relevant top-level folder (e.g. `kubernetes/`) and link to per-cloud helpers from there.
- Filenames follow the standard kebab-case convention — see [AGENTS.md](../AGENTS.md).

---

## Add a new cloud note

1. Pick the right sub-folder (`aws/`, `gcp/`, or create `azure/`).
2. Use the note template from [AGENTS.md](../AGENTS.md).
3. Sanitize all account IDs, project IDs, emails, IPs, and bucket names into `<placeholders>`.
4. Run the secret-scan command (in `AGENTS.md`).
5. Add an entry to the [Note catalog](../README.md#note-catalog) in the root README.
