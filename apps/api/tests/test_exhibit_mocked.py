"""API tests using mocked run_agent. No Anthropic or MCP calls made."""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from archivediver_api.main import app
from archivediver_api.models import ArtifactCaption, LLMExhibitOutput

FAKE_ARTIFACT = {
    "id": "edanmdm:nasm_test_1",
    "record_id": "nasm_test_1",
    "title": "Apollo Command Module",
    "date_display": "1967",
    "date_indexed": ["1960s"],
    "creator_display": "NASA",
    "description": "Command module used on Apollo missions.",
    "object_type": "Spacecraft",
    "unit_code": "NASM",
    "unit_name": "National Air and Space Museum",
    "source_url": "https://airandspace.si.edu/test",
    "image_url": "https://ids.si.edu/test_screen.jpg",
    "thumbnail_url": "https://ids.si.edu/test_thumb.jpg",
    "image_download_url": "https://ids.si.edu/test_hires.jpg",
    "image_alt": "Apollo Command Module",
    "rights": "CC0",
    "subject_tags": ["Space exploration"],
    "place_tags": ["USA"],
}

FAKE_TOOL_CALLS = [
    {
        "tool": "search_items",
        "input": {"query": "apollo program", "limit": 3},
        "output_count": 1,
    }
]
FAKE_NOTICES: list[str] = []

FAKE_LLM_OUTPUT = LLMExhibitOutput(
    title="Apollo: Engineering a Moon Landing",
    intro="Three artifacts trace the technology and ambition behind the Apollo program.",
    captions=[
        ArtifactCaption(
            artifact_id="edanmdm:nasm_test_1",
            caption="The Apollo Command Module carried astronauts to the Moon and back.",
        )
    ],
    limitations=["date_display missing on some objects"],
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_run_agent():
    with patch(
        "archivediver_api.main.run_agent",
        new=AsyncMock(return_value=([FAKE_ARTIFACT], FAKE_TOOL_CALLS, FAKE_LLM_OUTPUT, FAKE_NOTICES)),
    ) as m:
        yield m


def test_post_exhibit_returns_200(client, mock_run_agent):
    resp = client.post("/api/exhibit", json={"topic": "apollo program", "artifactCount": 3})
    assert resp.status_code == 200


def test_post_exhibit_response_shape(client, mock_run_agent):
    resp = client.post("/api/exhibit", json={"topic": "apollo program", "artifactCount": 3})
    data = resp.json()

    assert "title" in data
    assert "intro" in data
    assert "artifacts" in data
    assert "timeline" in data
    assert "dev" in data


def test_post_exhibit_llm_title_and_intro(client, mock_run_agent):
    resp = client.post("/api/exhibit", json={"topic": "apollo program", "artifactCount": 3})
    data = resp.json()

    assert data["title"] == "Apollo: Engineering a Moon Landing"
    assert data["intro"] == "Three artifacts trace the technology and ambition behind the Apollo program."


def test_post_exhibit_artifact_fields(client, mock_run_agent):
    resp = client.post("/api/exhibit", json={"topic": "apollo program", "artifactCount": 3})
    artifact = resp.json()["artifacts"][0]

    assert artifact["id"] == "edanmdm:nasm_test_1"
    assert artifact["title"] == "Apollo Command Module"
    assert artifact["image_url"] == "https://ids.si.edu/test_screen.jpg"
    assert artifact["source_url"] == "https://airandspace.si.edu/test"


def test_post_exhibit_artifact_caption_merged(client, mock_run_agent):
    resp = client.post("/api/exhibit", json={"topic": "apollo program", "artifactCount": 3})
    artifact = resp.json()["artifacts"][0]

    assert artifact["caption"] == "The Apollo Command Module carried astronauts to the Moon and back."


def test_post_exhibit_dev_tool_calls(client, mock_run_agent):
    resp = client.post("/api/exhibit", json={"topic": "apollo program", "artifactCount": 3})
    dev = resp.json()["dev"]

    assert len(dev["tool_calls"]) == 1
    assert dev["tool_calls"][0]["tool"] == "search_items"
    assert dev["tool_calls"][0]["output_count"] == 1


def test_post_exhibit_dev_limitations_populated(client, mock_run_agent):
    resp = client.post("/api/exhibit", json={"topic": "apollo program", "artifactCount": 3})
    dev = resp.json()["dev"]

    assert "date_display missing on some objects" in dev["limitations"]


def test_post_exhibit_timeline_built_from_artifacts(client, mock_run_agent):
    resp = client.post("/api/exhibit", json={"topic": "apollo program", "artifactCount": 3})
    timeline = resp.json()["timeline"]

    assert len(timeline) == 1
    assert timeline[0]["date"] == "1967"
    assert timeline[0]["label"] == "Apollo Command Module"


def test_post_exhibit_with_time_period(client, mock_run_agent):
    resp = client.post(
        "/api/exhibit", json={"topic": "apollo program", "timePeriod": "1960s", "artifactCount": 3}
    )
    assert resp.status_code == 200
    mock_run_agent.assert_called_once()
    call_kwargs = mock_run_agent.call_args.kwargs
    assert call_kwargs["time_period"] == "1960s"


def test_post_exhibit_invalid_count_too_high(client, mock_run_agent):
    resp = client.post("/api/exhibit", json={"topic": "space", "artifactCount": 11})
    assert resp.status_code == 422


def test_post_exhibit_empty_topic_rejected(client, mock_run_agent):
    resp = client.post("/api/exhibit", json={"topic": ""})
    assert resp.status_code == 422


def test_post_exhibit_missing_topic_rejected(client, mock_run_agent):
    resp = client.post("/api/exhibit", json={"artifactCount": 3})
    assert resp.status_code == 422


def test_post_exhibit_no_artifacts(client):
    empty_llm = LLMExhibitOutput(
        title="Exhibit: Obscure Topic",
        intro="No artifacts were found.",
        captions=[],
        limitations=["No image-bearing artifacts found for this topic."],
    )
    with patch(
        "archivediver_api.main.run_agent",
        new=AsyncMock(return_value=([], [], empty_llm, [])),
    ):
        resp = client.post("/api/exhibit", json={"topic": "obscure topic"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["artifacts"] == []
        assert data["timeline"] == []
        assert data["dev"]["tool_calls"] == []
        assert len(data["dev"]["limitations"]) > 0


def test_post_exhibit_503_on_mcp_failure(client):
    with patch(
        "archivediver_api.main.run_agent",
        new=AsyncMock(side_effect=ConnectionError("MCP server unavailable")),
    ):
        resp = client.post("/api/exhibit", json={"topic": "space"})
        assert resp.status_code == 503


def test_post_exhibit_artifact_has_no_image_download_url(client, mock_run_agent):
    resp = client.post("/api/exhibit", json={"topic": "apollo program", "artifactCount": 3})
    artifact = resp.json()["artifacts"][0]
    assert "image_download_url" not in artifact
