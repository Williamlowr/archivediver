# Deployment

ArchiveDiver is easiest to deploy as three pieces:

- static frontend
- FastAPI backend
- private MCP Smithsonian service

## Recommended topology

`browser -> web -> api -> mcp-smithsonian -> Smithsonian Open Access`

Keep the MCP service private. Only the API should talk to it.

## Required env vars

### Frontend

- `VITE_API_BASE_URL` if the API is on a different origin

### API

- `ANTHROPIC_API_KEY`
- `MCP_URL`

### MCP

- `SMITHSONIAN_API_KEY`
- `MCP_HOST`
- `MCP_PORT`

## Build and start

### Web

```bash
npm install --prefix apps/web
npm run build --prefix apps/web
```

Serve `apps/web/dist` from your static host.

### API

```bash
python3 -m venv .venv
.venv/bin/pip install -e "apps/api[dev]"
ANTHROPIC_API_KEY=... MCP_URL=http://mcp-smithsonian:9000/sse .venv/bin/python -m uvicorn archivediver_api.main:app --host 0.0.0.0 --port 8000
```

### MCP Smithsonian

```bash
python3 -m venv .venv
.venv/bin/pip install -e "apps/mcp-smithsonian[dev]"
SMITHSONIAN_API_KEY=... MCP_HOST=0.0.0.0 MCP_PORT=9000 .venv/bin/python -m mcp_smithsonian.server
```

## Reverse proxy notes

- Route frontend traffic normally.
- Route `/api/*` to the FastAPI service.
- Do not expose the MCP service publicly.

## Smoke check

1. Open the app.
2. Submit a topic.
3. Confirm the API returns `200`.
4. Confirm the dev panel shows `search_items`.
5. Confirm no Smithsonian key appears in frontend env or network payloads.

## Reality check

- There is no Docker or infra config in this repo yet.
- This is a prototype, not a hardened production deployment.
