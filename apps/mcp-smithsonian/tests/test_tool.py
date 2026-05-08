import json
import pytest
from unittest.mock import AsyncMock, patch

from tests.fixtures import APOLLO_ROW_WITH_IMAGE, ITEM_DETAIL_ROW, ROW_NO_IMAGE
from mcp_smithsonian.server import get_item_details, get_item_media, search_items


@pytest.fixture
def one_image_row():
    return [APOLLO_ROW_WITH_IMAGE]


@pytest.fixture
def no_image_rows():
    return [ROW_NO_IMAGE]


# search_items

async def test_search_items_returns_normalized_json(one_image_row):
    with patch(
        "mcp_smithsonian.server.search_artifacts_raw",
        new=AsyncMock(return_value=one_image_row),
    ):
        result = await search_items(query="apollo", limit=1)

    artifacts = json.loads(result)
    assert isinstance(artifacts, list)
    assert len(artifacts) == 1
    a = artifacts[0]
    assert a["id"] == "edanmdm:chndm_1901-39-3309"
    assert a["title"] == "Thirteen Apollo Subjects for Ceiling"
    assert a["image_url"] != ""
    assert a["source_url"] != ""


async def test_search_items_drops_items_without_image(no_image_rows):
    with patch(
        "mcp_smithsonian.server.search_artifacts_raw",
        new=AsyncMock(return_value=no_image_rows),
    ):
        result = await search_items(query="library items", limit=1)

    assert json.loads(result) == []


async def test_search_items_empty_response():
    with patch(
        "mcp_smithsonian.server.search_artifacts_raw",
        new=AsyncMock(return_value=[]),
    ):
        result = await search_items(query="nothing", limit=5)

    assert json.loads(result) == []


async def test_search_items_passes_period():
    captured = {}

    async def mock_search(query, limit, period):
        captured["query"] = query
        captured["period"] = period
        return []

    with patch("mcp_smithsonian.server.search_artifacts_raw", new=mock_search):
        await search_items(query="space", limit=3, period="1960s")

    assert captured["period"] == "1960s"
    assert captured["query"] == "space"


async def test_search_items_validates_empty_query():
    with pytest.raises(ValueError, match="non-empty"):
        await search_items(query="", limit=5)


async def test_search_items_validates_whitespace_query():
    with pytest.raises(ValueError, match="non-empty"):
        await search_items(query="   ", limit=5)


async def test_search_items_validates_limit_too_low():
    with pytest.raises(ValueError, match="limit"):
        await search_items(query="apollo", limit=0)


async def test_search_items_validates_limit_too_high():
    with pytest.raises(ValueError, match="limit"):
        await search_items(query="apollo", limit=51)


# get_item_details

async def test_get_item_details_returns_normalized_json():
    with patch(
        "mcp_smithsonian.server.get_item_raw",
        new=AsyncMock(return_value=ITEM_DETAIL_ROW),
    ):
        result = await get_item_details(item_id="edanmdm:chndm_1901-39-3309")

    data = json.loads(result)
    assert "error" not in data
    assert data["id"] == "edanmdm:chndm_1901-39-3309"
    assert data["title"] == "Thirteen Apollo Subjects for Ceiling"
    assert data["image_url"] != ""
    assert data["source_url"] != ""
    assert data["creator_display"] == "Felice Giani, Italian, 1758-1823"


async def test_get_item_details_imageless_returns_error_json():
    with patch(
        "mcp_smithsonian.server.get_item_raw",
        new=AsyncMock(return_value=ROW_NO_IMAGE),
    ):
        result = await get_item_details(item_id="edanmdm:sil_123")

    data = json.loads(result)
    assert data["error"] == "item has no usable image"
    assert data["item_id"] == "edanmdm:sil_123"


async def test_get_item_details_validates_empty_id():
    with pytest.raises(ValueError, match="non-empty"):
        await get_item_details(item_id="")


async def test_get_item_details_validates_whitespace_id():
    with pytest.raises(ValueError, match="non-empty"):
        await get_item_details(item_id="  ")


# get_item_media

async def test_get_item_media_returns_media_fields():
    with patch(
        "mcp_smithsonian.server.get_item_raw",
        new=AsyncMock(return_value=ITEM_DETAIL_ROW),
    ):
        result = await get_item_media(item_id="edanmdm:chndm_1901-39-3309")

    data = json.loads(result)
    assert data["item_id"] == "edanmdm:chndm_1901-39-3309"
    assert data["title"] == "Thirteen Apollo Subjects for Ceiling"
    assert data["image_url"] != ""
    assert data["thumbnail_url"] != ""
    assert data["source_url"] != ""
    assert data["rights"] == "CC0"
    assert data["creator_display"] == "Felice Giani, Italian, 1758-1823"
    assert "description" not in data
    assert "date_display" not in data


async def test_get_item_media_imageless_returns_empty_fields():
    with patch(
        "mcp_smithsonian.server.get_item_raw",
        new=AsyncMock(return_value=ROW_NO_IMAGE),
    ):
        result = await get_item_media(item_id="edanmdm:sil_123")

    data = json.loads(result)
    assert data["item_id"] == "edanmdm:sil_123"
    assert data["image_url"] == ""
    assert data["thumbnail_url"] == ""
    assert "error" not in data


async def test_get_item_media_validates_empty_id():
    with pytest.raises(ValueError, match="non-empty"):
        await get_item_media(item_id="")
