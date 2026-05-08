import json
import pytest
from unittest.mock import AsyncMock, patch

from tests.fixtures import APOLLO_ROW_WITH_IMAGE, ROW_NO_IMAGE
from mcp_smithsonian.server import search_artifacts


@pytest.fixture
def one_image_row():
    return [APOLLO_ROW_WITH_IMAGE]


@pytest.fixture
def no_image_rows():
    return [ROW_NO_IMAGE]


async def test_search_artifacts_returns_normalized_json(one_image_row):
    with patch(
        "mcp_smithsonian.server.search_artifacts_raw",
        new=AsyncMock(return_value=one_image_row),
    ):
        result = await search_artifacts(query="apollo", limit=1)

    artifacts = json.loads(result)
    assert isinstance(artifacts, list)
    assert len(artifacts) == 1
    a = artifacts[0]
    assert a["id"] == "edanmdm:chndm_1901-39-3309"
    assert a["title"] == "Thirteen Apollo Subjects for Ceiling"
    assert a["image_url"] != ""
    assert a["source_url"] != ""


async def test_search_artifacts_drops_items_without_image(no_image_rows):
    with patch(
        "mcp_smithsonian.server.search_artifacts_raw",
        new=AsyncMock(return_value=no_image_rows),
    ):
        result = await search_artifacts(query="library items", limit=1)

    artifacts = json.loads(result)
    assert artifacts == []


async def test_search_artifacts_empty_response():
    with patch(
        "mcp_smithsonian.server.search_artifacts_raw",
        new=AsyncMock(return_value=[]),
    ):
        result = await search_artifacts(query="nothing", limit=5)

    assert json.loads(result) == []


async def test_search_artifacts_passes_period():
    captured = {}

    async def mock_search(query, limit, period):
        captured["query"] = query
        captured["period"] = period
        return []

    with patch("mcp_smithsonian.server.search_artifacts_raw", new=mock_search):
        await search_artifacts(query="space", limit=3, period="1960s")

    assert captured["period"] == "1960s"
    assert captured["query"] == "space"
