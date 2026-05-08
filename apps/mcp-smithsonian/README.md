# MCP Smithsonian Service

Python MCP server that wraps Smithsonian Open Access search and normalization.

## Purpose

- Expose Smithsonian artifact search as MCP tools.
- Normalize Smithsonian response fields for backend use.
- Keep Smithsonian API key server-side only.

## Local Run

- `python -m pip install -e .`
- `python -m mcp_smithsonian`

## Environment

- `SMITHSONIAN_API_KEY`

## Test

- `pytest`
