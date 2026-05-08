# API Contract

Stage 1 verified on 2026-05-08. This document is the Stage 2 frontend handoff reference.

---

## POST /api/exhibit

### Request

```json
{
  "topic": "apollo program",
  "period": "1960s",
  "count": 3
}
```

| Field    | Type            | Required | Constraints        | Default |
|----------|-----------------|----------|--------------------|---------|
| `topic`  | string          | yes      | min length 1       |         |
| `period` | string or null  | no       | passed as date filter to Smithsonian | null |
| `count`  | integer         | no       | 1 to 10 inclusive  | 5       |

Returns HTTP 422 if `topic` is empty, `count` is out of range, or the body is malformed.

### Response (200)

```json
{
  "title": "Exhibit: Apollo Program",
  "intro": "A collection of 3 artifacts exploring apollo program.",
  "artifacts": [
    {
      "id": "edanmdm:nasm_A19940223000",
      "title": "Model, Rocket, Saturn V, 1:34",
      "date_display": "",
      "date_indexed": [],
      "creator_display": "David P. Gianakos",
      "description": "",
      "object_type": "Missiles; Rockets; Models",
      "unit_code": "NASM",
      "unit_name": "National Air and Space Museum",
      "source_url": "http://n2t.net/ark:/65665/...",
      "image_url": "https://ids.si.edu/ids/download?id=...screen",
      "thumbnail_url": "https://ids.si.edu/ids/download?id=...thumb",
      "image_alt": "Scale model of black and white Saturn V Rocket",
      "rights": "CC0",
      "subject_tags": ["Outer space", "Human spaceflight"],
      "place_tags": ["United States of America"]
    }
  ],
  "timeline": [
    { "date": "1960s", "label": "Model, Rocket, Saturn V, 1:34" }
  ],
  "dev": {
    "tool_calls": [
      {
        "tool": "search_artifacts",
        "input": { "query": "apollo program", "limit": 3 },
        "output_count": 3
      }
    ],
    "limitations": []
  }
}
```

### Response field types

| Field                         | Type                   | Notes |
|-------------------------------|------------------------|-------|
| `title`                       | string                 | Hardcoded template: "Exhibit: {topic.title()}" |
| `intro`                       | string                 | Hardcoded template with count and period |
| `artifacts`                   | array of ArtifactOut   | May be empty if no image-bearing results found |
| `artifacts[].id`              | string                 | Smithsonian canonical id, e.g. `edanmdm:nasm_...` |
| `artifacts[].title`           | string                 | Always non-empty |
| `artifacts[].date_display`    | string                 | Human-readable, often empty |
| `artifacts[].date_indexed`    | string[]               | Structured dates, often empty |
| `artifacts[].creator_display` | string                 | May be empty |
| `artifacts[].description`     | string                 | May be empty; sourced from notes labeled Description/Abstract/Caption |
| `artifacts[].object_type`     | string                 | Semicolon-separated; may be empty |
| `artifacts[].unit_code`       | string                 | Smithsonian unit code, e.g. NASM, CHNDM |
| `artifacts[].unit_name`       | string                 | Display name of museum/unit |
| `artifacts[].source_url`      | string                 | Public Smithsonian page for the object |
| `artifacts[].image_url`       | string                 | Screen-resolution image; always non-empty (items without images are dropped) |
| `artifacts[].thumbnail_url`   | string                 | Thumbnail; may be empty if not provided by Smithsonian |
| `artifacts[].image_alt`       | string                 | Falls back to title if accessibility text is blank |
| `artifacts[].rights`          | string                 | License/rights text; may be empty |
| `artifacts[].subject_tags`    | string[]               | May be empty |
| `artifacts[].place_tags`      | string[]               | May be empty |
| `timeline`                    | array of TimelineEntry | Sorted by date_display; only artifacts with non-empty dates appear |
| `timeline[].date`             | string                 | Artifact date_display value |
| `timeline[].label`            | string                 | Artifact title |
| `dev.tool_calls`              | array                  | One entry per MCP tool call made |
| `dev.tool_calls[].tool`       | string                 | Always "search_artifacts" in Stage 1 |
| `dev.tool_calls[].input`      | object                 | Tool input args |
| `dev.tool_calls[].output_count` | integer              | Number of artifacts returned by the tool |
| `dev.limitations`             | string[]               | Currently always empty; reserved for Stage 2 |

---

## MCP Tool: search_artifacts

Tool name: `search_artifacts`

Exposed by `apps/mcp-smithsonian` over HTTP/SSE at `http://localhost:9000/sse`.

### Input

| Field    | Type           | Required | Default | Notes |
|----------|----------------|----------|---------|-------|
| `query`  | string         | yes      |         | Search terms passed to Smithsonian |
| `limit`  | integer        | no       | 5       | Desired output count after image filtering |
| `period` | string or null | no       | null    | Appended to query as `date:"<period>"` |

The MCP server fetches `limit * 4` rows (capped at 50) from Smithsonian to buffer against units (SIL, SIA) that tag items as having images but have no actual online_media. The query is also prefixed with `online_media_type:Images` to bias search results toward image-bearing units (NASM, CHNDM, etc.).

### Output

JSON string containing an array of normalized artifact objects. Only items that pass the image validation chain are included. May be an empty array.

```json
[
  {
    "id": "edanmdm:nasm_A19940223000",
    "record_id": "nasm_A19940223000",
    "title": "Model, Rocket, Saturn V, 1:34",
    "date_display": "",
    "date_indexed": [],
    "creator_display": "David P. Gianakos",
    "description": "",
    "object_type": "Missiles; Rockets; Models",
    "unit_code": "NASM",
    "unit_name": "National Air and Space Museum",
    "source_url": "http://n2t.net/ark:/65665/...",
    "image_url": "https://ids.si.edu/ids/download?id=..._screen",
    "thumbnail_url": "https://ids.si.edu/ids/download?id=..._thumb",
    "image_download_url": "https://ids.si.edu/ids/download?id=....jpg",
    "image_alt": "Scale model...",
    "rights": "CC0",
    "subject_tags": [],
    "place_tags": ["United States of America"]
  }
]
```

`record_id` and `image_download_url` are present in the MCP output but are stripped from the `ArtifactOut` response. The frontend only receives `ArtifactOut` fields.

---

## Known Limitations

- `artifacts` may be empty for queries that return only SIL/SIA results (both units tag items with `online_media_type:Images` but provide no actual media).
- `date_display` and `date_indexed` are often empty for NASM objects; the timeline will be sparse or empty for space-related queries.
- `description` is often empty (NASM objects frequently omit notes labeled Description/Abstract/Caption).
- `thumbnail_url` may be empty if the Smithsonian item provides no thumbnail resource.
- `period` filter uses a Smithsonian `date:` query term which is not guaranteed to match all date formats in the collection.
- The title and intro are hardcoded templates. Stage 2 should replace these with LLM-generated text.
- `dev.limitations` is always an empty array in Stage 1. Stage 2 should populate it with notes about sparse results or dropped artifacts.
- The LLM model is `claude-haiku-4-5-20251001` (fast and cheap for prototyping).

---

## Environment Variables

| Variable              | Required by         | Notes |
|-----------------------|---------------------|-------|
| `SMITHSONIAN_API_KEY` | `apps/mcp-smithsonian` | Falls back to `DEMO_KEY` if unset; `DEMO_KEY` is rate-limited |
| `ANTHROPIC_API_KEY`   | `apps/api`          | Required for live LLM calls |
| `MCP_HOST`            | `apps/mcp-smithsonian` | Default: `127.0.0.1` |
| `MCP_PORT`            | `apps/mcp-smithsonian` | Default: `9000` |
| `MCP_URL`             | `apps/api`          | Default: `http://localhost:9000/sse` |

---

## How to Run Locally

All commands run from the repo root. The shared venv is at `.venv`.

### Install

```bash
python3 -m venv .venv
.venv/bin/pip install -e "apps/mcp-smithsonian[dev]"
.venv/bin/pip install -e "apps/api[dev]"
```

### Start MCP server

```bash
export $(grep -v '^#' .env | xargs)
PYTHONPATH=apps/mcp-smithsonian/src .venv/bin/python -m mcp_smithsonian.server
# Listening on http://127.0.0.1:9000
```

### Start API server

```bash
export $(grep -v '^#' .env | xargs)
PYTHONPATH=apps/api/src .venv/bin/uvicorn archivediver_api.main:app --port 8000
# Listening on http://127.0.0.1:8000
```

### Test

```bash
# MCP unit tests (no network)
.venv/bin/python -m pytest apps/mcp-smithsonian/tests/test_normalizer.py apps/mcp-smithsonian/tests/test_tool.py -v

# Smithsonian live test (network, uses SMITHSONIAN_API_KEY)
export $(grep -v '^#' .env | xargs) && .venv/bin/python -m pytest apps/mcp-smithsonian/tests/test_live.py -v -s

# API mocked test (no network, no Anthropic)
.venv/bin/python -m pytest apps/api/tests/test_exhibit_mocked.py -v

# Live end-to-end (requires both servers running)
LIVE_TESTS=1 .venv/bin/python -m pytest apps/api/tests/test_live.py -v -s
```

### Curl check

```bash
curl -s -X POST http://localhost:8000/api/exhibit \
  -H "Content-Type: application/json" \
  -d '{"topic":"apollo program","count":3}' | python3 -m json.tool
```
