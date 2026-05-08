# MCP Smithsonian Service

Python MCP service that wraps Smithsonian Open Access.

## Owns

- Smithsonian API requests
- artifact normalization
- filtering out items without usable images

## Tools

- `search_items`
- `get_item_details`
- `get_item_media`

## Run

- `.venv/bin/pip install -e "apps/mcp-smithsonian[dev]"`
- `SMITHSONIAN_API_KEY=... MCP_HOST=127.0.0.1 MCP_PORT=9000 .venv/bin/python -m mcp_smithsonian.server`

## Env

- `SMITHSONIAN_API_KEY`
- `MCP_HOST`, default `127.0.0.1`
- `MCP_PORT`, default `9000`

## Test

- `.venv/bin/python -m pytest apps/mcp-smithsonian`
