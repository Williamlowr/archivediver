from __future__ import annotations

import json
import os

from mcp.server.fastmcp import FastMCP

from mcp_smithsonian.client import search_artifacts_raw
from mcp_smithsonian.normalizer import normalize_row

_host = os.environ.get("MCP_HOST", "127.0.0.1")
_port = int(os.environ.get("MCP_PORT", "9000"))

mcp = FastMCP("mcp-smithsonian", host=_host, port=_port)


@mcp.tool()
async def search_artifacts(
    query: str,
    limit: int = 5,
    period: str | None = None,
) -> str:
    """Search Smithsonian Open Access for artifacts matching query.

    Returns JSON array of normalized artifact objects. Only items with a
    confirmed image URL are included.
    """
    rows = await search_artifacts_raw(query=query, limit=limit, period=period)
    artifacts = []
    for row in rows:
        if len(artifacts) >= limit:
            break
        artifact = normalize_row(row)
        if artifact is not None:
            artifacts.append(artifact.model_dump())
    return json.dumps(artifacts)


if __name__ == "__main__":
    mcp.run(transport="sse")
