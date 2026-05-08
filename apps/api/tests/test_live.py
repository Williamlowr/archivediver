"""Live end-to-end test. Requires both MCP server and API server running.

Start servers before running:
  cd apps/mcp-smithsonian && python -m mcp_smithsonian.server
  cd apps/api && uvicorn archivediver_api.main:app --port 8000

Run with:
  LIVE_TESTS=1 python -m pytest tests/test_live.py -v -s
"""
import os

import httpx
import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("LIVE_TESTS"),
    reason="Set LIVE_TESTS=1 to run live backend tests",
)

API_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


async def test_live_post_exhibit():
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{API_URL}/api/exhibit",
            json={"topic": "apollo program", "artifactCount": 3},
        )

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()

    assert data["title"], "title must be non-empty"
    assert data["intro"], "intro must be non-empty"
    assert len(data["artifacts"]) > 0, "Expected at least one artifact"
    assert len(data["dev"]["tool_calls"]) > 0, "Expected at least one tool call in dev trace"

    artifact = data["artifacts"][0]
    assert artifact["id"], "artifact.id must be non-empty"
    assert artifact["title"], "artifact.title must be non-empty"
    assert artifact["source_url"], "artifact.source_url must be non-empty"
    assert artifact["image_url"], "artifact.image_url must be non-empty"
    assert "caption" in artifact, "artifact must have a caption field"
    assert "image_download_url" not in artifact, "image_download_url must not leak to frontend"

    tc = data["dev"]["tool_calls"][0]
    assert tc["tool"] == "search_items"
    assert tc["output_count"] > 0

    assert "limitations" in data["dev"], "dev must have a limitations field"
