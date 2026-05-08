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

- Node.js 20+
- npm 10+
- Python 3.11+
- Smithsonian Open Access API key
- Anthropic API key

## Quickstart

1. Copy env template:
   - `cp .env.example .env`
2. Fill in required keys in `.env`.
3. Install dependencies:
   - `npm install` (root scripts only)
   - `npm install --prefix apps/web`
   - `python -m pip install -e apps/api`
   - `python -m pip install -e apps/mcp-smithsonian`
4. Start all services:
   - `make dev` or `npm run dev`

## Commands

- `make dev` / `npm run dev`: start web, api, and mcp placeholder processes
- `make test` / `npm run test`: run test suites across services
- `make lint` / `npm run lint`: run lint checks
- `make format` / `npm run format`: run formatting hooks

## Service README Files

- `apps/web/README.md`
- `apps/api/README.md`
- `apps/mcp-smithsonian/README.md`

## Notes

- `.env` stays local and untracked.
- `.env.example` is tracked and contains variable names only.
