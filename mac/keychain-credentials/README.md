# Secure API Credential Management on macOS using Apple Keychain

> **Audience:** Developers and DevOps engineers working on macOS who need a reliable,
> secure, and repeatable system for managing API credentials locally.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [General Keychain Commands](#general-keychain-commands)
4. [AWS Credentials](#aws-credentials)
5. [MongoDB Atlas](#mongodb-atlas)
6. [Cloudflare](#cloudflare)
7. [Recommended Naming Convention](#recommended-naming-convention)
8. [Loading All Secrets at Once](#loading-all-secrets-at-once)
9. [Using Credentials in Applications](#using-credentials-in-applications)
10. [AI Assistant Security Rules](#ai-assistant-security-rules)
11. [Git Best Practices](#git-best-practices)
12. [Security Best Practices Checklist](#security-best-practices-checklist)
13. [Troubleshooting](#troubleshooting)
14. [Appendix: Quick Reference Cheat Sheet](#appendix--quick-reference-cheat-sheet)

---

## Quick Start: Step-by-Step Setup

> New here? Follow these steps in order. Each step links to the full explanation.
> You can skip services you don't use.

### Phase 1: One-time machine setup (do this first, once)

| Step | What to do | Jump to |
|------|-----------|---------|
| **1** | Understand why Keychain beats `.env` and shell profiles | [Introduction](#introduction) |
| **2** | Learn the 4 core commands: store, verify, export, delete | [General Keychain Commands](#general-keychain-commands) |
| **3** | Create `~/.config/secrets/load-secrets.sh` on your machine | [Loading All Secrets at Once](#loading-all-secrets-at-once) |
| **4** | Add the `load-secrets` alias to your `.zshrc` | [Sourcing the Script](#sourcing-the-script) |

---

### Phase 2: Store your credentials (one per service)

Pick only the services you use:

| Service | What to store | Jump to |
|---------|--------------|---------|
| **AWS** | `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` | [AWS Credentials → Store in Keychain](#store-aws-credentials-in-keychain) |
| **MongoDB** | `MONGODB_URI` (single connection string) | [MongoDB Atlas → Store in Keychain](#store-mongodb-uri-in-keychain) |
| **Cloudflare** | `CLOUDFLARE_API_TOKEN` | [Cloudflare → Store in Keychain](#store-cloudflare-token-in-keychain) |

---

### Phase 3: Use credentials in your project

| Step | What to do | Jump to |
|------|-----------|---------|
| **5** | Run `source ~/.config/secrets/load-secrets.sh` at the start of any session | [Loading All Secrets at Once](#loading-all-secrets-at-once) |
| **6** | Read env vars in your code, Node.js, Python, Go, etc. | [Using Credentials in Applications](#using-credentials-in-applications) |
| **7** | Add `.gitignore` rules so secrets can never be committed | [Git Best Practices](#git-best-practices) |
| **8** | Paste the AI rules into Cursor or Claude so they never ask for secrets | [AI Assistant Security Rules](#ai-assistant-security-rules) |

---

### Quick-lookup by goal

| I want to… | Go to |
|-----------|-------|
| Store a secret right now | [Store a Secret](#store-a-secret) |
| Export a secret to my shell | [Export a Secret as an Environment Variable](#export-a-secret-as-an-environment-variable) |
| Set up AWS access keys | [AWS Credentials](#aws-credentials) |
| Set up a MongoDB connection | [MongoDB Atlas](#mongodb-atlas) |
| Set up a Cloudflare token | [Cloudflare](#cloudflare) |
| Create one script to load everything | [load-secrets.sh](#load-secretssh) |
| See all naming conventions at a glance | [Recommended Naming Convention](#recommended-naming-convention) |
| Fix a Keychain error | [Troubleshooting](#troubleshooting) |
| See all commands in one place | [Appendix: Cheat Sheet](#appendix--quick-reference-cheat-sheet) |

---

## Introduction

### What is Apple Keychain?

Apple Keychain is macOS's built-in encrypted credential store. It has been part of macOS
since the early days and is deeply integrated into the operating system. Under the hood,
Keychain stores credentials in an encrypted SQLite database protected by AES-256
encryption. The encryption key itself is derived from your macOS login password, meaning
the store is locked when your Mac is off and decrypts automatically when you log in.

Keychain supports three types of entries relevant to developer workflows:

| Type | Use case |
|---|---|
| **Generic password** | API tokens, passwords, secrets (the type used in this guide |
| **Internet password** | Browser-saved website credentials |
| **Certificate/Key** | TLS certificates, SSH keys, code-signing identities |

This guide focuses entirely on **generic passwords** managed via the `security` CLI tool.

---

### Why Keychain is Safer Than `.env` Files

`.env` files are the most common source of accidental secret exposure. The risks are real:

| Risk | `.env` file | Keychain |
|---|---|---|
| Accidentally committed to Git | Very common | Not possible (lives outside the repo |
| Readable by any process as plain text | Yes | No (requires explicit macOS permission grant |
| Persists across reboots unencrypted | Yes (if disk is unencrypted) | Encrypted at rest, always |
| Visible in text editors, file browsers | Yes | No |
| Included in zip/tar backups carelessly | Yes | No |
| Exposed in Docker build context | Yes | No |

`.env` files are plain text sitting on your filesystem. Any process, any script, any IDE
plugin, any npm package you run can silently read them. Keychain requires the calling
process to be explicitly granted access and logs every access attempt.

> **Warning:** A `.env` file on disk is readable by every process running as your user
> account, including malicious scripts in `node_modules`, Python packages, or shell
> scripts you run from the internet.

---

### Why Keychain is Safer Than Shell Profiles (`.zshrc`, `.bash_profile`)

Many developers export secrets in their shell profile:

```bash
# ❌ Never do this
export AWS_SECRET_ACCESS_KEY="AKIAIOSFODNN7EXAMPLE..."
```

This is dangerous for several reasons:

- Shell profiles are **plain text files** stored unencrypted on disk
- They are often backed up to iCloud, Time Machine, or Dropbox, all of which sync to
  remote servers
- Every shell session loads them, meaning the secret is in memory constantly, even when
  you are not using it
- They show up in dotfile repositories that developers frequently share publicly on GitHub
- The value is visible in shell history if typed incorrectly or echoed accidentally

Keychain secrets are fetched only when explicitly requested, are never stored in shell
history, and are never included in dotfile backups.

---

### Why Secrets Must Never Be Committed to Git

Once a secret is in Git history it is effectively public, even if you delete it from the
latest commit. Anyone with a clone of the repository can run `git log`, `git show`, or
`git grep` to retrieve it. Services like GitHub retain commit history even after force
pushes for a period of time, and security scanners constantly crawl public repositories.

In 2023 alone, over 10 million secrets were detected in public GitHub repositories by
GitHub's own Secret Scanning service. Leaked AWS keys in particular are found and exploited
by automated bots within **seconds** of being pushed.

> **Critical:** If a secret is committed to a public repository, treat it as fully
> compromised immediately. Rotate it before doing anything else.

---

### Why AI Assistants Should Never Receive Actual Secrets

When you paste a real API key or connection string into an AI chat interface (Cursor,
Claude, ChatGPT, Copilot, etc.) that value becomes part of the conversation context which:

- May be logged by the AI provider's infrastructure
- May be used for model training (depending on provider settings)
- Is visible in your conversation history, which may sync to cloud accounts
- Could be exposed if your account is compromised

The correct workflow is always: store the secret in Keychain, refer to the secret by its
**environment variable name** in AI conversations, and let the AI generate code that reads
`process.env.MY_SECRET` rather than containing the actual value.

---

## Architecture Overview

### General Flow

```mermaid
flowchart TD
    A[Developer stores secret once] --> B[Apple Keychain\nEncrypted at rest\nAES-256]
    B --> C[Terminal — load-secrets.sh\nsecurity find-generic-password]
    C --> D[Environment Variables\nIn current shell session only]
    D --> E[Cursor / Claude Code\nReads process.env / os.environ]
    D --> F[Application Code\nprocess.env / os.environ / os.getenv]
    F --> G[AWS SDK / MongoDB Driver\n/ Cloudflare SDK]
```

---

### AWS Credential Flow

```mermaid
flowchart TD
    A[AWS IAM Console\nCreate Access Key] --> B[Keychain\nAWS_ACCESS_KEY_ID\nAWS_SECRET_ACCESS_KEY]
    B --> C[load-secrets.sh\nexports both vars]
    C --> D[AWS CLI\naws s3 ls]
    C --> E[AWS SDK — Node.js\nnew S3Client]
    C --> F[AWS SDK — Python\nboto3.client]
    D & E & F --> G[AWS API\nSTS validates identity]
```

---

### MongoDB Atlas Flow

```mermaid
flowchart TD
    A[Atlas Console\nCreate DB User\nGet Connection String] --> B[Keychain\nMONGODB_URI]
    B --> C[load-secrets.sh\nexports MONGODB_URI]
    C --> D[Node.js — Mongoose\nmongoose.connect]
    C --> E[Node.js — native driver\nMongoClient]
    C --> F[Python — PyMongo\nMongoClient]
```

---

### Cloudflare Flow

```mermaid
flowchart TD
    A[Cloudflare Dashboard\nCreate scoped API Token] --> B[Keychain\nCLOUDFLARE_API_TOKEN]
    B --> C[load-secrets.sh\nexports CLOUDFLARE_API_TOKEN]
    C --> D[curl\nAuthorization: Bearer]
    C --> E[Node.js — cloudflare SDK]
    C --> F[Wrangler CLI\nwrangler deploy]
```

---

## General Keychain Commands

All Keychain operations use the macOS `security` command-line tool, which ships with
every macOS installation. No installation required.

---

### Store a Secret

```bash
printf 'Paste token (hidden): '; \
read -s token && echo && \
security add-generic-password \
  -s "service-name" \
  -a "ENV_VARIABLE_NAME" \
  -w "$token" \
  -U && \
unset token
```

**Argument breakdown:**

| Argument | Meaning |
|---|---|
| `-s "service-name"` | The **service** label (use a short, consistent, lowercase slug (e.g. `aws-access-key`) |
| `-a "ENV_VARIABLE_NAME"` | The **account** label (use the exact environment variable name (e.g. `AWS_ACCESS_KEY_ID`) |
| `-w "$token"` | The **secret value** (passed as a variable, never typed directly in the command |
| `-U` | **Update** (if an entry with the same `-s` and `-a` already exists, overwrite it silently instead of erroring |

**Why use `read -s` instead of typing the value directly?**

If you type `security add-generic-password -w "mytoken123"` the value appears in your
shell history forever (`~/.zsh_history`). Using `read -s` prompts you to paste the value
without it ever appearing on screen or being saved to history. The `unset token` at the
end clears the variable from memory.

> **Tip:** The `-s` and `-a` pair together form the unique key for a Keychain entry. Both
> must match exactly when you retrieve the value later. Keep them consistent across your
> team and across machines.

---

### Verify a Secret Exists

```bash
security find-generic-password \
  -s "service-name" \
  -a "ENV_VARIABLE_NAME"
```

This returns metadata about the entry, the service name, account, creation date, and
modification date. **without** showing the secret value. Use this to confirm an entry
was saved correctly before trying to use it.

Example output:

```
keychain: "/Users/yourname/Library/Keychains/login.keychain-db"
class: "genp"
attributes:
    "acct"<blob>="AWS_ACCESS_KEY_ID"
    "cdat"<timedate>=0x32303234...
    "desc"<blob>=<NULL>
    "gena"<blob>=<NULL>
    "icmt"<blob>=<NULL>
    "invi"<sint32>=<NULL>
    "modi"<timedate>=0x32303234...
    "mstr"<sint32>=<NULL>
    "pdmn"<string>="afe"
    "svce"<blob>="aws-access-key"
    "type"<uint32>=<NULL>
```

To verify and also print the value (for debugging only, never in scripts that log output):

```bash
security find-generic-password \
  -s "service-name" \
  -a "ENV_VARIABLE_NAME" \
  -w
```

The `-w` flag prints just the raw secret value to stdout, which is exactly what is used
in the export commands below.

---

### Export a Secret as an Environment Variable

```bash
export CLOUDFLARE_API_TOKEN="$(
  security find-generic-password \
    -s "cloudflare-api-token" \
    -a "CLOUDFLARE_API_TOKEN" \
    -w
)"
```

**Why this approach is preferred:**

- The secret value is never stored in a file, it lives only in memory for the duration
  of the shell session
- The command substitution `$(...)` runs in a subshell; the raw value is returned and
  immediately assigned to the environment variable
- When the terminal session ends, the variable is gone
- No file permissions to misconfigure, no risk of the file appearing in backups or sync

> **Warning:** Never store the output of this command to a file, and never `echo` the
> variable in a shared terminal, log file, or CI environment.

---

### Delete a Secret

```bash
security delete-generic-password \
  -s "service-name" \
  -a "ENV_VARIABLE_NAME"
```

This permanently removes the entry from Keychain. Use this when rotating credentials:
delete the old entry first, then add the new one (or use `-U` to update in place).

---

### Updating an Existing Secret

The `-U` flag on `add-generic-password` handles updates atomically. If an entry with the
given `-s` and `-a` already exists, it replaces the value. If no entry exists, it creates
a new one. This means your store command is always idempotent:

```bash
printf 'New token value: '; \
read -s token && echo && \
security add-generic-password \
  -s "service-name" \
  -a "ENV_VARIABLE_NAME" \
  -w "$token" \
  -U && \
unset token
```

Run the same command again with a new value after rotating a credential. No need to
delete first.

---

## AWS Credentials

### Why Not to Use the Root Account

When you create an AWS account, a **root user** is created. This account has unrestricted
access to every AWS service and every resource. It cannot be restricted by IAM policies.

You should:

- Enable MFA on the root account immediately
- Store the root credentials somewhere extremely secure (physical safe, 1Password)
- **Never create programmatic access keys for the root account**
- Never use the root account for day-to-day development

All programmatic access should go through IAM users or IAM roles with the minimum
permissions required.

---

### Creating a Least-Privilege IAM User for Development

#### Step 1: Create an AWS Account

Go to [aws.amazon.com](https://aws.amazon.com) and create an account. Enable MFA on the
root account as the first action after signup.

#### Step 2: Open IAM Console

Sign in to the AWS Management Console. Navigate to **IAM** (Identity and Access
Management).

#### Step 3: Create an IAM Group with Scoped Permissions

Groups make it easy to manage permissions for multiple users and to audit what any user
can do.

1. In IAM → **User groups** → **Create group**
2. Name it clearly: `developers`, `devops-team`, or `project-name-developers`
3. Attach only the policies your work requires. Do not attach `AdministratorAccess`.

Examples of least-privilege policies:

| What you need | Minimum policy |
|---|---|
| Read S3 buckets | `AmazonS3ReadOnlyAccess` |
| Deploy Lambda functions | `AWSLambda_FullAccess` (scoped to specific functions via resource ARN if possible) |
| Use EC2 | `AmazonEC2FullAccess` or a custom policy scoped to specific instance types/regions |
| Use DynamoDB | `AmazonDynamoDBFullAccess` or a custom table-scoped policy |
| Use SES | `AmazonSESFullAccess` (or send-only via a custom policy) |

> **Best practice:** Create a custom policy using the **IAM Policy Generator** or the
> JSON editor that grants access only to the specific actions and specific resource ARNs
> your application uses. Wildcard `"Resource": "*"` should be avoided wherever possible.

#### Step 4: Create an IAM User

1. IAM → **Users** → **Create user**
2. Name it clearly: `tarun-dev`, `project-name-ci`, `local-dev`
3. Select **"I want to create an IAM user"** (not SSO)
4. Do **not** enable console access unless needed
5. Add the user to the group you created in Step 3
6. Finish creation

#### Step 5: Create an Access Key

1. Open the user → **Security credentials** tab
2. Under **Access keys** → **Create access key**
3. Choose **"Local code"** as the use case
4. **Download the CSV or copy both values immediately**, the secret key is shown only once

You will now have two values:

| Variable | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | The key identifier (starts with `AKIA` for long-term keys |
| `AWS_SECRET_ACCESS_KEY` | The secret (a 40-character string. Never shown again after creation |

---

### Understanding AWS_SESSION_TOKEN

Session tokens are required when using **temporary credentials** issued by AWS STS
(Security Token Service). This happens when:

- Assuming an IAM role (`aws sts assume-role`)
- Using AWS SSO / IAM Identity Center
- Using EC2 instance profiles or ECS task roles

For local development with a standard IAM user access key, `AWS_SESSION_TOKEN` is not
required. For CI/CD pipelines using OIDC or role assumption, all three variables are used.

| Variable | Required for standard IAM user | Required for assumed role / SSO |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | Yes | Yes |
| `AWS_SECRET_ACCESS_KEY` | Yes | Yes |
| `AWS_SESSION_TOKEN` | No | Yes |

---

### Store AWS Credentials in Keychain

```bash
# AWS Access Key ID
printf 'AWS_ACCESS_KEY_ID: '; \
read -s val && echo && \
security add-generic-password \
  -s "aws-access-key" \
  -a "AWS_ACCESS_KEY_ID" \
  -w "$val" -U && unset val

# AWS Secret Access Key
printf 'AWS_SECRET_ACCESS_KEY: '; \
read -s val && echo && \
security add-generic-password \
  -s "aws-secret-key" \
  -a "AWS_SECRET_ACCESS_KEY" \
  -w "$val" -U && unset val

# AWS Session Token (only if using temporary credentials)
printf 'AWS_SESSION_TOKEN: '; \
read -s val && echo && \
security add-generic-password \
  -s "aws-session-token" \
  -a "AWS_SESSION_TOKEN" \
  -w "$val" -U && unset val
```

---

### Export AWS Credentials

```bash
export AWS_ACCESS_KEY_ID="$(
  security find-generic-password -s "aws-access-key" -a "AWS_ACCESS_KEY_ID" -w
)"

export AWS_SECRET_ACCESS_KEY="$(
  security find-generic-password -s "aws-secret-key" -a "AWS_SECRET_ACCESS_KEY" -w
)"

# Only if using temporary credentials:
export AWS_SESSION_TOKEN="$(
  security find-generic-password -s "aws-session-token" -a "AWS_SESSION_TOKEN" -w
)"
```

---

### Using AWS Credentials in Applications

**AWS CLI:**

```bash
# After exporting, the AWS CLI automatically picks up the environment variables
aws sts get-caller-identity
aws s3 ls
aws ec2 describe-instances --region us-east-1
```

**Node.js (AWS SDK v3):**

```javascript
import { S3Client, ListBucketsCommand } from "@aws-sdk/client-s3";

// The SDK automatically reads AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
// from process.env — no explicit credential passing required
const client = new S3Client({ region: process.env.AWS_REGION ?? "us-east-1" });

const response = await client.send(new ListBucketsCommand({}));
console.log(response.Buckets);
```

**Python (boto3):**

```python
import boto3

# boto3 automatically reads AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
# from environment variables — no explicit credential passing required
s3 = boto3.client("s3")
response = s3.list_buckets()
print(response["Buckets"])
```

> **Important:** Never pass credentials explicitly in code like
> `boto3.client("s3", aws_access_key_id="AKIA...")`. Always let the SDK read them from
> the environment.

---

### AWS Security Best Practices

- **Rotate access keys every 90 days.** Use the `-U` flag to update Keychain with the
  new value after rotation.
- **Never share access keys.** Each developer and each CI pipeline should have its own
  IAM user or role.
- **Use IAM roles instead of access keys for production.** EC2 instances, Lambda
  functions, and ECS tasks should use instance/execution roles, not hardcoded keys.
- **Enable CloudTrail** to log all API calls made with your credentials.
- **Set up IAM Access Analyzer** to detect overly permissive policies.
- **Enable MFA Delete on S3 buckets** containing critical data.

**Revocation:** If a key is suspected to be compromised, go to IAM → Users → Security
credentials → Deactivate the key immediately, then delete it and create a new one. Update
Keychain on all machines.

---

### Common AWS Mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Using root account access keys | Full account compromise if leaked | Create a dedicated IAM user |
| Committing `.aws/credentials` to Git | Instant compromise via GitHub scanners | Move to Keychain + environment variables |
| Using `AdministratorAccess` for dev | Blast radius is entire account | Create a custom least-privilege policy |
| Sharing access keys across developers | Impossible to audit who did what | One key per human or pipeline |
| Never rotating keys | Old leaked keys remain valid forever | Rotate every 90 days |

---

## MongoDB Atlas

### Creating an Atlas Account and Cluster

#### Step 1: Create an Atlas Account

Go to [cloud.mongodb.com](https://cloud.mongodb.com) and sign up.

#### Step 2: Create an Organization and Project

After signing in, create an **Organization** (your company or personal account) and a
**Project** within it. Projects isolate clusters, users, and network settings from each
other.

#### Step 3: Create a Cluster

Inside your project, click **"Build a Cluster"**. For development:

- Choose **M0 Free Tier** or **M2/M5** for light production use
- Select a cloud provider (AWS, GCP, or Azure) and region close to your application
- Give the cluster a meaningful name (e.g. `dev-cluster`, `prod-cluster`)

#### Step 4: Create a Database User

Go to **Database Access** → **Add New Database User**.

- Choose **Password** authentication (not X.509 for most use cases)
- Use a strong randomly generated password, never a password you reuse elsewhere
- Set the role to the minimum required:

| Role | Use case |
|---|---|
| `readWrite` on specific database | Application user |
| `read` on specific database | Read-only reporting |
| `atlasAdmin` | Only for database administrators, never for app users |

> **Best practice:** Create one database user per application or per environment
> (dev, staging, production). This limits blast radius if one set of credentials is leaked.

#### Step 5: Configure IP Access List

Under **Network Access** → **IP Access List**, add the IP addresses that should be allowed
to connect.

- For local development, add your current IP: `0.0.0.0/0` is convenient but means
  anyone with valid credentials can connect from anywhere, avoid it in production
- For production, add only the specific IP ranges of your application servers or VPN

#### Step 6: Get the Connection String

In the Atlas dashboard, click **Connect** → **Connect your application** → choose your
driver and version. Copy the connection string. It looks like this:

```
mongodb+srv://dbuser:<password>@dev-cluster.abc12.mongodb.net/mydatabase?retryWrites=true&w=majority
```

Replace `<password>` with your database user's password.

---

### Understanding the MongoDB URI

```
mongodb+srv://dbuser:p@ssw0rd@dev-cluster.abc12.mongodb.net/mydatabase?retryWrites=true&w=majority
│             │      │        │                              │           │              │
│             │      │        │                              │           │              └─ Write concern: majority of replicas must acknowledge
│             │      │        │                              │           └─ retryWrites: auto-retry failed write operations
│             │      │        │                              └─ Database name (optional in URI; can be specified in code)
│             │      │        └─ Atlas cluster hostname (SRV record resolves to replica set members)
│             │      └─ Password (URL-encoded if it contains special characters)
│             └─ Database username
└─ Protocol: mongodb+srv uses DNS SRV records for discovery (simpler than listing all hosts)
```

**Why store the full URI, not the parts separately?**

The URI encodes username, password, host, port, and options in a single string. Drivers
from all languages accept this single string. Splitting it into separate variables
(`MONGODB_HOST`, `MONGODB_USER`, `MONGODB_PASSWORD`) creates more surface area for errors
and more variables to manage without meaningful security benefit. Store only `MONGODB_URI`.

---

### Store MongoDB URI in Keychain

```bash
printf 'MONGODB_URI: '; \
read -s val && echo && \
security add-generic-password \
  -s "mongodb-uri" \
  -a "MONGODB_URI" \
  -w "$val" -U && unset val
```

---

### Export MongoDB URI

```bash
export MONGODB_URI="$(
  security find-generic-password -s "mongodb-uri" -a "MONGODB_URI" -w
)"
```

---

### Using MongoDB URI in Applications

**Node.js (native MongoDB driver):**

```javascript
import { MongoClient } from "mongodb";

const client = new MongoClient(process.env.MONGODB_URI);

async function main() {
  await client.connect();
  const db = client.db("mydatabase");
  const collection = db.collection("users");
  const docs = await collection.find({}).toArray();
  console.log(docs);
  await client.close();
}

main();
```

**Node.js (Mongoose):**

```javascript
import mongoose from "mongoose";

await mongoose.connect(process.env.MONGODB_URI);
console.log("Connected to MongoDB");
```

**Python (PyMongo):**

```python
import os
from pymongo import MongoClient

client = MongoClient(os.environ["MONGODB_URI"])
db = client["mydatabase"]
collection = db["users"]
docs = list(collection.find({}))
print(docs)
```

---

### MongoDB Security Considerations

- **Never put the connection string in source code.** Even in a private repository.
- **URL-encode special characters** in the password. If the password contains `@`, `/`,
  `:`, or `?`, they must be percent-encoded (e.g. `@` → `%40`). The Atlas dashboard
  handles this automatically when it generates the connection string for you.
- **Use TLS.** The `mongodb+srv://` scheme enforces TLS by default.
- **Rotate the database user password regularly** and update Keychain with `-U`.
- **Do not use the Atlas admin user** for application connections. Create a scoped user.

---

## Cloudflare

### Global API Key vs. API Tokens

Cloudflare provides two types of programmatic access:

| Type | Scope | Risk |
|---|---|---|
| **Global API Key** | Full account access (equivalent to your password | Extremely high (one leak means full account compromise |
| **API Tokens** | Scoped to specific zones, specific permissions, and optionally specific IPs and time windows | Low (a leaked token can only do what it was explicitly granted |

**Always use API Tokens.** The Global API Key exists for legacy reasons and should never
be used in scripts, CI, or applications.

---

### Creating a Scoped API Token

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) → **My Profile** →
   **API Tokens** → **Create Token**
2. Choose **"Create Custom Token"** for full control
3. Configure the token:

| Setting | Value |
|---|---|
| **Token name** | Something descriptive: `dns-automation`, `workers-deploy`, `local-dev` |
| **Permissions** | Add only what is needed (see examples below) |
| **Zone Resources** | Choose specific zones or "All zones" only if truly required |
| **IP Address Filtering** | Optional but recommended (restrict to your office/home IP |
| **TTL** | Set an expiry date for tokens used in CI or temporary access |

**DNS management permissions:**

| Resource | Permission |
|---|---|
| Zone — DNS | Edit |
| Zone — Zone | Read |

**Workers deployment permissions:**

| Resource | Permission |
|---|---|
| Account — Workers Scripts | Edit |
| Zone — Workers Routes | Edit |

**Read-only zone permissions (for monitoring):**

| Resource | Permission |
|---|---|
| Zone — Zone | Read |
| Zone — Analytics | Read |

After clicking **"Continue to summary"** → **"Create Token"**, copy the token value. It
is shown only once.

---

### Store Cloudflare Token in Keychain

```bash
printf 'CLOUDFLARE_API_TOKEN: '; \
read -s val && echo && \
security add-generic-password \
  -s "cloudflare-api-token" \
  -a "CLOUDFLARE_API_TOKEN" \
  -w "$val" -U && unset val
```

---

### Export Cloudflare Token

```bash
export CLOUDFLARE_API_TOKEN="$(
  security find-generic-password -s "cloudflare-api-token" -a "CLOUDFLARE_API_TOKEN" -w
)"
```

---

### Using the Cloudflare Token in Applications

**curl:**

```bash
curl -s -X GET "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" | jq .
```

**Node.js (Cloudflare SDK):**

```javascript
import Cloudflare from "cloudflare";

const cf = new Cloudflare({
  apiToken: process.env.CLOUDFLARE_API_TOKEN,
});

const zones = await cf.zones.list();
console.log(zones.result);
```

**Wrangler CLI (Workers deployment):**

```bash
# Wrangler automatically reads CLOUDFLARE_API_TOKEN from the environment
wrangler deploy
wrangler tail my-worker
```

**Python (using requests):**

```python
import os
import requests

headers = {
    "Authorization": f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}",
    "Content-Type": "application/json",
}

response = requests.get(
    "https://api.cloudflare.com/client/v4/zones",
    headers=headers,
)
print(response.json())
```

---

### Cloudflare Token Rotation and Revocation

**Rotation:** Go to API Tokens → find the token → click the three-dot menu →
**"Roll"** to generate a new value with the same permissions. Update Keychain immediately
after rolling:

```bash
printf 'New CLOUDFLARE_API_TOKEN: '; \
read -s val && echo && \
security add-generic-password \
  -s "cloudflare-api-token" \
  -a "CLOUDFLARE_API_TOKEN" \
  -w "$val" -U && unset val
```

**Revocation:** Click the token → **"Revoke"**. The token becomes invalid immediately.
Use this if a token is suspected to be compromised. Create a new token, update Keychain,
and check your Cloudflare Audit Log for any unauthorized activity.

---

## Recommended Naming Convention

Using consistent names across all machines, projects, and team members eliminates
confusion when reading scripts or setting up a new machine.

| Service | Keychain `-s` (service) | Keychain `-a` (account) | Environment Variable |
|---|---|---|---|
| AWS Access Key ID | `aws-access-key` | `AWS_ACCESS_KEY_ID` | `AWS_ACCESS_KEY_ID` |
| AWS Secret Access Key | `aws-secret-key` | `AWS_SECRET_ACCESS_KEY` | `AWS_SECRET_ACCESS_KEY` |
| AWS Session Token | `aws-session-token` | `AWS_SESSION_TOKEN` | `AWS_SESSION_TOKEN` |
| AWS Region | `aws-region` | `AWS_REGION` | `AWS_REGION` |
| MongoDB URI | `mongodb-uri` | `MONGODB_URI` | `MONGODB_URI` |
| Cloudflare API Token | `cloudflare-api-token` | `CLOUDFLARE_API_TOKEN` | `CLOUDFLARE_API_TOKEN` |
| Cloudflare Account ID | `cloudflare-account-id` | `CLOUDFLARE_ACCOUNT_ID` | `CLOUDFLARE_ACCOUNT_ID` |
| Cloudflare Zone ID | `cloudflare-zone-id` | `CLOUDFLARE_ZONE_ID` | `CLOUDFLARE_ZONE_ID` |
| GitHub Personal Access Token | `github-pat` | `GITHUB_TOKEN` | `GITHUB_TOKEN` |
| Slack Bot Token | `slack-bot-token` | `SLACK_BOT_TOKEN` | `SLACK_BOT_TOKEN` |
| Datadog API Key | `datadog-api-key` | `DD_API_KEY` | `DD_API_KEY` |
| Datadog App Key | `datadog-app-key` | `DD_APP_KEY` | `DD_APP_KEY` |
| SendGrid API Key | `sendgrid-api-key` | `SENDGRID_API_KEY` | `SENDGRID_API_KEY` |

**Conventions:**

- Keychain service name (`-s`): always lowercase, hyphen-separated
- Keychain account name (`-a`): always the exact environment variable name in uppercase
  with underscores, this makes it trivially obvious which env var maps to which entry
- Environment variable name: follow the official SDK convention for the service

---

## Loading All Secrets at Once

Rather than exporting variables one by one in every terminal session, create a single
script that loads everything from Keychain.

### `load-secrets.sh`

Save this file to a location outside of any Git repository, for example
`~/.config/secrets/load-secrets.sh`.

```bash
#!/usr/bin/env bash
# load-secrets.sh
# Loads all API credentials from macOS Keychain into the current shell session.
# Usage: source ~/.config/secrets/load-secrets.sh
#
# Do NOT make this script executable and run it directly (./load-secrets.sh).
# It MUST be sourced (source or .) so the exports affect the current shell.

set -euo pipefail

# Helper: fetch from Keychain, fail with a clear message if the entry is missing
_load() {
  local env_var="$1"
  local service="$2"
  local account="$3"

  local value
  value=$(security find-generic-password -s "$service" -a "$account" -w 2>/dev/null || true)

  if [[ -z "$value" ]]; then
    echo "⚠️  Keychain: '$service' / '$account' not found — $env_var will not be set" >&2
    return 0
  fi

  export "$env_var"="$value"
}

# ── AWS ───────────────────────────────────────────────────────────────
_load AWS_ACCESS_KEY_ID    "aws-access-key"    "AWS_ACCESS_KEY_ID"
_load AWS_SECRET_ACCESS_KEY "aws-secret-key"   "AWS_SECRET_ACCESS_KEY"
# Uncomment if using temporary credentials:
# _load AWS_SESSION_TOKEN  "aws-session-token" "AWS_SESSION_TOKEN"

# ── MongoDB ───────────────────────────────────────────────────────────
_load MONGODB_URI          "mongodb-uri"       "MONGODB_URI"

# ── Cloudflare ────────────────────────────────────────────────────────
_load CLOUDFLARE_API_TOKEN "cloudflare-api-token" "CLOUDFLARE_API_TOKEN"
# _load CLOUDFLARE_ACCOUNT_ID "cloudflare-account-id" "CLOUDFLARE_ACCOUNT_ID"

echo "✅  Secrets loaded from Keychain"
```

**Line-by-line explanation:**

| Line | Purpose |
|---|---|
| `set -euo pipefail` | Exit on error (`-e`), treat unset variables as errors (`-u`), propagate pipe failures (`-o pipefail`) |
| `_load()` function | Generic helper that reads one Keychain entry and exports it as an environment variable |
| `2>/dev/null \|\| true` | Silences the error if the entry doesn't exist, letting the missing-value check handle it gracefully |
| `-z "$value"` check | If the value is empty (entry not found), print a warning to stderr and skip (don't hard-fail the entire script |
| `export "$env_var"="$value"` | Makes the variable available to all child processes (your application, CLI tools, etc.) |
| `echo "✅  Secrets loaded"` | Confirms the script ran without showing any values |

---

### Sourcing the Script

The script **must be sourced**, not executed. Executing it in a subshell means the
exports only exist inside that subshell, not in your current terminal:

```bash
# ✅ Correct — source it
source ~/.config/secrets/load-secrets.sh

# ✅ Also correct — the dot is an alias for source
. ~/.config/secrets/load-secrets.sh

# ❌ Wrong — exports are lost when the subshell exits
~/.config/secrets/load-secrets.sh
bash ~/.config/secrets/load-secrets.sh
```

**Optional: add an alias to `.zshrc`:**

```bash
# In ~/.zshrc — add this line at the bottom
alias load-secrets='source ~/.config/secrets/load-secrets.sh'
```

Then in any terminal session simply type `load-secrets`. This is the only secret-related
line that should ever appear in your `.zshrc`.

---

## Using Credentials in Applications

All examples below assume the environment variables are already exported (via
`load-secrets.sh` or manually).

### Node.js

```javascript
// Always read from process.env
const dbUri      = process.env.MONGODB_URI;
const cfToken    = process.env.CLOUDFLARE_API_TOKEN;
const awsKeyId   = process.env.AWS_ACCESS_KEY_ID;

if (!dbUri) {
  throw new Error("MONGODB_URI is not set. Run: source ~/.config/secrets/load-secrets.sh");
}
```

### Python

```python
import os

db_uri   = os.environ["MONGODB_URI"]          # raises KeyError if missing
cf_token = os.getenv("CLOUDFLARE_API_TOKEN")  # returns None if missing

if not cf_token:
    raise EnvironmentError(
        "CLOUDFLARE_API_TOKEN is not set. "
        "Run: source ~/.config/secrets/load-secrets.sh"
    )
```

### Go

```go
package main

import (
    "fmt"
    "os"
)

func main() {
    mongoURI := os.Getenv("MONGODB_URI")
    if mongoURI == "" {
        fmt.Fprintln(os.Stderr, "MONGODB_URI is not set")
        os.Exit(1)
    }

    cfToken := os.Getenv("CLOUDFLARE_API_TOKEN")
    if cfToken == "" {
        fmt.Fprintln(os.Stderr, "CLOUDFLARE_API_TOKEN is not set")
        os.Exit(1)
    }
}
```

### Rust

```rust
use std::env;

fn main() {
    let mongo_uri = env::var("MONGODB_URI")
        .expect("MONGODB_URI must be set. Run: source ~/.config/secrets/load-secrets.sh");

    let cf_token = env::var("CLOUDFLARE_API_TOKEN")
        .expect("CLOUDFLARE_API_TOKEN must be set.");

    println!("Connecting to MongoDB...");
}
```

### Shell Scripts

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${AWS_ACCESS_KEY_ID:?AWS_ACCESS_KEY_ID is not set. Source load-secrets.sh first.}"
: "${AWS_SECRET_ACCESS_KEY:?AWS_SECRET_ACCESS_KEY is not set.}"

aws s3 ls
```

The `${VAR:?message}` syntax causes the script to exit immediately with the error message
if the variable is unset or empty.

---

## AI Assistant Security Rules

The following rules are designed to be pasted directly into **Cursor Rules**,
**Claude Project Instructions**, or similar AI assistant configuration.

---

```
# AI Assistant Security Rules — API Credentials

## Credential Handling

- NEVER ask the user for actual API keys, tokens, passwords, connection strings,
  or any secret values.
- NEVER include placeholder secrets, example keys, or demo tokens in generated code
  that look realistic (e.g., "AKIA..." style strings).
- NEVER hardcode credentials in any file — not in source code, not in config files,
  not in scripts, not in Dockerfiles, not in comments.
- NEVER print, log, or echo environment variable values that may contain secrets.
- NEVER suggest storing secrets in .env files, shell profiles (.zshrc, .bash_profile),
  configuration files, or any file that could be committed to version control.
- NEVER create .env files that contain real credentials. If a .env.example file is
  appropriate, use only placeholder names like YOUR_API_KEY_HERE.
- NEVER suggest committing any file that contains or might contain secrets.

## Environment Variable Convention

- ALWAYS read credentials from environment variables.
- Assume credentials are already loaded from Apple Keychain via load-secrets.sh or
  equivalent. Do not suggest how to set the value — only how to read it.
- If a required environment variable is not set, generate code that exits with a clear
  error message naming the missing variable and instructing the user to load it from
  Keychain.
- Use the official environment variable names for each SDK:
  - AWS: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_REGION
  - MongoDB: MONGODB_URI
  - Cloudflare: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ZONE_ID
  - GitHub: GITHUB_TOKEN
  - Slack: SLACK_BOT_TOKEN

## Code Generation Rules

- Generated code must never contain actual credential values.
- Generated code must always validate that required environment variables are present
  before attempting to use them.
- If the user pastes a string that looks like an API key or token, inform them immediately
  that they should not share secrets with AI assistants, and do not use or reference the
  value in any response.
- Prefer `os.environ["VAR"]` (Python) or `process.env.VAR` (Node.js) over reading from
  files or constructing credentials from multiple parts.

## Git and Version Control

- NEVER suggest `git add .env` or any command that would stage secret-containing files.
- ALWAYS recommend .gitignore entries for .env, .env.local, credentials.json, and
  similar files when setting up a new project.
- If the user asks how to store credentials for a project, always recommend Keychain
  (macOS) or the equivalent secret manager for their platform.
```

---

## Git Best Practices

### `.gitignore`: Files That Must Never Be Committed

Add these entries to every project's `.gitignore` file:

```gitignore
# ── Secrets and credentials ───────────────────────────────────────────
.env
.env.*
!.env.example
credentials.json
credentials.yaml
credentials.yml
config.json
config.yaml
*.pem
*.key
*.p12
*.pfx
id_rsa
id_rsa.pub
id_ed25519
id_ecdsa
*.jks
secrets.json
secrets.yaml
secrets.md
keys.txt
token.txt
.secret
.secrets/
vault-token

# ── AWS ───────────────────────────────────────────────────────────────
.aws/credentials
.aws/config

# ── Google Cloud ──────────────────────────────────────────────────────
*-service-account.json
application_default_credentials.json
gcloud-credentials.json

# ── Node.js ───────────────────────────────────────────────────────────
node_modules/

# ── Python ────────────────────────────────────────────────────────────
*.pyc
__pycache__/
.venv/
venv/
```

The `!.env.example` line explicitly allows `.env.example` (a template with placeholder
variable names but no real values) while blocking all other `.env.*` files.

---

### Secret Scanning

**GitHub Secret Scanning** is a free feature that automatically scans every commit pushed
to a GitHub repository for known credential patterns (AWS keys, GitHub tokens, Slack
tokens, Cloudflare keys, etc.). When detected:

- GitHub notifies the repository owner by email
- For public repositories, GitHub notifies the affected service provider, which may
  immediately revoke the secret
- The alert appears in **Security** → **Secret scanning alerts** in the repository

**For private repositories**, GitHub Secret Scanning is available on GitHub Advanced
Security (included in GitHub Team and Enterprise plans).

To enable Secret Scanning:

1. Repository → **Settings** → **Security** → **Code security and analysis**
2. Enable **Secret scanning** and **Push protection**

**Push protection** blocks a push if a secret is detected, before it is written to the
remote repository's history.

---

### What to Do If a Secret Is Committed

Act **immediately**. Every minute the secret is in a public repository increases the risk.

**Step 1: Revoke the secret now**

Go to the service (AWS IAM, Cloudflare, MongoDB Atlas, etc.) and revoke or rotate the
compromised credential before doing anything else with Git. A secret that is revoked
cannot be exploited even if it is still visible in history.

**Step 2: Check for unauthorized use**

- AWS: CloudTrail → Event history
- Cloudflare: Audit Log in the dashboard
- MongoDB Atlas: Activity Feed in the project
- GitHub: Repository → Insights → Network (for unexpected forks)

**Step 3: Remove from Git history**

Use `git filter-branch` or the faster `git-filter-repo` tool:

```bash
# Install git-filter-repo (recommended over filter-branch)
brew install git-filter-repo

# Remove the file from all history
git filter-repo --path .env --invert-paths

# Force-push to replace remote history
git push origin --force --all
```

> **Warning:** `git push --force` rewrites remote history. All collaborators must
> re-clone or hard-reset their local copies. Co-ordinate with your team before doing this.

**Step 4: Generate a new credential**

Create a new key/token after revoking the old one. Store it in Keychain. Never in a file.

**Step 5: Review and prevent recurrence**

Add the file type to `.gitignore`. Consider enabling GitHub Push Protection.

---

## Security Best Practices Checklist

### Keychain and Local Machine

- [ ] All secrets stored in macOS Keychain, zero secrets in plain text files
- [ ] `load-secrets.sh` lives outside any Git repository (`~/.config/secrets/`)
- [ ] `load-secrets.sh` has permissions `600` (`chmod 600 ~/.config/secrets/load-secrets.sh`)
- [ ] No secrets in `.zshrc`, `.bashrc`, `.bash_profile`, or any shell config file
- [ ] No secrets in `~/.profile`, `~/.zprofile`, or login scripts
- [ ] macOS login password is strong (12+ characters, not reused)
- [ ] macOS FileVault is enabled (disk encryption protects Keychain when off)
- [ ] Mac locks automatically after 5 minutes of inactivity
- [ ] macOS user account does not have "automatic login" enabled

### AWS

- [ ] Root account MFA enabled
- [ ] No access keys created for the root account
- [ ] All programmatic access through IAM users or roles
- [ ] IAM users have only the minimum permissions required
- [ ] Access keys rotated every 90 days or less
- [ ] Old access keys deleted after rotation (not just deactivated)
- [ ] CloudTrail enabled in all regions
- [ ] IAM Access Analyzer enabled
- [ ] No access keys shared between developers
- [ ] CI/CD uses OIDC or IAM roles, not long-term access keys

### MongoDB Atlas

- [ ] Root Atlas account has MFA enabled
- [ ] Separate database users per application and per environment
- [ ] Database users have the minimum role required (`readWrite` on specific DB only)
- [ ] IP Access List is not `0.0.0.0/0` in production
- [ ] Atlas Audit Log enabled in production
- [ ] Database user passwords rotated when team members leave
- [ ] Connection string stored only in Keychain, not in any file

### Cloudflare

- [ ] Global API Key is not used anywhere, only scoped API Tokens
- [ ] Each API Token scoped to the minimum zones and permissions required
- [ ] IP address filtering configured on tokens where possible
- [ ] TTL set on tokens used in CI pipelines
- [ ] Cloudflare Audit Log reviewed periodically
- [ ] Compromised tokens revoked immediately (not just rotated)

### Git and Version Control

- [ ] `.gitignore` contains entries for all secret file patterns
- [ ] GitHub Secret Scanning enabled on all repositories
- [ ] GitHub Push Protection enabled on all repositories
- [ ] Pre-commit hooks installed to block `.env` files (consider `detect-secrets` or `gitleaks`)
- [ ] No secrets in commit messages (connection strings, passwords, tokens)
- [ ] Historical commits audited for accidentally committed secrets
- [ ] `.env.example` provided with placeholder values instead of real values
- [ ] `CONTRIBUTING.md` documents the credential management workflow for new contributors

### Applications and Code

- [ ] Application startup fails fast with a clear error if a required env var is missing
- [ ] No credentials in application logs
- [ ] No credentials in error messages returned to clients
- [ ] No credentials in URLs (query strings, path parameters)
- [ ] Dependencies reviewed for known vulnerabilities (`npm audit`, `pip-audit`, etc.)
- [ ] SDKs are configured to read from environment, not from hardcoded values

---

## Troubleshooting

### macOS Asks for Keychain Password Repeatedly

**Cause:** The Keychain access control for the entry was set to "Confirm before
allowing access" or your login Keychain is set to lock after a period of inactivity.

**Fix:**

1. Open **Keychain Access.app** (Spotlight → "Keychain Access")
2. Find the entry under "login" keychain
3. Right-click → **Get Info** → **Access Control** tab
4. Check "Allow all applications to access this item" (for development entries only)
5. Alternatively, increase or disable the lock timeout: Keychain Access →
   Edit → Change Settings for Keychain "login" → set "Lock after X minutes" to a
   higher value

---

### `security: SecKeychainSearchCopyNext: The specified item could not be found.`

**Cause:** The `-s` or `-a` value does not exactly match what was used when storing the
entry. Keychain lookups are case-sensitive.

**Fix:** Verify the exact values used when the entry was created:

```bash
# List all generic passwords to see exact service and account names
security dump-keychain | grep -A5 "svce\|acct" | grep -E '"svce"|"acct"'
```

Or open Keychain Access.app and search for the entry visually.

---

### Environment Variable Is Empty After Export

**Cause 1:** The script was executed rather than sourced.

```bash
# Wrong — runs in a subshell, exports are lost
bash ~/.config/secrets/load-secrets.sh

# Correct
source ~/.config/secrets/load-secrets.sh
```

**Cause 2:** The Keychain entry exists but the value is empty.

```bash
# Check if the entry exists and has a non-empty value
security find-generic-password -s "service-name" -a "ACCOUNT_NAME" -w
```

---

### Application Cannot See the Environment Variable

**Cause:** The application was launched before `load-secrets.sh` was sourced, or it was
launched from a different terminal session.

**Fix:** Source the secrets script in the same terminal session before launching the
application:

```bash
source ~/.config/secrets/load-secrets.sh
node index.js          # or python app.py, go run main.go, etc.
```

If launching from an IDE like VS Code or Cursor, set the environment variables in the
integrated terminal before running the project, or configure the IDE's launch settings to
run `load-secrets.sh` as a pre-launch task.

---

### `security` Command Returns Error Code 44

Error code 44 means the Keychain item was not found. Double-check the exact service and
account names used:

```bash
security find-generic-password -s "exact-service-name" -a "EXACT_ACCOUNT_NAME" -w
```

Common mistakes: trailing spaces in the service name, different capitalisation, or using
a colon (`:`) in the service name which some versions of macOS handle inconsistently.

---

### Cannot Add Entry: "The specified item already exists"

**Cause:** An entry with the same `-s` and `-a` already exists and `-U` was not used.

**Fix:** Always use the `-U` flag when adding credentials:

```bash
security add-generic-password -s "service" -a "ACCOUNT" -w "$value" -U
```

Or delete the existing entry and re-add it:

```bash
security delete-generic-password -s "service" -a "ACCOUNT"
security add-generic-password -s "service" -a "ACCOUNT" -w "$value"
```

---

### Keychain Is Locked After macOS Restart

By default, the login Keychain unlocks automatically when you log in. If this is not
happening, it means the login Keychain password has become out of sync with your login
password (can happen after a password reset).

**Fix:**

1. Open **Keychain Access.app**
2. Right-click on **"login"** in the left panel → **Change Password for Keychain "login"**
3. Enter the old Keychain password and set the new one to match your login password

---

## Appendix: Quick Reference Cheat Sheet

### Keychain Commands

```bash
# Add / update a secret (interactive, hidden input)
printf 'Value: '; read -s v && echo && \
security add-generic-password -s "SERVICE" -a "ACCOUNT" -w "$v" -U && unset v

# Retrieve a secret value
security find-generic-password -s "SERVICE" -a "ACCOUNT" -w

# Verify an entry exists (no value shown)
security find-generic-password -s "SERVICE" -a "ACCOUNT"

# Export as environment variable
export MY_VAR="$(security find-generic-password -s "SERVICE" -a "ACCOUNT" -w)"

# Delete an entry
security delete-generic-password -s "SERVICE" -a "ACCOUNT"
```

---

### Credential Entries: Standard Names

```bash
# AWS
security add-generic-password -s "aws-access-key"    -a "AWS_ACCESS_KEY_ID"       -w "$v" -U
security add-generic-password -s "aws-secret-key"    -a "AWS_SECRET_ACCESS_KEY"   -w "$v" -U
security add-generic-password -s "aws-session-token" -a "AWS_SESSION_TOKEN"       -w "$v" -U

# MongoDB
security add-generic-password -s "mongodb-uri"       -a "MONGODB_URI"             -w "$v" -U

# Cloudflare
security add-generic-password -s "cloudflare-api-token"  -a "CLOUDFLARE_API_TOKEN"    -w "$v" -U
security add-generic-password -s "cloudflare-account-id" -a "CLOUDFLARE_ACCOUNT_ID"   -w "$v" -U
```

---

### Useful Links

| Resource | URL |
|---|---|
| Apple `security` man page | `man security` in Terminal, or [ss64.com/osx/security.html](https://ss64.com/osx/security.html) |
| Apple Keychain documentation | [developer.apple.com/documentation/security/keychain_services](https://developer.apple.com/documentation/security/keychain_services) |
| AWS IAM Best Practices | [docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) |
| AWS Access Key Rotation | [docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) |
| MongoDB Atlas Connection Strings | [www.mongodb.com/docs/atlas/connect-to-database-deployment](https://www.mongodb.com/docs/atlas/connect-to-database-deployment/) |
| MongoDB Atlas Database Users | [www.mongodb.com/docs/atlas/security-add-mongodb-users](https://www.mongodb.com/docs/atlas/security-add-mongodb-users/) |
| Cloudflare API Tokens | [developers.cloudflare.com/fundamentals/api/get-started/create-token](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/) |
| Cloudflare API Token Permissions | [developers.cloudflare.com/fundamentals/api/reference/permissions](https://developers.cloudflare.com/fundamentals/api/reference/permissions/) |
| GitHub Secret Scanning | [docs.github.com/en/code-security/secret-scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning) |
| GitHub Push Protection | [docs.github.com/en/code-security/secret-scanning/push-protection-for-repositories-and-organizations](https://docs.github.com/en/code-security/secret-scanning/push-protection-for-repositories-and-organizations) |
| `gitleaks`, Git secret scanner | [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) |
| `detect-secrets` (pre-commit hook | [github.com/Yelp/detect-secrets](https://github.com/Yelp/detect-secrets) |
| `git-filter-repo` (history rewriting | [github.com/newren/git-filter-repo](https://github.com/newren/git-filter-repo) |

---

*Last updated: August 2026 · Part of [tech-notes](https://github.com/Tarunrj99/tech-notes) · [Back to mac/](../README.md)*
