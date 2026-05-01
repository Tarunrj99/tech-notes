# AWS

> AWS-specific setup guides and how-tos.

[Back to repo root](../../README.md) · [`cloud/`](../README.md) · [`cloud/gcp/`](../gcp/) · [Repo conventions](../../AGENTS.md)

---

## Notes

| Note | Topic | Status |
| --- | --- | --- |
| [SES — CloudWatch logging setup](ses-cloudwatch-logging-setup-guide.md) | SES → SNS → Lambda → CloudWatch pipeline for per-email visibility (bounce / complaint / delivery), with a reusable CloudFormation template | stable |

*More AWS notes will be added here as they are published.*

---

## Conventions

- Account IDs → `<aws-account-id>`
- ARNs → `arn:aws:<service>:<region>:<aws-account-id>:<resource-name>`
- Region examples use `us-east-1` (N. Virginia) unless the topic is region-specific
- All sender / recipient emails sanitized to `<your-domain.com>` placeholders
- Sensitive identifiers (support case IDs, key IDs, etc.) are always placeholders

See [`../README.md`](../README.md) and [`AGENTS.md`](../../AGENTS.md) for the full conventions.
