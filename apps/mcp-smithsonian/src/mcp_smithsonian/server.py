from __future__ import annotations

import json
import os

from mcp.server.fastmcp import FastMCP

from mcp_smithsonian.client import get_item_raw, search_artifacts_raw
from mcp_smithsonian.normalizer import extract_media, normalize_row

_host = os.environ.get("MCP_HOST", "127.0.0.1")
_port = int(os.environ.get("MCP_PORT", "9000"))

mcp = FastMCP("mcp-smithsonian", host=_host, port=_port)


@mcp.tool()
async def search_items(
    query: str,
    limit: int = 5,
    period: str | None = None,
) -> str:
    """Search Smithsonian Open Access for artifacts matching a topic or keyword.

    Use this tool to find historical objects, artworks, and specimens from
    the Smithsonian collection. Only returns items that have confirmed image URLs.
    Returns a JSON array of normalized artifact objects.

    Args:
        query: Search terms (required, non-empty).
        limit: Max artifacts to return, 1 to 50. Default 5.
        period: Optional date filter appended as date:"<period>", e.g. "1960s".
    """
    if not query or not query.strip():
        raise ValueError("query must be a non-empty string")
    if not (1 <= limit <= 50):
        raise ValueError("limit must be between 1 and 50")

    rows = await search_artifacts_raw(query=query, limit=limit, period=period)
    artifacts = []
    for row in rows:
        if len(artifacts) >= limit:
            break
        artifact = normalize_row(row)
        if artifact is not None:
            artifacts.append(artifact.model_dump())
    return json.dumps(artifacts)


@mcp.tool()
async def get_item_details(item_id: str) -> str:
    """Fetch full details for a specific Smithsonian item by its canonical ID.

    Use this to re-fetch or enrich an item found via search_items.
    Accepts IDs in the format returned by search_items, e.g. "edanmdm:nasm_A19940223000".
    Returns a JSON object with all normalized artifact fields, or an error object
    if the item has no usable image.

    Args:
        item_id: Smithsonian canonical ID (required, non-empty).
    """
    if not item_id or not item_id.strip():
        raise ValueError("item_id must be a non-empty string")

    row = await get_item_raw(item_id)
    artifact = normalize_row(row)
    if artifact is None:
        return json.dumps({"error": "item has no usable image", "item_id": item_id})
    return json.dumps(artifact.model_dump())


@mcp.tool()
async def get_item_media(item_id: str) -> str:
    """Extract image URLs and citation metadata for a specific Smithsonian item.

    Returns image_url, thumbnail_url, source_url, rights, creator, and alt text.
    Use when you only need media and citation fields, not the full artifact record.
    Image fields will be empty strings if the item has no usable media.

    Args:
        item_id: Smithsonian canonical ID (required, non-empty).
    """
    if not item_id or not item_id.strip():
        raise ValueError("item_id must be a non-empty string")

    row = await get_item_raw(item_id)
    media = extract_media(item_id, row)
    return json.dumps(media.model_dump())


if __name__ == "__main__":
    mcp.run(transport="sse")
