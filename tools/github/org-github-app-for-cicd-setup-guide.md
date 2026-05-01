# Org-Owned GitHub App for CI/CD — Setup & Migration Guide

> Replace the user-PAT or "service-user account" your CI/CD currently authenticates as with an **org-owned GitHub App** that mints short-lived installation tokens. No more PAT rotation, no more "the cicd-bot user just left the company" outages.

**Purpose:** Stand up a GitHub App owned by your organization so CI jobs authenticate as the app (not as a person), then migrate your centralized workflows and downstream app repos to use it.
**Target:** GitHub Organizations · GitHub Actions · centralized reusable workflows.
**You'll end up with:** A GitHub App in the org · An App ID + private key (`.pem`) stored in CI secrets · Repos installed and migrated.

[Back to repo root](../../README.md) · [`tools/github/`](./README.md) · [Repo conventions](../../AGENTS.md)

---

## Table of contents

1. [Why use a GitHub App instead of a PAT or service user](#why-use-a-github-app-instead-of-a-pat-or-service-user)
2. [Prerequisites](#prerequisites)
3. [Step 1 — Create the GitHub App (org-owned)](#step-1--create-the-github-app-org-owned)
4. [Step 2 — Generate App ID + private key, store as secrets](#step-2--generate-app-id--private-key-store-as-secrets)
5. [Step 3 — Install the App on the repos CI/CD needs](#step-3--install-the-app-on-the-repos-cicd-needs)
6. [Step 4 — Use the App in a workflow](#step-4--use-the-app-in-a-workflow)
7. [Step 5 — Migrate centralized workflows to the new token](#step-5--migrate-centralized-workflows-to-the-new-token)
8. [Step 6 — Update application repos (`secrets: inherit`)](#step-6--update-application-repos-secrets-inherit)
9. [Step 7 — Org-wide bulk migration script](#step-7--org-wide-bulk-migration-script)
10. [PR description requirements (`check_screenshots` workflow)](#pr-description-requirements-check_screenshots-workflow)
11. [Troubleshooting](#troubleshooting)

---

## Why use a GitHub App instead of a PAT or service user

| Problem with PAT / service user | Fixed by GitHub App |
| --- | --- |
| Token tied to a person — leaves the company → CI breaks | App is org-owned, lives forever |
| Long-lived secret (often `repo` scope on the entire org) | Tokens are minted per-job, expire in ~1 hour |
| Hard to scope to specific repos | App permissions + selective install give per-repo scope |
| Auditing shows "user X did it" — not what actually ran | Audit shows the app name, easy to spot CI-driven actions |
| Manual rotation, painful at scale | Rotate the private key, update one secret, done |

---

## Prerequisites

- **Org admin** (or someone with permission to create and manage GitHub Apps in the organization).
- A clear list of repositories CI/CD needs to access — split into "checkout-only" vs "writes commits/tags/releases".

---

## Step 1 — Create the GitHub App (org-owned)

1. Open your GitHub Organization in the browser.
   Navigate to: **Settings → Developer settings → GitHub Apps → New GitHub App**.
2. Fill in basic details:
   - **GitHub App name:** Pick something obviously CI/CD, e.g. `<your-org>-cicd-automation` or `<your-org>-ci`.
   - **Description:** `CI/CD service identity for org-wide automation.`
   - **Homepage URL:** Any valid URL (a wiki page, internal docs link, or even the org URL is fine).
3. Webhooks and callbacks:
   - **Webhook:** Disable unless you explicitly need webhook events.
   - **Callback URL:** Leave empty if the app is only for CI/CD token minting.
   - **Expire user authorization tokens:** Leave **unchecked** for CI/CD use — installation tokens don't use refresh tokens; this setting only affects user OAuth flows.
4. Where the app can be installed:
   - **Only on this account (organization)** — unless you have a specific reason to allow broader installs.
5. **Repository permissions** (start minimal — expand only when a job fails with `403`):

   | Permission | Recommended default | Increase to **Read & write** when |
   | --- | --- | --- |
   | **Metadata** | Read-only (required) | n/a |
   | **Contents** | Read-only | CI pushes commits/tags, creates releases, or updates files |
   | **Pull requests** | Not set / Read-only | CI creates or updates PRs |
   | **Issues** | Not set / Read-only | CI creates or updates issues |
   | **Actions** | Not set | CI manages workflow runs |
   | **Packages** | Not set / Read-only | CI publishes/reads GitHub Packages |

6. Click **Create GitHub App**.

---

## Step 2 — Generate App ID + private key, store as secrets

1. Open the app's settings page (you'll land there right after creation).
2. Copy the numeric **App ID** — you'll use it as `CICD_APP_ID`.
3. Click **Generate a private key** — a `.pem` file downloads. **Don't commit this anywhere.**

### Add Actions secrets

Prefer **Org-level** secrets if multiple repos will use the app — one place to rotate.

- **Org-level (recommended):** Org → Settings → Secrets and variables → Actions → **New organization secret**.
- **Repo-level:** Repo → Settings → Secrets and variables → Actions → **New repository secret**.

| Secret name | Value | Where to find it |
| --- | --- | --- |
| `CICD_APP_ID` | The numeric App ID | App settings page → App ID |
| `CICD_APP_PRIVATE_KEY` | Full contents of the `.pem` file (including `-----BEGIN ...-----` and `-----END ...-----` lines) | The `.pem` file you just downloaded |

### Private key safety rules

- ❌ **Never commit** the `.pem` file to any repo (add `*.pem` to `.gitignore` to be safe).
- ✅ Store only in a secret manager (GitHub Actions secrets, Vault, AWS Secrets Manager, etc.).
- 🔄 Plan for **key rotation**: generate a new key in the app → update the secret → delete the old key from the app.

---

## Step 3 — Install the App on the repos CI/CD needs

1. From the GitHub App page, click **Install App**.
2. Pick the install scope:
   - **All repositories** — convenient if your CI/CD centrally manages many repos (common for org-wide pipelines).
   - **Only select repositories** — recommended if CI only touches a small set, or you want tighter scope.
3. Complete the install.

> You can revisit and change the install scope anytime from **Org Settings → Installed GitHub Apps → Configure**.

---

## Step 4 — Use the App in a workflow

The community-standard action [`actions/create-github-app-token`](https://github.com/actions/create-github-app-token) mints a short-lived installation token from the App ID + private key. Pass that token to `actions/checkout` (or any other action that takes a token).

### Same-repo checkout (simplest case)

```yaml
- name: Create GitHub App token
  id: app-token
  uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ secrets.CICD_APP_ID }}
    private-key: ${{ secrets.CICD_APP_PRIVATE_KEY }}

- name: Checkout
  uses: actions/checkout@v4
  with:
    token: ${{ steps.app-token.outputs.token }}
```

### Cross-repo checkout (explicit scope — recommended)

```yaml
- name: Create GitHub App token (scoped)
  id: app-token
  uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ secrets.CICD_APP_ID }}
    private-key: ${{ secrets.CICD_APP_PRIVATE_KEY }}
    owner: <your-org>
    repositories: <target-repo-name>

- name: Checkout another private repo
  uses: actions/checkout@v4
  with:
    repository: <your-org>/<target-repo-name>
    token: ${{ steps.app-token.outputs.token }}
```

> **When to specify `owner` / `repositories`:**
> - **Not strictly required** if your job only needs the current repository and the app is installed on it.
> - **Recommended** for cross-repo access (checking out other repos, scanning other repos, org-wide automation) — it ensures the minted token is scoped only to what the job needs.
> - If you see `Not Found while determining the default branch`, the token cannot reach the target repo (the app is not installed there, or the token scope didn't include it). Add explicit `owner` + `repositories`.

### Minimal validation workflow

Use this to confirm the app token can reach a specific private repo before rolling out.

```yaml
name: GitHub App Token Test

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Create GitHub App token (scoped)
        id: app-token
        uses: actions/create-github-app-token@v1
        with:
          app-id: ${{ secrets.CICD_APP_ID }}
          private-key: ${{ secrets.CICD_APP_PRIVATE_KEY }}
          owner: <your-org>
          repositories: <target-repo-name>

      - name: Checkout target repository
        uses: actions/checkout@v4
        with:
          repository: <your-org>/<target-repo-name>
          token: ${{ steps.app-token.outputs.token }}

      - name: Verify checkout
        run: |
          pwd
          ls -la
```

> **Failure tip:** `403 / Resource not accessible` → the app is missing the required permission, **or** the app is not installed on the target repo.

---

## Step 5 — Migrate centralized workflows to the new token

If your org uses a **centralized workflow repo** (e.g. `<your-org>/<centralized-workflows-repo>`) that all app repos call via `uses: <your-org>/<centralized-workflows-repo>/.github/workflows/build.yml@v3`, here's the upgrade strategy.

### Strategy: cut a new versioned branch (e.g. `v4`)

- ☐ Create branch **`v4`** from the existing stable branch (`v3`) in the centralized workflow repo.
- ☐ In every centralized workflow file, replace the old PAT secret reference (e.g. `TOKEN_GITHUB_CICD`) with `CICD_APP_ID` + `CICD_APP_PRIVATE_KEY` in the `secrets:` declaration.
- ☐ Add a **"Create GitHub App token"** step before every cross-repo checkout step in each job.
- ☐ Replace all `token: '${{ secrets.TOKEN_GITHUB_CICD }}'` references with `token: '${{ steps.app-token.outputs.token }}'`.
- ☐ Push `v4` and validate with **one** application repo before rolling out.

### Token-minting pattern (paste before every cross-repo checkout)

```yaml
- name: Create GitHub App token
  id: app-token
  uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ secrets.CICD_APP_ID }}
    private-key: ${{ secrets.CICD_APP_PRIVATE_KEY }}
    owner: <your-org>

- name: Checkout shared config repo
  uses: actions/checkout@v4
  with:
    repository: <your-org>/<shared-config-repo>
    sparse-checkout: pipeline-config
    token: '${{ steps.app-token.outputs.token }}'
    ref: master
```

### Files in a centralized workflow repo that typically need the upgrade

| File | What changes |
| --- | --- |
| `build.yml` | Replace secret + add token minting in `envvars` and build jobs. Update any `GITHUB_NPM_PACKAGE_TOKEN`-style env var. |
| `deploy.yml` | Replace secret + add token minting in `envvars` and every per-environment deploy job. |
| `release.yml` | Replace secret + add token minting in `envvars` and all release jobs. |
| `codescan.yml` | Replace secret + add token minting in `envvars` job. |
| `post-deploy.yml` | Replace secret + add token minting in `envvars` job. |
| `post-release.yml` | Replace secret + add token minting in `envvars` job. |
| `veracode-scan.yml` (or other SAST) | Replace secret + add token minting in `envvars` and the scan job (cross-repo checkout). |
| `veracode-sca.yml` (or other SCA) | Replace secret + add token minting. Update `github_token:` references in the SCA action. |

---

## Step 6 — Update application repos (`secrets: inherit`)

Each application repo has small workflow files that call the centralized workflows. Two changes per app repo:

1. Point at the **new branch** (`@v4` instead of `@v3`).
2. Replace explicit `secrets:` blocks with `secrets: inherit`.

### Before (old — explicit secrets, brittle)

```yaml
build:
  name: Build
  uses: <your-org>/<centralized-workflows-repo>/.github/workflows/build.yml@v3
  with:
    REPO_NAME: <example-app>
  secrets:
    GCP_CREDENTIAL_PROD: ${{ secrets.GCP_CREDENTIAL_PROD }}
    TOKEN_GITHUB_CICD: ${{ secrets.TOKEN_GITHUB_CICD }}
    SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

### After (new — `secrets: inherit`)

```yaml
build:
  name: Build
  uses: <your-org>/<centralized-workflows-repo>/.github/workflows/build.yml@v4
  with:
    REPO_NAME: <example-app>
  secrets: inherit
```

> **Why `secrets: inherit` works:** It auto-passes ALL org-level and repo-level secrets to the called workflow — including `CICD_APP_ID` and `CICD_APP_PRIVATE_KEY` — without listing every secret in every app's workflow file. This is what makes future secret additions zero-touch for app repos.

### Test approach (before rolling out to all repos)

- ☐ Pick **one** application repo as the test (e.g. a small frontend or internal tool).
- ☐ Create branch `feature/replace-token-with-github-app` from its `dev`/`main` branch.
- ☐ Update its workflow files to point at the **test branch** of the centralized workflows (e.g. `@feature/replace-token-with-github-app`).
- ☐ Open a PR and verify all CI jobs pass.
- ☐ Once green, cut the final `v4` branch on the centralized repo and roll out to all app repos.

---

## Step 7 — Org-wide bulk migration script

To migrate many app repos at once, use the GitHub CLI (`gh`). This is the bare-bones outline — adapt to your exact secret names and centralized workflow path.

### Steps

- ☐ Identify all repos referencing the old centralized version (e.g. `@v3`) using `gh search` or the API.
- ☐ For each repo: clone the dev branch, create `feature/replace-token-with-github-app`, update workflow files, commit, push, open PR.

### Per-repo automation script outline

```bash
#!/usr/bin/env bash
set -euo pipefail

# Iterate over each application repo
for REPO in "${REPOS[@]}"; do
  git clone --branch dev "https://x-access-token:${GH_TOKEN}@github.com/<your-org>/${REPO}.git"
  cd "${REPO}"

  git checkout -b feature/replace-token-with-github-app

  # 1) Bump centralized workflow ref
  sed -i 's|@v3|@v4|g' .github/workflows/*.yml

  # 2) Replace explicit `secrets:` blocks with `secrets: inherit`
  #    (use a small Python/Node script for safe YAML edits — sed alone is fragile here)

  git add .github/workflows/
  git commit -m "ci: migrate to org-owned GitHub App for CI/CD auth"
  git push -u origin feature/replace-token-with-github-app

  gh pr create \
    --base dev \
    --head feature/replace-token-with-github-app \
    --title "ci: migrate to org-owned GitHub App for CI/CD auth" \
    --body "Switching CI auth from the personal PAT to the org-owned GitHub App.

![screenshot](<your-public-image-url>)"

  cd ..
done
```

### Skip a repo if any of these are true

- It does not have the expected branch (e.g. no `dev` branch).
- Branch protection blocks direct push (handle manually or request a bypass).
- It does not reference the old centralized version anywhere in `.github/workflows/`.

---

## PR description requirements (`check_screenshots` workflow)

Some orgs ship an **org-level workflow** (e.g. `<your-org>/.github/workflows/check_screenshots.yaml`) that runs on every PR and **fails** if the PR description does not contain an image.

### What the check looks for (in PR body, not comments)

- Markdown image syntax: `![alt text](image-url)`
- HTML img tag: `<img src="url" />`

> **Important:** the check reads the **PR description (body)**, NOT PR comments. Pasting the image URL as a plain link in a comment will not pass.

### ✅ Correct PR body format

```
Your PR description text here.

![screenshot](https://your-public-image-url.png)
```

### ❌ Wrong — these will fail the check

```
# Plain URL in a comment — does NOT work
https://your-public-image-url.png

# Plain URL in PR body — does NOT work
https://your-public-image-url.png
```

### Bulk-update PR descriptions (via API)

```bash
gh api "repos/<your-org>/<repo>/pulls/<pr-number>" \
  -X PATCH \
  -f body="Your description text

![screenshot](https://your-public-image-url.png)"
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `403 — Resource not accessible by integration` | Missing repository permission on the App | Add the permission, accept the prompt to update existing installs |
| `Not Found while determining the default branch` | App not installed on the target repo, OR token wasn't scoped to it | Install the app on the target repo, or pass `owner:` + `repositories:` |
| `Bad credentials` | Wrong App ID or malformed PEM in the secret | Re-paste the entire `.pem` (BEGIN/END lines included) into the secret |
| `secrets: inherit` doesn't pass the secrets | Reusable workflow lives in a different org | `secrets: inherit` only passes secrets within the same org — you must list them explicitly across orgs |
| Token works locally with `gh auth login` but fails in Actions | You're using your **user** token locally, not the **app** | Mint via `actions/create-github-app-token` in CI; never mix personal and app auth |
| Job that worked yesterday now fails after rotating the key | New `.pem` not pasted into the secret yet | Update `CICD_APP_PRIVATE_KEY` immediately after generating a new key, then delete the old key in the app |

---

## Reference

- [GitHub Apps documentation](https://docs.github.com/en/apps/creating-github-apps)
- [`actions/create-github-app-token`](https://github.com/actions/create-github-app-token)
- [Reusable workflows + `secrets: inherit`](https://docs.github.com/en/actions/using-workflows/reusing-workflows#using-secrets-in-reusable-workflows)
- [GitHub Apps — installation tokens](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation)
