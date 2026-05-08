# Project Brief

ArchiveDiver is a prototype that turns a user topic into a small digital exhibit using Smithsonian Open Access data.

## Goal

Build a simple end-to-end demo with a clean boundary between:

- `apps/web` for UI
- `apps/api` for exhibit generation
- `apps/mcp-smithsonian` for Smithsonian access and normalization

## User flow

1. User enters a topic, optional time period, and artifact count up to 10.
2. Backend asks the MCP service for Smithsonian artifacts.
3. Backend returns an exhibit with a title, intro, artifact cards, timeline data, and dev details.
4. Frontend renders the result.

## Expected output

- Exhibit title
- Short intro
- Artifact cards with image and source metadata
- Timeline when dates are available
- Dev panel with tool trace and result limitations

## Scope rules

- Keep the Smithsonian key server-side only.
- Frontend must not call Smithsonian directly.
- Do not put agent logic in the frontend.
- No auth, no persistence, no payments.
