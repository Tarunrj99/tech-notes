# Google Docs HTML Formatting

> [⬅ Back to ai-prompts/](../README.md) · [⬅ Repo root](../../README.md) · [Workflow rules (AGENTS.md)](../../AGENTS.md)

A reusable AI prompt that converts any HTML file into a layout that pastes cleanly into a Google Doc — preserving headings, tables, code blocks, callouts, and styling.

The same prompt works in any AI coding assistant — Cursor, Claude Code, ChatGPT, Gemini, Copilot Chat, etc. The only thing that changes is the wrapper format the tool expects.

## Files in this folder

| File | Use it for |
|---|---|
| [`prompt.md`](prompt.md) | The universal instruction text. Source of truth. Paste anywhere. |
| [`wrappers/cursor.mdc`](wrappers/cursor.mdc) | Cursor IDE rule (frontmatter + same content). Drop into `~/.cursor/rules/`. |
| [`wrappers/claude-skill.md`](wrappers/claude-skill.md) | Claude Code skill (frontmatter + same content). Drop into `~/.claude/skills/<name>/SKILL.md` or `<project>/.claude/skills/<name>/SKILL.md`. |

## How to use it in each AI tool

### Cursor IDE

```bash
mkdir -p ~/.cursor/rules
cp wrappers/cursor.mdc ~/.cursor/rules/google-docs-html-formatting.mdc
# Reload Cursor: Cmd+Shift+P → Reload Window
```

Then open any `.html` file in Cursor and say:

> apply doc formatting

### Claude Code

```bash
mkdir -p ~/.claude/skills/google-docs-html-formatting
cp wrappers/claude-skill.md ~/.claude/skills/google-docs-html-formatting/SKILL.md
```

Then in any project, run `claude` and say:

> apply doc formatting to <file>.html

### ChatGPT (Custom GPT or Project Instructions)

1. Open the [`prompt.md`](prompt.md) file
2. Copy the entire contents
3. Paste into the **Instructions** field of your Custom GPT or **Project instructions**

### Gemini / Copilot Chat / any other AI

1. Open [`prompt.md`](prompt.md)
2. Copy + paste at the start of your conversation, prefixed with:
   `You will follow these formatting rules whenever I ask you to "apply doc formatting":`

### Plain prompt (one-off)

Just paste the contents of [`prompt.md`](prompt.md) before your request.

## When to use this

You want to:

- Write technical documentation in HTML, then paste it into Google Docs without losing tables, code blocks, or styling
- Maintain a single source HTML file and produce a Google-Docs-ready output on demand
- Avoid the headache of Google Docs eating your CSS, breaking your tables, or stripping colors from code blocks

## Trigger phrase

By convention across all wrappers: **"apply doc formatting"**.

You can change the trigger by editing the prompt — search for "apply doc formatting" in `prompt.md` and replace.

## Updating

Edit only [`prompt.md`](prompt.md). Then sync the wrappers:

```bash
# from the repo root:
# (manual copy — the wrappers add their own frontmatter, so they're not auto-derived)
# Open both wrapper files and update the body to match prompt.md
```

(Future improvement: a small build script that injects `prompt.md` content into each wrapper's body.)

## Related

- [Cursor Rules — Setup & Reference Guide](../../tools/cursor/rules-setup-guide.md) — full guide on Cursor Rules, including how the Cursor wrapper works
- [Other Cursor-specific rules](../../tools/cursor/README.md) — rules that only apply inside Cursor
