# **Cursor Rules — Setup & Reference Guide**

**Table of Contents**

1. What are Cursor Rules?  
2. Rule File Structure  
3. Global Rules (all projects)  
4. Project Rules (single project)  
5. Commands & File Names Reference  
6. Our Existing Rule — Google Docs HTML Formatting  
7. Additional Recommended Rules  
8. Tips & Best Practices

---

## **1\. What are Cursor Rules?**

Cursor Rules are persistent instructions stored in .mdc files that Cursor AI reads automatically every time you work on a file. Instead of repeating the same instructions in every chat, you write them once in a rule file — and Cursor follows them forever.

| Without Rules | With Rules |
| :---- | :---- |
| Paste long formatting prompt every time you open a new HTML file | Just say "apply doc formatting" — Cursor knows exactly what to do |
| Re-explain coding standards for every new file or project | Standards are enforced automatically on every session |
| Instructions reset when you start a new chat | Rules persist across all chats, windows, and projects |

---

## **2\. Rule File Structure**

Every rule is a .mdc file with a YAML header (frontmatter) followed by the instruction content in Markdown.

```
---
description: Brief description shown in Cursor rule picker
globs: **/*.html         # which files trigger this rule (optional)
alwaysApply: false       # true = applies to every session automatically
---

# Rule Title

Your instructions here in plain Markdown.
Include examples, commands, code snippets — anything Cursor should know.
```

### **Frontmatter Fields**

| Field | Type | Purpose | Example |
| :---- | :---- | :---- | :---- |
| description | string | What the rule does — shown in the rule picker UI | Apply Google Docs HTML formatting |
| globs | string | File pattern — rule loads when a matching file is open | \*\*/\*.html, \*\*/\*.ts, devops/\*\* |
| alwaysApply | boolean | If true, Cursor reads this rule in every session regardless of file | true or false |

**⚠️ Keep rules under 500 lines** Cursor reads the full rule file on every matching session. Long rules slow down context loading. Split large rules into focused smaller ones.

---

## **3\. Global Rules — Apply to ALL Projects**

Global rules live in your home directory at \~/.cursor/rules/. They are available in every Cursor window, every project, on this machine.

### **Step-by-Step: Create a Global Rule**

**Step 1 — Create the global rules directory (one time only)**

```
mkdir -p ~/.cursor/rules
```

**Step 2 — Create your rule file**

```
# Create a new rule file (use any name, must end in .mdc)
touch ~/.cursor/rules/your-rule-name.mdc

# Then open it in your editor and add frontmatter + content
open ~/.cursor/rules/your-rule-name.mdc
```

**Step 3 — Verify it exists**

```
ls -la ~/.cursor/rules/
```

**Step 4 — Restart Cursor** (or reload window with Cmd+Shift+P → Reload Window) so the new rule is picked up.

### **Global Rules Directory**

```
~/.cursor/
  rules/
    google-docs-html-formatting.mdc   ← our formatting rule
    your-other-rule.mdc
```

---

## **4\. Project Rules — Apply to ONE Project Only**

Project rules live inside the project folder at .cursor/rules/. They only apply when Cursor has that folder open. Useful for project-specific conventions.

### **Step-by-Step: Create a Project Rule**

**Step 1 — Create the project rules directory inside your project**

```
mkdir -p /path/to/your/project/.cursor/rules
```

**Step 2 — Create your rule file**

```
touch /path/to/your/project/.cursor/rules/your-rule-name.mdc
```

**Step 3 — Verify**

```
ls -la /path/to/your/project/.cursor/rules/
```

### **Project Rules Directory**

```
your-project/
  .cursor/
    rules/
      your-rule-name.mdc
  src/
  README.md
```

**ℹ️ Global vs Project — which wins?** Both apply at the same time. If a file matches both a global rule and a project rule, Cursor uses both. Project rules do not override global rules — they add to them.

---

## **5\. Commands & File Names Reference**

| Action | Command |
| :---- | :---- |
| Create global rules directory | mkdir \-p \~/.cursor/rules |
| Create project rules directory | mkdir \-p .cursor/rules |
| List global rules | ls \~/.cursor/rules/ |
| List project rules | ls .cursor/rules/ |
| Copy a rule from project to global | cp .cursor/rules/rule.mdc \~/.cursor/rules/rule.mdc |
| Copy a rule from global to project | cp \~/.cursor/rules/rule.mdc .cursor/rules/rule.mdc |
| Edit a global rule | open \~/.cursor/rules/rule-name.mdc |
| Delete a rule | rm \~/.cursor/rules/rule-name.mdc |
| Reload Cursor after adding rule | Cmd+Shift+P → Reload Window |

### **File Naming Convention**

| Rule Purpose | Suggested Filename |
| :---- | :---- |
| Google Docs HTML formatting | google-docs-html-formatting.mdc |
| Kubernetes / DevOps conventions | devops-kubernetes.mdc |
| Python coding standards | python-standards.mdc |
| Git commit message format | git-commit-format.mdc |
| Shell scripting standards | shell-scripting.mdc |
| Docker best practices | docker-best-practices.mdc |
| Security / secrets hygiene | security-hygiene.mdc |

---

## **6\. Our Existing Rule — Google Docs HTML Formatting**

**ℹ️ This rule is universal** — it works in Cursor, Claude Code, ChatGPT, and any other AI tool. The source of truth and all wrappers live in [`../../ai-prompts/google-docs-html-formatting/`](../../ai-prompts/google-docs-html-formatting/).

**✅ Already applied globally** This rule exists at \~/.cursor/rules/google-docs-html-formatting.mdc and is available in all Cursor windows.

### **How to trigger it**

Open any .html file and say:

```
apply doc formatting
```

### **File: \~/.cursor/rules/google-docs-html-formatting.mdc**

Complete file content — copy this exactly to create or recreate the rule:

```
---
description: Apply Google Docs compatible HTML formatting. Trigger with "apply doc formatting" on any HTML file.
globs: **/*.html
alwaysApply: false
---

# Google Docs HTML Formatting

When the user says "apply doc formatting" on an HTML file, apply the full style
below and replace the existing <style> block.

FONT & PAGE:
- Font: Calibri, Arial, sans-serif — 11pt
- Page: max-width 6.5in, margin 1in auto, padding 0
  (Google Docs Letter 8.5" x 11" Portrait = 8.5in total minus 1in left margin
  minus 1in right margin = 6.5in content width)

HEADINGS:
- h1: 24pt, color #0066cc, border-bottom 2px solid #0066cc, padding-bottom 6pt
- h2: 18pt, color #0066cc
- h3: 14pt, color #333
- h4: 12pt, color #333

CODE BLOCKS:
- Use <pre><code>plain text</code></pre> structure — no color spans inside
- pre: background #f5f5f5, border 1px solid #ddd, border-radius 4px,
       padding 12pt, font "Courier New" 9pt, line-height 1.6
- pre code: no extra background, no padding, no border (inherit from pre)
- inline code: background #f5f5f5, padding 2px 4px, border-radius 3px,
               font "Courier New" 9pt

TABLES:
- border-collapse: collapse, width 100%, margin 12pt 0, table-layout: fixed
- th and td: border 1px solid #ddd, padding 6pt, vertical-align top
- th: background #0066cc, color white, font-size 10pt
- td: word-break: break-word, overflow-wrap: break-word, font-size 9.5pt
- even rows: background #f9f9f9
- Dense tables (4+ columns): class="dense-table" — font-size 9pt, padding 5pt

NOTE / CALLOUT BOXES:
- All box types (.box, .box-info, .callout):
    border 1px solid #ddd, background #fafafa, padding 10pt 12pt,
    border-radius 6px, margin 12pt 0
- Warning (.box-warning): border-color #e6c84a, background #fffef0
- Danger  (.box-danger):  border-color #e0a0a0, background #fff8f8
- Success (.box-success): border-color #90cca0, background #f6fff8

TAGS / CHIPS (.tag, .chip):
- background #eef6ff, color #004a99, border 1px solid #cfe6ff,
  border-radius 10px, font-size 9pt, padding 2px 6px

DIVIDERS:
- hr: border-top 1px solid #ddd, margin 18pt 0, no border on other sides

FOOTER (.footer):
- border-top 1px solid #ddd, font-size 9pt, color #888,
  text-align center, margin-top 36pt, padding-top 10pt

CRITICAL RULES FOR COPY-PASTE INTO GOOGLE DOCS:
1. All code blocks must use <pre><code>plain text</code></pre>
   Strip ALL <span> color tags inside <pre> blocks — keep text content only.
2. Tables must have explicit border on every th and td (not just border-bottom)
   so borders survive Google Docs paste.
3. No flexbox, no CSS grid, no box-shadow anywhere in content —
   these do not transfer on paste.
4. Meta/info rows must use <p> tags, not flex divs.
5. max-width must be 6.5in — never 8.5in.
   8.5in is the paper width; 6.5in is the usable content width.

After applying:
- Strip color <span> tags from all <pre> blocks (use a script if many blocks).
- Open in Chrome → Cmd+A → Cmd+C → paste into Google Docs.
```

---

## **7\. Additional Recommended Rules**

Below are ready-to-use rules you can create. Copy the content into a new .mdc file in \~/.cursor/rules/.

### **Rule 1 — Git Commit Message Format**

**File:** \~/.cursor/rules/git-commit-format.mdc

```
---
description: Enforce conventional git commit message format
globs: ""
alwaysApply: false
---

# Git Commit Message Format

Always write commit messages in this format:

  <type>(<scope>): <short summary>

Types: feat, fix, docs, chore, refactor, test, ci
- feat: new feature
- fix: bug fix
- docs: documentation only
- chore: maintenance, deps update
- refactor: code change with no feature or fix
- ci: CI/CD pipeline changes

Examples:
  feat(auth): add JWT refresh token support
  fix(api): handle null response from payment gateway
  chore(deps): update helm chart to 3.12.0
  docs(rbac): add user access setup guide

Rules:
- Subject line max 72 characters
- Use imperative mood: "add" not "added"
- No period at end of subject line
- Reference ticket number if applicable: feat(rbac): add &lt;username&gt; access [TICK-123]
```

---

### **Rule 2 — Kubernetes / DevOps YAML Standards**

**File:** \~/.cursor/rules/devops-kubernetes.mdc

```
---
description: Kubernetes YAML and DevOps conventions
globs: **/*.yaml, **/*.yml
alwaysApply: false
---

# Kubernetes & DevOps YAML Standards

## YAML Structure
- Always include apiVersion, kind, metadata, spec in that order
- Add labels: managed-by, environment, app to every resource metadata
- Add comments explaining non-obvious fields

## Naming Conventions
- Resource names: lowercase, hyphen-separated (e.g. my-app-deployment)
- Namespace names: environment-based (production, staging, development)
- ConfigMap / Secret names: <app>-<type> (e.g. payments-api-config)

## Security
- Never hardcode secrets in YAML — use Kubernetes Secrets or Vault references
- Always set resource requests and limits on containers
- Use non-root user in containers where possible

## Helm
- values.yaml: document every key with a comment
- Use .Release.Name prefix on resource names to avoid collisions
- Pin image tags — never use :latest in production
```

---

### **Rule 3 — Shell Script Standards**

**File:** \~/.cursor/rules/shell-scripting.mdc

```
---
description: Shell scripting best practices for bash scripts
globs: **/*.sh
alwaysApply: false
---

# Shell Script Standards

## Header (every script must have)
  #!/usr/bin/env bash
  set -euo pipefail   # exit on error, undefined vars, pipe failure

## Style
- 2-space indentation
- UPPER_CASE for constants and env vars
- lower_case for local variables and function names
- Quote all variable expansions: "$VAR" not $VAR

## Error Handling
- Always check exit codes for critical commands
- Print meaningful error messages to stderr: echo "ERROR: ..." >&2
- Use trap for cleanup: trap 'cleanup' EXIT

## Functions
- One function per logical task
- Add a brief comment above each function explaining its purpose

## Secrets
- Never hardcode passwords or tokens in scripts
- Read from environment variables or vault: VAL=$(vault kv get ...)
```

---

### **Rule 4 — Docker Best Practices**

**File:** \~/.cursor/rules/docker-best-practices.mdc

```
---
description: Dockerfile and Docker Compose best practices
globs: **/Dockerfile*, **/docker-compose*.yml
alwaysApply: false
---

# Docker Best Practices

## Dockerfile
- Use specific base image tags — never FROM node:latest
- Order layers: install deps before copying source code (cache efficiency)
- Use multi-stage builds for compiled languages to keep image small
- Run as non-root user: USER nonroot
- Use .dockerignore to exclude node_modules, .git, secrets
- Set WORKDIR explicitly: WORKDIR /app
- Combine RUN commands with && to reduce layers

## Docker Compose
- Always specify version at top
- Use named volumes, not bind mounts in production
- Set restart: unless-stopped for production services
- Use environment files (.env) for secrets, never hardcode in compose file
- Add healthcheck to critical services
```

---

### **Rule 5 — Security & Secrets Hygiene**

**File:** \~/.cursor/rules/security-hygiene.mdc

```
---
description: Security and secrets hygiene rules — apply to all files
globs: ""
alwaysApply: true
---

# Security & Secrets Hygiene

## Never do this (in any file type)
- Hardcode passwords, API keys, tokens, private keys in any file
- Commit .env files with real values
- Use root credentials for application service accounts
- Store secrets in ConfigMaps (use Kubernetes Secrets or Vault)

## Always do this
- Reference secrets from environment variables or secret managers
- Add .env to .gitignore
- Use least-privilege principle for all service accounts and RBAC roles
- Rotate secrets regularly — document rotation steps

## When writing RBAC / IAM
- Grant minimum permissions needed — no wildcards unless absolutely required
- Prefer namespace-scoped Roles over cluster-wide ClusterRoles
- Document what each permission allows and why it is needed
- Always separate role definition from role binding (two files)
```

---

### **Rule 6 — GCP / Cloud CLI Hygiene**

**File:** \~/.cursor/rules/gcp-cli-hygiene.mdc

```
---
description: GCP CLI and cloud resource hygiene rules
globs: **/*.sh, **/*.yaml
alwaysApply: false
---

# GCP & Cloud CLI Hygiene

## gcloud Commands
- Always specify --project flag explicitly — never rely on default project
- Always specify --region or --zone explicitly
- Use --format=json or --format=table for scripted output
- Prefer gcloud auth application-default login over service account keys

## Resource Creation
- Never create service accounts unless absolutely necessary
- Always clean up temporary resources after testing
- Tag/label all created resources with: managed-by, environment, owner
- Prefer IAM Conditions over broad role assignments

## Cleanup Checklist (after testing)
- Delete any test service accounts created
- Revoke application-default credentials: gcloud auth application-default revoke
- Disable any APIs that were enabled only for testing
- Remove temporary IAM bindings
```

---

## **8\. Tips & Best Practices**

| Tip | Detail |
| :---- | :---- |
| Keep rules focused | One rule per topic. A 30-line focused rule works better than one 300-line mega-rule. |
| Use globs wisely | Set globs: \*\*/\*.html so the rule only loads for relevant files — reduces noise. |
| alwaysApply sparingly | Only set alwaysApply: true for truly universal rules like security hygiene. Over-use slows Cursor. |
| Trigger words | Write a clear trigger phrase in the rule (e.g. "when user says apply doc formatting"). This makes it easy to invoke. |
| Version your rules | Keep rule files in your project's git repo (.cursor/rules/) so team members share the same standards. |
| Test after creating | Always do Cmd+Shift+P → Reload Window after adding a new rule, then test with a simple trigger phrase. |
| Global vs Project | Use global (\~/.cursor/rules/) for personal standards. Use project (.cursor/rules/) for team/project-specific rules. |
| Rule inheritance | Both global and project rules apply simultaneously — they add to each other, not override. |

---

