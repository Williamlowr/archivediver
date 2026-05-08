# Developer Handoff

## Current state

ArchiveDiver is a working prototype with three services:

- `apps/web`: React frontend
- `apps/api`: FastAPI + LangChain backend
- `apps/mcp-smithsonian`: Smithsonian MCP service

The app takes a topic, fetches Smithsonian artifacts through MCP, and returns a short exhibit with dev trace details.

## Start here

- Read `README.md` for local setup.
- Read `docs/api-contract.md` for backend shape.
- Read `docs/frontend-contract.md` for UI expectations.
- Read `docs/deployment.md` if you need to ship it somewhere.

## Important rules

- Keep the Smithsonian key in `apps/mcp-smithsonian` only.
- Do not add agent logic to the frontend.
- Frontend should not call Smithsonian directly.
- No auth, persistence, or payments unless scope changes.

## Useful commands

- Run these from the activated `.venv`.
- `make dev`
- `make test`
- `make lint`
- `make build`

## Known rough edges

- Smithsonian image availability is inconsistent across units.
- Some records have weak dates or descriptions.
- `DEMO_KEY` is rate-limited, so real testing is better with a real API key.

## If you pick this up next

- Keep docs in sync with code when request shapes or env vars change.
- Add a prompt-log entry for major AI-assisted work.
- If deployment matters, add real process management, health checks, and secret handling instead of relying on manual commands.
