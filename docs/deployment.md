# Deployment

ArchiveDiver supports three startup paths:

- containerized startup with `docker compose up --build`
- local dev with `make install && make dev`
- Windows PowerShell Dev

For anything beyond local review, treat the app as three pieces:

- static frontend
- FastAPI backend
- private MCP Smithsonian service

Get a Smithsonian Open Access API key here: https://api.data.gov/signup/

Follow one of three startup options based on your starting configurations

For local dev with Docker:
Run commands:
```bash
cp .env.example .env
# fill in ANTHROPIC_API_KEY (or OPENAI_API_KEY) and SMITHSONIAN_API_KEY (from https://api.data.gov/signup/)
docker compose up --build
```

Open `http://127.0.0.1:8080`.

For Mac dev, no Docker:
install Make dev tools if needed: 
```bash
xcode-select --install
```
With Make installed,
Run commands: 
```bash
cp .env.example .env
# stop and fill in ANTHROPIC_API_KEY (or OPENAI_API_KEY) and SMITHSONIAN_API_KEY (from https://api.data.gov/signup/)
python3 -m venv .venv && source .venv/bin/activate
make install
make dev
```

Open `http://127.0.0.1:5173`.

### Windows PowerShell local dev without Docker or Make
```powershell
Copy-Item .env.example .env
# fill in ANTHROPIC_API_KEY or OPENAI_API_KEY and SMITHSONIAN_API_KEY

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

pip install -e "apps/api[dev]"
pip install -e "apps/mcp-smithsonian[dev]"
npm install --prefix apps/web
```

Compose behavior:

- `web` is the only published service (port 8080)
- `web` proxies `/api/*` to `api`
- `api` talks to `mcp` over the internal Compose network
- `mcp` is not exposed publicly

## Required env vars

### API

- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` (at least one required; Anthropic wins when both are set)
- `MCP_URL`

### MCP

- `SMITHSONIAN_API_KEY`
- `MCP_HOST`
- `MCP_PORT`

### Frontend

- `VITE_API_BASE_URL`: set this for local or split-origin deployments
- `VITE_USE_MOCK`: optional offline UI mode

## Request routing

There are two request paths depending on how you start the app:

- Local `make dev` path: the frontend uses `VITE_API_BASE_URL` from the repo-root `.env`, so requests go to `http://localhost:8000/api/exhibit` unless you change that value.
- Docker path: the production build does not bake in `VITE_API_BASE_URL`, so the frontend falls back to relative `/api/exhibit`, and nginx forwards `/api/*` to the API container.

## Recommended topology

`browser -> web -> api -> mcp-smithsonian -> Smithsonian Open Access`

Keep the MCP service private. Only the API should talk to it.

## Smoke check

1. Open the app.
2. Submit a topic.
3. Confirm the API returns `200`.
4. Confirm the dev panel shows `search_items`.
5. Confirm no Smithsonian key appears in frontend env or network payloads.

## Reality check

- Docker Compose is available for local containerized startup (`make docker`).
- The supported local dev flow is `make install && make dev`.
- This is a prototype, not a hardened production deployment.
