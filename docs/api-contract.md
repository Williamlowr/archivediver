# API Contract

Current backend contract for `apps/api`.

## Endpoint

`POST /api/exhibit`

## Request body

```json
{
  "topic": "apollo program",
  "timePeriod": "1960s",
  "artifactCount": 3
}
```

- `topic`: required string, minimum length 1
- `timePeriod`: optional string or `null`
- `artifactCount`: optional integer, `1` to `10`, default `5`

## Success response

```json
{
  "title": "Apollo: Engineering a Moon Landing",
  "intro": "Three artifacts trace the technology behind the Apollo program.",
  "artifacts": [],
  "timeline": [],
  "dev": {
    "tool_calls": [],
    "limitations": []
  }
}
```

### Top-level fields

- `title`: LLM-generated exhibit title
- `intro`: LLM-generated intro
- `artifacts`: normalized Smithsonian artifacts with LLM captions
- `timeline`: derived from artifact dates
- `dev.tool_calls`: MCP tool trace
- `dev.limitations`: concrete gaps in the result set

### Artifact fields

Each artifact can include:

- `id`, `title`, `caption`
- `date_display`, `date_indexed`
- `creator_display`, `description`, `object_type`
- `unit_code`, `unit_name`
- `source_url`, `image_url`, `thumbnail_url`, `image_alt`, `rights`
- `subject_tags`, `place_tags`

The API does not expose MCP-only fields like `record_id` or `image_download_url`.

## Failure codes

- `422`: bad request body or validation failure
- `503`: MCP service unavailable or LLM request failed

## Backend notes

- Backend calls the MCP `search_items` tool once per request.
- Timeline entries are built from `date_display` or the first `date_indexed` value.
- Smithsonian artifacts without usable images are dropped in the MCP layer before they reach the API.
