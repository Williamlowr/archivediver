# ArchiveDiver

ArchiveDiver is a prototype that generates a small digital exhibit from a user topic using Smithsonian Open Access data through an MCP boundary.

## Repo Layout

- `apps/web`: React + Vite + TypeScript frontend
- `apps/api`: FastAPI backend with LangChain orchestration
- `apps/mcp-smithsonian`: MCP server that wraps Smithsonian Open Access
- `docs`: briefs, handoff notes, deployment notes, prompt log

## Architecture Boundaries

- Frontend calls backend over HTTP only.
- Backend treats MCP as the source of artifact data.
- Smithsonian API key is server-side only and scoped to `apps/mcp-smithsonian`.
- No auth, no persistence, no payments for MVP.

## Prerequisites

- Docker (for the containerized path)
- Node.js 20+, Python 3.11+ (for local dev only)
- **Smithsonian Open Access API key (retrieve at https://api.data.gov/signup/ using email)**
- Anthropic API key or OpenAI API key

## Quickstart

### Get a Smithsonian Open Access API key here: https://api.data.gov/signup/

Follow one of three startup options based on your starting configurations

### For local dev with Docker:
Run commands:
```bash
cp .env.example .env
# fill in ANTHROPIC_API_KEY (or OPENAI_API_KEY) and SMITHSONIAN_API_KEY (from https://api.data.gov/signup/)
docker compose up --build
```

Open `http://127.0.0.1:8080`.

### For Mac dev, no Docker:
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

# Run each service in a new terminal: 
# Web
cd apps/web 
npm run dev

# API
cd apps/api
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# MCP
cd apps/mcp-smithsonian
python -m mcp_smithsonian.server
```

## Commands

- `make docker`: build and run the full stack with Docker Compose
- `make install`: install all dependencies (web + Python packages)
- `make dev`: start web, api, and mcp concurrently (local dev)
- `make test`: run all test suites
- `make lint`: run all linters
- `make format`: run formatters (Prettier + Ruff)

## Service README Files

- `apps/web/README.md`
- `apps/api/README.md`
- `apps/mcp-smithsonian/README.md`

## Notes

- `.env` stays local and untracked.
- `.env.example` is tracked and contains variable names only.
