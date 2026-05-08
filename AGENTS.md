# ArchiveDiver Agent Rules

This file is the source of truth for how AI assistants should work in this repository.

## Style rules
- No emojis.
- No em dashes.
- Keep responses and documentation concise and practical for humans.
- Avoid corporate filler language.

## Prompt logging
After you send a prompt, append an entry to `/docs/prompt-log.md`.

- Log only metadata: timestamp, tool, short task summary.
- Do not copy the user prompt into `/docs/prompt-log.md`. The user will paste it themselves.
- Timestamp command (source of truth):

```bash
date +"%I:%M %p %d/%m/%Y"
```

- Entry format:

```text
Time: HH:MM AM/PM DD/MM/YYYY
Tool: Cursor | Claude Code | Codex
Task: Short summary
```

## Project scope rules
- No auth.
- No persistence.
- No payments.
- Keep the Smithsonian API key secure and server-side only.
- Do not add agent logic to the frontend.
- Do not expose API keys in the frontend.
- Frontend should not call Smithsonian directly.

## Work rules
- Plan before implementing.
- Preserve file structure unless asked to change it.
- After changes, provide a summary of what changed.
- Use test suites to verify as we go.

