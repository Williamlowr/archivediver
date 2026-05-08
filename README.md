# ArchiveDiver

ArchiveDiver is a small prototype that turns a topic into a short digital exhibit using Smithsonian Open Access data.

## What lives here

- `apps/web`: React + Vite frontend
- `apps/api`: FastAPI backend that generates exhibit content
- `apps/mcp-smithsonian`: MCP service that searches and normalizes Smithsonian data
- `docs`: brief, contracts, deployment notes, handoff notes, prompt log

## Hard boundaries

- Frontend talks to backend over HTTP only.
- Frontend does not call Smithsonian directly.
- Smithsonian API key stays server-side in `apps/mcp-smithsonian`.
- No auth, no persistence, no payments.

## Local setup

1. Copy the env template: `cp .env.example .env`
2. Fill in `ANTHROPIC_API_KEY` and `SMITHSONIAN_API_KEY`
3. Create a venv: `python3 -m venv .venv`
4. Activate it: `source .venv/bin/activate`
5. Install Python deps: `python -m pip install -e "apps/mcp-smithsonian[dev]" -e "apps/api[dev]"`
6. Install web deps: `npm install --prefix apps/web`
7. Start the app: `make dev`

Open `http://127.0.0.1:5173`.

## Common commands

- Run these from the activated venv.
- `make dev`: run web, API, and MCP together
- `make test`: run web, API, and MCP tests
- `make lint`: run ESLint and Ruff
- `make build`: build the frontend

## Key docs

- `docs/project-brief.md`
- `docs/api-contract.md`
- `docs/frontend-contract.md`
- `docs/deployment.md`
- `docs/handoff.md`
- `docs/prompt-log.md`
