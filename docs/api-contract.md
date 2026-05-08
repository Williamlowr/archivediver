# API Contract

Stage 2 operational as of 2026-05-08. LLM now generates title, intro, per-artifact captions, and limitations.
Request fields renamed: `count` -> `artifactCount`, `period` -> `timePeriod`.
See `docs/frontend-contract.md` for the full frontend reference.

---

## POST /api/exhibit

### Request

```json
{
  "topic": "apollo program",
  "timePeriod": "1960s",
  "artifactCount": 3
}
```

| Field           | Type            | Required | Constraints        | Default |
|-----------------|-----------------|----------|--------------------|---------|
| `topic`         | string          | yes      | min length 1       |         |
| `timePeriod`    | string or null  | no       | passed as date filter to Smithsonian | null |
| `artifactCount` | integer         | no       | 1 to 10 inclusive  | 5       |

Returns HTTP 422 if `topic` is empty, `artifactCount` is out of range, or the body is malformed.
Returns HTTP 503 if the MCP server or LLM is unavailable.

### Response (200)

```json
{
  "title": "Apollo: Engineering a Moon Landing",
  "intro": "Three artifacts trace the technology and ambition behind the Apollo program.",
  "artifacts": [
    {
      "id": "edanmdm:nasm_A19940223000",
      "title": "Model, Rocket, Saturn V, 1:34",
      "caption": "This 1:34 scale model documents the Saturn V rocket used in Apollo missions.",
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
    "limitations": ["date_display is empty on most NASM objects; timeline may be sparse."]
  }
}
```

### Response field types

| Field                         | Type                   | Origin  | Notes |
|-------------------------------|------------------------|---------|-------|
| `title`                       | string                 | LLM     | LLM-generated exhibit title |
| `intro`                       | string                 | LLM     | LLM-generated 2-3 sentence intro |
| `artifacts`                   | array of ArtifactOut   | mixed   | May be empty if no image-bearing results found |
| `artifacts[].id`              | string                 | Source  | Smithsonian canonical id, e.g. `edanmdm:nasm_...` |
| `artifacts[].title`           | string                 | Source  | Always non-empty |
| `artifacts[].caption`         | string                 | LLM     | 1-2 sentence caption; may be empty if generation failed |
| `artifacts[].date_display`    | string                 | Source  | Human-readable, often empty |
| `artifacts[].date_indexed`    | string[]               | Source  | Structured dates, often empty |
| `artifacts[].creator_display` | string                 | Source  | May be empty |
| `artifacts[].description`     | string                 | Source  | May be empty; sourced from notes labeled Description/Abstract/Caption |
| `artifacts[].object_type`     | string                 | Source  | Semicolon-separated; may be empty |
| `artifacts[].unit_code`       | string                 | Source  | Smithsonian unit code, e.g. NASM, CHNDM |
| `artifacts[].unit_name`       | string                 | Source  | Display name of museum/unit |
| `artifacts[].source_url`      | string                 | Source  | Public Smithsonian page for the object |
| `artifacts[].image_url`       | string                 | Source  | Screen-resolution image; always non-empty (items without images are dropped) |
| `artifacts[].thumbnail_url`   | string                 | Source  | Thumbnail; may be empty if not provided by Smithsonian |
| `artifacts[].image_alt`       | string                 | Source  | Falls back to title if accessibility text is blank |
| `artifacts[].rights`          | string                 | Source  | License/rights text; may be empty |
| `artifacts[].subject_tags`    | string[]               | Source  | May be empty |
| `artifacts[].place_tags`      | string[]               | Source  | May be empty |
| `timeline`                    | array of TimelineEntry | Derived | Sorted by date_display; only artifacts with non-empty dates appear |
| `timeline[].date`             | string                 | Derived | Artifact date_display value |
| `timeline[].label`            | string                 | Derived | Artifact title |
| `dev.tool_calls`              | array                  | Derived | One entry per MCP tool call made |
| `dev.tool_calls[].tool`       | string                 | Derived | Always "search_items" in Stage 2 |
| `dev.tool_calls[].input`      | object                 | Derived | Tool input args |
| `dev.tool_calls[].output_count` | integer              | Derived | Number of artifacts returned by the tool |
| `dev.limitations`             | string[]               | LLM     | LLM-observed result gaps; may be empty array |
| `dev.limitations`             | string[]               | Currently always empty; reserved for Stage 2 |

---

## MCP Tools

All three tools are exposed by `apps/mcp-smithsonian` over HTTP/SSE at `http://localhost:9000/sse`.

---

### `search_items`

Search Smithsonian Open Access for artifacts matching a topic or keyword. Only returns items with confirmed image URLs.

#### Input

| Field    | Type           | Required | Default | Notes |
|----------|----------------|----------|---------|-------|
| `query`  | string         | yes      |         | Search terms; must be non-empty |
| `limit`  | integer        | no       | 5       | Desired output count, 1 to 50 |
| `period` | string or null | no       | null    | Appended to query as `date:"<period>"` |

The MCP server fetches `limit * 4` rows (capped at 50) from Smithsonian to buffer against units (SIL, SIA) that tag items as having images but have no actual online_media. The query is also prefixed with `online_media_type:Images` to bias search results toward image-bearing units (NASM, CHNDM, etc.).

#### Output

JSON string containing an array of normalized artifact objects. May be an empty array.

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

### `get_item_details`

Fetch full normalized details for a specific Smithsonian item by canonical ID. Uses the `content/{id}` endpoint.

#### Input

| Field     | Type   | Required | Notes |
|-----------|--------|----------|-------|
| `item_id` | string | yes      | Smithsonian canonical ID, e.g. `edanmdm:nasm_A19940223000`; must be non-empty |

#### Output

JSON object with all normalized artifact fields (same schema as a `search_items` array element), or an error object if the item has no usable image:

```json
{ "error": "item has no usable image", "item_id": "edanmdm:sil_123" }
```

---

### `get_item_media`

Extract image URLs and citation metadata only for a specific Smithsonian item. Lighter-weight than `get_item_details`.

#### Input

| Field     | Type   | Required | Notes |
|-----------|--------|----------|-------|
| `item_id` | string | yes      | Smithsonian canonical ID; must be non-empty |

#### Output

```json
{
  "item_id": "edanmdm:nasm_A19940223000",
  "title": "Model, Rocket, Saturn V, 1:34",
  "creator_display": "David P. Gianakos",
  "image_url": "https://ids.si.edu/ids/download?id=..._screen",
  "thumbnail_url": "https://ids.si.edu/ids/download?id=..._thumb",
  "image_download_url": "https://ids.si.edu/ids/download?id=....jpg",
  "image_alt": "Scale model...",
  "source_url": "http://n2t.net/ark:/65665/...",
  "rights": "CC0",
  "unit_code": "NASM",
  "unit_name": "National Air and Space Museum"
}
```

Image fields are empty strings if the item has no usable media.

---

## Known Limitations

- `artifacts` may be empty for queries that return only SIL/SIA results (both units tag items with `online_media_type:Images` but provide no actual media).
- `date_display` and `date_indexed` are often empty for NASM objects; the timeline will be sparse or empty for space-related queries.
- `description` is often empty (NASM objects frequently omit notes labeled Description/Abstract/Caption).
- `thumbnail_url` may be empty if the Smithsonian item provides no thumbnail resource.
- `timePeriod` filter uses a Smithsonian `date:` query term which is not guaranteed to match all date formats in the collection.
- `artifacts[].caption` may be empty if Phase 2 (structured output generation) fails; a fallback limitation note is added to `dev.limitations`.
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
  -d '{"topic":"apollo program","artifactCount":3}' | python3 -m json.tool
```
