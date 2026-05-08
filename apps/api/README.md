# API Service

FastAPI backend for ArchiveDiver.

## Owns

- `POST /api/exhibit`
- MCP tool calls
- exhibit title, intro, caption, and limitation generation

## Run

- `.venv/bin/pip install -e "apps/api[dev]"`
- `ANTHROPIC_API_KEY=... MCP_URL=http://127.0.0.1:9000/sse .venv/bin/python -m uvicorn archivediver_api.main:app --reload --host 127.0.0.1 --port 8000`

## Env

- `ANTHROPIC_API_KEY`
- `MCP_URL`, default `http://localhost:9000/sse`

## Test

- `.venv/bin/python -m pytest apps/api`
