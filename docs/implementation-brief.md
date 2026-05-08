# Implementation Brief

This repo ships one thin vertical slice. The goal is clarity, not feature breadth.

## Service split

- `apps/web` owns the UI and calls `POST /api/exhibit`
- `apps/api` owns the LLM flow and response assembly
- `apps/mcp-smithsonian` owns Smithsonian requests, normalization, and media filtering

## Current request flow

1. Frontend posts `topic`, `timePeriod`, and `artifactCount` to `/api/exhibit`.
2. API runs a two-step backend flow:
   - call the MCP `search_items` tool once
   - generate title, intro, captions, and limitations from the returned artifacts
3. MCP returns only normalized artifacts with usable images.
4. API builds a timeline from artifact dates and returns the exhibit payload.

## Deliberate constraints

- Smithsonian key stays in the MCP service only.
- Frontend never calls Smithsonian or runs agent logic.
- Artifact count is capped at 10.
- Empty dates and descriptions are expected and surfaced as limitations.

## What is intentionally missing

- Auth
- Persistence
- Payments
- Export and sharing
- Production hardening beyond a prototype
