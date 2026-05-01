# GCS Bucket — Public File Access & Security Setup Guide

> Configure a Google Cloud Storage bucket so files are **publicly readable via URL** but the bucket **cannot be listed** by outsiders. Includes a Cloud Function that auto-applies public-read ACL to every new upload.

**Purpose:** Make specific objects in a GCS bucket publicly accessible by URL, without exposing the bucket's file index.
**Target:** Google Cloud Storage (GCS), Cloud Functions Gen 2, Eventarc.
**Tested on:** GCP — `gcloud` CLI 466+ · Cloud Function runtime `python311`.

[Back to repo root](../../README.md) · [`cloud/gcp/`](./README.md) · [Repo conventions](../../AGENTS.md)

---

## Table of contents

1. [Why this is non-obvious](#why-this-is-non-obvious)
2. [Access-control concepts (IAM vs ACL vs UBLA)](#access-control-concepts-iam-vs-acl-vs-ubla)
3. [Best practices for new buckets](#best-practices-for-new-buckets)
4. [Make an existing bucket "URL-accessible but unlistable"](#make-an-existing-bucket-url-accessible-but-unlistable)
5. [Auto-publish future uploads — Cloud Function (Gen 2)](#auto-publish-future-uploads--cloud-function-gen-2)
6. [Bulk-publish existing files (long-running, Cloud Shell)](#bulk-publish-existing-files-long-running-cloud-shell)
7. [Security guarantees](#security-guarantees)
8. [Troubleshooting](#troubleshooting)

---

## Why this is non-obvious

Most teams hit one of these surprises:

- They make the bucket public via IAM (`allUsers` → `Storage Object Viewer`) — but that role **also grants `list` permission**, so anyone who knows the bucket name can enumerate every file.
- They turn on **Uniform Bucket-Level Access (UBLA)** — which is the modern default — and then can't make a single object public without granting bucket-wide read.

The clean answer is: **disable UBLA + use object-level ACLs**. URL access works; listing doesn't. Below is the full setup, plus an automation Cloud Function so you never have to remember to apply the ACL by hand.

> **"List" means**: a user without project credentials can run `gsutil ls gs://<bucket>` and see every file, just by knowing the bucket name. That's what we want to prevent.

---

## Access-control concepts (IAM vs ACL vs UBLA)

| Control type | Scope | What it does | Notes |
| --- | --- | --- | --- |
| **IAM** (Identity and Access Management) | Bucket / project | Roles like `Storage Object Viewer`, `Storage Object Admin` | Any bucket-level read role **includes list permission** |
| **ACL** (Access Control List) | Object (per-file) | Read/write access on individual files | Can make a file public **without** giving bucket listing rights |
| **UBLA** (Uniform Bucket-Level Access) | Bucket | When ON, **disables ACLs**; access is controlled fully by IAM | If ON, you cannot make a single file public without allowing listing |
| `allUsers` | Global | Everyone on the internet (anonymous) | Public access if granted via IAM **or** ACL |
| `allAuthenticatedUsers` | Global | Any signed-in Google account | Grants access to all logged-in users |

---

## Best practices for new buckets

For **private** buckets:

- Enable UBLA (uniform access via IAM only).
- Never grant `allUsers` or `allAuthenticatedUsers` at the bucket level.
- Apply **public access prevention** policy.

For buckets that need **per-object public URLs** (this guide):

- Leave UBLA **off** (you need ACLs).
- Never grant `allUsers` IAM at the bucket level.
- Use the Cloud Function below to apply per-object public-read ACL on upload.

---

## Make an existing bucket "URL-accessible but unlistable"

> Goal: users can `curl https://storage.googleapis.com/<bucket>/<file>` to download, but `gsutil ls gs://<bucket>` returns AccessDenied for unauthenticated callers.

### Step 1 — Disable Uniform Bucket-Level Access (UBLA)

ACLs only work when UBLA is OFF.

**Console:** Storage → Bucket → Permissions → Uniform bucket-level access → toggle OFF.

**CLI:**

```bash
gcloud storage buckets update gs://<your-bucket-name> \
  --no-uniform-bucket-level-access
```

> **Why:** With UBLA ON, ACLs are disabled, you cannot mark individual files as public, and you cannot achieve "read without list".

### Step 2 — Remove public IAM roles (stop bucket listing)

Strip any `allUsers` or `allAuthenticatedUsers` entries at the bucket level.

**Console:** Storage → Bucket → Permissions → delete all public IAM roles.

**CLI:**

```bash
gcloud storage buckets remove-iam-policy-binding gs://<your-bucket-name> \
  --member=allUsers \
  --role=roles/storage.legacyObjectReader

gcloud storage buckets remove-iam-policy-binding gs://<your-bucket-name> \
  --member=allUsers \
  --role=roles/storage.objectViewer
```

### Step 3 — Make a single file public via ACL

```bash
gsutil acl ch -u AllUsers:R gs://<your-bucket-name>/path/to/file.pdf
```

After this:

- `curl -I https://storage.googleapis.com/<your-bucket-name>/path/to/file.pdf` → `200 OK`
- `gsutil ls gs://<your-bucket-name>` → `AccessDeniedException` (good)

### Step 4 — (Optional) Make all existing files public in one shot

For an existing bucket where every current file should become public:

```bash
gsutil -m acl ch -R -u AllUsers:R gs://<your-bucket-name>
```

| Flag | Meaning |
| --- | --- |
| `-m` | Run in parallel (much faster on large buckets) |
| `-R` | Recursive — every folder and file |

---

## Auto-publish future uploads — Cloud Function (Gen 2)

> Goal: **every new upload to a specific bucket** automatically receives `allUsers:READER` ACL — no manual `gsutil acl ch` ever again.

### Architecture

```
Any upload to bucket
         │
         ▼
   Eventarc (object.finalized)
         │
         ▼
   Cloud Function (Gen 2, Python)
         │
         ▼
   Apply ACL → allUsers : READER
```

### 1. Function code

**`main.py`:**

```python
from google.cloud import storage

ALLOWED_BUCKETS = {
    "<your-bucket-name>",
}


def make_object_public(event, context):
    data = event

    bucket_name = data.get("bucket")
    object_name = data.get("name")

    if not bucket_name or not object_name:
        print("Missing bucket or object name")
        return

    if object_name.endswith("/"):
        return

    if bucket_name not in ALLOWED_BUCKETS:
        print(f"Skipping bucket: {bucket_name}")
        return

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    blob.acl.all().grant_read()
    blob.acl.save()

    print(f"Public ACL applied: gs://{bucket_name}/{object_name}")
```

**`requirements.txt`:**

```
google-cloud-storage
```

### 2. Deploy the function

Replace `<your-gcp-project-id>` and the trigger bucket name. Region must match the bucket's location.

```bash
gcloud functions deploy gcs-public-read-acl \
  --gen2 \
  --project=<your-gcp-project-id> \
  --region=us-central1 \
  --runtime=python311 \
  --entry-point=make_object_public \
  --trigger-location=us \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=<your-bucket-name>"
```

> Deploy takes ~2 minutes. GCP automatically creates the corresponding **Eventarc trigger** for you. You cannot create another trigger with the same destination — and you don't need to.

### 3. Verify the trigger was created

```bash
gcloud eventarc triggers list \
  --location=us \
  --project=<your-gcp-project-id>
```

Look for an auto-named trigger pointing at `Cloud Run service gcs-public-read-acl`.

```bash
gcloud eventarc triggers describe <trigger-name> \
  --location=us \
  --project=<your-gcp-project-id>
```

Confirm:

- `bucket: <your-bucket-name>`
- `eventType: google.cloud.storage.object.v1.finalized`

### 4. Grant the function service account permission to write ACLs (CRITICAL)

The function runs as the App Engine default service account:

```
<your-gcp-project-id>@appspot.gserviceaccount.com
```

It needs `Storage Object Admin` to mutate ACLs:

```bash
gcloud projects add-iam-policy-binding <your-gcp-project-id> \
  --member="serviceAccount:<your-gcp-project-id>@appspot.gserviceaccount.com" \
  --role="roles/storage.objectAdmin" \
  --condition=None
```

> **Important:** This only lets the function write ACLs on objects. It does **not** make the bucket publicly listable.

### 5. Test it

Upload a file → confirm public read → confirm listing still blocked.

```bash
gsutil cp test.pdf gs://<your-bucket-name>/test/test.pdf

curl -I https://storage.googleapis.com/<your-bucket-name>/test/test.pdf
# Expect: HTTP/1.1 200 OK

gsutil ls gs://<your-bucket-name>
# Expect: AccessDeniedException
```

### 6. Check function logs

```bash
gcloud functions logs read gcs-public-read-acl \
  --gen2 \
  --region=us-central1 \
  --project=<your-gcp-project-id>
```

You should see:

```
Public ACL applied: gs://<your-bucket-name>/test/test.pdf
```

### 7. Adding more buckets later

Edit `ALLOWED_BUCKETS` in `main.py` and redeploy:

```python
ALLOWED_BUCKETS = {
    "<your-bucket-name>",
    "<another-bucket-name>",
}
```

> Want zero-redeploy bucket changes? Move `ALLOWED_BUCKETS` to an environment variable and use `--update-env-vars` instead.

---

## Bulk-publish existing files (long-running, Cloud Shell)

`gsutil -m acl ch -R` on a multi-TB bucket can take hours. Run it in the background so a Cloud Shell disconnect doesn't kill it.

> **Cloud Shell already runs inside `tmux`** by default — no need to install `screen` or start your own `tmux`. Just use `nohup`.

```bash
nohup gsutil -m acl ch -R -u AllUsers:R gs://<your-bucket-name> \
  > gsutil-acl.log 2>&1 &
```

### Monitor progress

```bash
ps aux | grep gsutil
tail -f gsutil-acl.log
```

`Ctrl+C` stops the `tail` only — the background job keeps running.

### Stop the job if needed

```bash
pkill -f "gsutil -m acl ch"
```

> This is a **one-time** fix for legacy objects. Future uploads are handled by the Cloud Function — no need to repeat.

---

## Security guarantees

After this setup:

| Requirement | Result |
| --- | --- |
| Public read by URL | ✅ |
| No bucket listing | ✅ |
| Fine-grained per-object ACL | ✅ |
| Multi-bucket support (via `ALLOWED_BUCKETS`) | ✅ |
| No bulk `gsutil` needed for new files | ✅ |

### Caveats

- The Cloud Function **only handles new uploads** (event type `object.finalized`). Existing objects need the one-time `gsutil acl ch -R` (above).
- ACL approach requires the bucket to be **fine-grained** (UBLA off). It will not work on UBLA-enabled buckets.
- The Cloud Function service account has `Storage Object Admin` — this is project-wide. If you need tighter scope, replace the App Engine default SA with a dedicated SA bound only to the target bucket.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `gsutil acl ch` returns "ACLs are not enabled" | UBLA is ON | Disable UBLA (Step 1) |
| File returns `403` via public URL | Object ACL not set OR bucket has Public Access Prevention | `gsutil acl get gs://<bucket>/<file>` to inspect; remove PAP via console |
| `gsutil ls gs://<bucket>` succeeds anonymously | A public IAM role is still bound at bucket level | Re-run Step 2 to strip `allUsers` from bucket IAM |
| Cloud Function deploys but objects still aren't public | Function SA missing `roles/storage.objectAdmin` | Re-run Step 4 of the function setup |
| Function deploy fails with "trigger already exists" | Eventarc auto-created the trigger; you can't manually add another | Delete the existing trigger or re-use it |
| Cloud Function runs but logs `Skipping bucket: ...` | Bucket name not in `ALLOWED_BUCKETS` set | Add it and redeploy |

---

## Reference

- [GCS — Access control overview](https://cloud.google.com/storage/docs/access-control)
- [GCS — Uniform bucket-level access](https://cloud.google.com/storage/docs/uniform-bucket-level-access)
- [GCS — Object ACLs](https://cloud.google.com/storage/docs/access-control/lists)
- [Cloud Functions Gen 2 — Eventarc triggers](https://cloud.google.com/functions/docs/calling/eventarc)
