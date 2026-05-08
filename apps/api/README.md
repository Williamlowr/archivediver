# API Service

FastAPI service that coordinates exhibit generation and MCP tool calls.

## Purpose

- Accept `POST /api/exhibit` requests.
- Use LangChain tool-calling with MCP-backed Smithsonian data.
- Return exhibit JSON and dev trace details.

## Local Run

- `python -m pip install -e .`
- `uvicorn archivediver_api.main:app --reload --port 8000`

## Environment

- `ANTHROPIC_API_KEY`
- `MCP_SERVER_URL` (if using HTTP transport)

## Test

- `pytest`
