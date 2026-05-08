"""Live Smithsonian API test. Requires network access.

Uses SMITHSONIAN_API_KEY env var, falls back to DEMO_KEY.
DEMO_KEY may be rate-limited; stop and investigate if 429 is returned.
"""
import pytest
from mcp_smithsonian.client import search_artifacts_raw
from mcp_smithsonian.normalizer import normalize_row


async def test_live_search_returns_artifacts():
    rows = await search_artifacts_raw(query="apollo", limit=3)
    assert len(rows) > 0, "Expected at least one search row from Smithsonian"

    for row in rows:
        assert "id" in row or "url" in row, f"Row missing id/url: {list(row.keys())}"
        assert "content" in row, "Row missing content block"


async def test_live_normalization_produces_valid_artifacts():
    rows = await search_artifacts_raw(query="apollo", limit=5)
    assert len(rows) > 0

    valid = [normalize_row(row) for row in rows]
    valid = [a for a in valid if a is not None]

    assert len(valid) > 0, (
        "No artifacts survived normalization. "
        "All rows may lack usable images -- check raw rows above."
    )

    first = valid[0]
    assert first.id, "id must be non-empty"
    assert first.title, "title must be non-empty"
    assert first.source_url, "source_url must be non-empty"
    assert first.image_url, "image_url must be non-empty (items without images are dropped)"
