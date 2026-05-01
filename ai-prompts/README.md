# AI Prompts

> [⬅ Back to repo root](../README.md) · [Workflow rules (AGENTS.md)](../AGENTS.md)

Reusable AI-assistant prompts (instructions, system prompts, "rules") that are **tool-agnostic** — they work in Cursor, Claude Code, ChatGPT, Gemini, GitHub Copilot Chat, and any other AI coding assistant.

Each prompt has:

- A universal `prompt.md` (the source of truth)
- A folder of `wrappers/` for the specific frontmatter formats different tools expect (Cursor `.mdc`, Claude `SKILL.md`, etc.)
- A `README.md` explaining what the prompt does and how to install it in each AI tool

## Why this folder exists

A prompt is just text. The same instruction works regardless of which AI tool you're using — only the wrapper format changes. Storing prompts here (instead of inside a tool-specific folder) means:

- **Single source of truth** — edit one file, it applies everywhere
- **Cross-tool reuse** — copy into Cursor, Claude Code, or ChatGPT
- **Discoverable** — anyone can find and reuse them

## Folder structure

```
ai-prompts/
└── <prompt-name>/
    ├── README.md           # what it does, when to use, install in each tool
    ├── prompt.md           # the universal instruction text
    └── wrappers/
        ├── cursor.mdc      # Cursor frontmatter wrapper
        ├── claude-skill.md # Claude Code SKILL.md wrapper
        └── ...             # add wrappers as new tools are supported
```

## Index

- [google-docs-html-formatting](google-docs-html-formatting/) — apply Google-Docs-compatible styling to any HTML file so it pastes cleanly into a Google Doc. Trigger: `apply doc formatting`.

*(More prompts will be added here as they are published.)*

## Adding a new prompt

1. Create `ai-prompts/<your-prompt-name>/`
2. Add `prompt.md` with the universal instruction text (no tool-specific frontmatter)
3. Add `wrappers/cursor.mdc` and any other wrappers your team needs
4. Add `README.md` describing what it does and install steps for each tool
5. Update this index
6. Update the main repo `README.md`

See [AGENTS.md](../AGENTS.md) at the repo root for the full workflow (folder map, naming rules, sanitization, secret-scan, commit format, pre-push checklist).

## Related

- [Cursor-specific rules](../tools/cursor/README.md) — rules that only apply to the Cursor IDE (not cross-tool)
- [Repo conventions and contribution guide](../CONTRIBUTING.md)
