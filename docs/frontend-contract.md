# Frontend Contract

Stage 2 frontend contract for the ArchiveDiver vertical slice MVP.

Updated for Stage 2 backend: LangChain two-phase agent now generates `title`, `intro`, `caption` per artifact, and `dev.limitations`. Request fields renamed to `artifactCount` and `timePeriod`.

## Goals

- Keep backend behavior unchanged.
- Build the UI against a mock `POST /api/exhibit` response first.
- Verify in this order:
  1. Frontend builds
  2. Mock UI renders
  3. Real backend is wired and tested once
- If the live backend check fails or behaves unexpectedly, stop and investigate before continuing.

## Visual Direction

- Museum-like editorial UI.
- Background: warm off-white parchment tone.
- Accents: tan, umber, muted brown.
- Typography:
  - Serif for headline and historical framing copy.
  - Modern sans serif for controls, metadata, and artifact cards.
- Layout:
  - Centered page with a strong hero at the top.
  - Hero contains topic, timeline period, artifact count, and the primary action.
  - Results render below as a curated exhibit rather than a dashboard.
- Motion:
  - Smooth hover lift on cards.
  - Soft transitions for button state and panels.
- Icons:
  - Tasteful, sparse, non-emoji display icons only.

## Request Schema

`POST /api/exhibit`

```json
{
  "topic": "apollo program",
  "timePeriod": "1900s",
  "artifactCount": 5
}
```

| Field           | Type          | Required | Constraints | Default |
|-----------------|---------------|----------|-------------|---------|
| `topic`         | string        | yes      | min length 1 |        |
| `artifactCount` | integer       | no       | 1 to 10     | 5       |
| `timePeriod`    | string / null | no       | date filter | null    |

HTTP 422 if topic is empty or `artifactCount` is out of range.
HTTP 503 if MCP server or LLM is unavailable.

## Inputs

The hero form posts the request shape above:

### Input rules

- `topic`
  - Required free-text input.
  - Placeholder should guide toward a historical topic or keyword.
- `timePeriod`
  - Presented as preset chips, not free text.
  - Values:
    - `Any` -> `null`
    - `1600s`
    - `1700s`
    - `1800s`
    - `1900s`
    - `2000s`
- `artifactCount`
  - Integer control from 1 to 10.
  - Default 5.
- Submit button label:
  - Idle: `Build Exhibit`
  - Loading: `Diving…`

## Response Schema

```json
{
  "title": "Apollo: Engineering a Moon Landing",
  "intro": "Three artifacts trace the technology and ambition of the Apollo program.",
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
      "image_alt": "Scale model of Saturn V Rocket",
      "rights": "CC0",
      "subject_tags": ["Human spaceflight"],
      "place_tags": ["United States of America"]
    }
  ],
  "timeline": [
    { "date": "1969", "label": "Model, Rocket, Saturn V, 1:34" }
  ],
  "dev": {
    "tool_calls": [
      { "tool": "search_artifacts", "input": { "query": "apollo program", "limit": 3 }, "output_count": 3 }
    ],
    "limitations": ["date_display is empty on most NASM objects; timeline may be sparse."]
  }
}
```

### Field origin table

| Field                      | Origin  | Notes                                                        |
|----------------------------|---------|--------------------------------------------------------------|
| `title`                    | LLM     | Always non-empty.                                            |
| `intro`                    | LLM     | Always non-empty.                                            |
| `artifacts[].caption`      | LLM     | 1-2 sentences. May be empty if generation failed.            |
| `dev.limitations`          | LLM     | May be empty array.                                          |
| `artifacts[].id`           | Source  | Smithsonian canonical id.                                    |
| `artifacts[].title`        | Source  | Always non-empty.                                            |
| `artifacts[].date_display` | Source  | Often empty for NASM.                                        |
| `artifacts[].date_indexed` | Source  | Often empty.                                                 |
| `artifacts[].creator_display` | Source | May be empty.                                             |
| `artifacts[].description`  | Source  | May be empty.                                                |
| `artifacts[].object_type`  | Source  | Semicolon-separated. May be empty.                           |
| `artifacts[].unit_code`    | Source  | e.g. NASM, CHNDM.                                           |
| `artifacts[].unit_name`    | Source  | Display name of museum. May be empty.                        |
| `artifacts[].source_url`   | Source  | Always non-empty.                                            |
| `artifacts[].image_url`    | Source  | Always non-empty (no-image items dropped by MCP).            |
| `artifacts[].thumbnail_url`| Source  | May be empty.                                                |
| `artifacts[].image_alt`    | Source  | Falls back to title.                                         |
| `artifacts[].rights`       | Source  | May be empty.                                                |
| `artifacts[].subject_tags` | Source  | May be empty array.                                          |
| `artifacts[].place_tags`   | Source  | May be empty array.                                          |
| `timeline`                 | Derived | Built from artifacts with non-empty dates.                   |
| `dev.tool_calls`           | Derived | One entry per MCP tool call.                                 |

Note: `image_download_url` is present in the MCP layer but stripped server-side. It will never appear in the frontend response.

## Response Mapping

### Exhibit header

- `title`
  - Primary exhibit heading. LLM-generated.
- `intro`
  - Introductory paragraph under the title. LLM-generated.

### Artifact cards

Each artifact card renders:

- Image:
  - Use `image_url` as the primary display image.
  - Use `image_alt` for alt text.
  - On image load error, show a placeholder. Never block the card.
- Card title:
  - `title`
- Card caption:
  - Use `caption` (LLM-generated). May be empty; render nothing if empty.
  - Do not fall back to `description` or `title` for caption.
- Source details:
  - Date: `date_display || date_indexed[0] || ""`
  - Creator: `creator_display`
  - Museum/source: `unit_name`
  - Object type: `object_type`
  - Rights: `rights`
  - Source link: `source_url` (label: "View at Smithsonian")
- Optional metadata chips:
  - `subject_tags`
  - `place_tags`

Missing optional fields should disappear from the card instead of rendering placeholders.

### Timeline panel

- Use `timeline` when non-empty.
- Each entry renders:
  - `date`
  - `label`
- If empty, render a sparse-state note explaining that no structured dates were available for this result set.

### Dev panel

- Render `dev.tool_calls` and `dev.limitations`.
- Keep the panel collapsed by default so the editorial UI stays clean.
- Show at least:
  - tool name
  - query input
  - result count
- `dev.limitations` is now populated by the LLM with observed gaps.
- If empty, show a quiet “No limitations reported” state.

## States

- Initial:
  - Hero visible, results hidden.
- Loading:
  - Submit button shows `Diving…`
  - Existing results remain visible until replaced.
- Success:
  - Render exhibit header, artifact grid, timeline section, and dev panel.
- Empty artifacts:
  - Render intro and a simple note that no image-bearing artifacts were returned.
- Error:
  - Render a small inline error message near the hero.
  - Do not expose stack traces or backend internals.

## Frontend Data Boundary

- Define shared TypeScript types that mirror the current backend models.
- Use one client abstraction with two implementations:
  - mock client for default slice development
  - HTTP client for the final live wiring pass
- The switch between mock and live data should happen in one place.

## Assets

Create `apps/web/public/assets/` as the drop location for:

- favicon SVG
- logo SVG
- secondary logo SVG

The app should not require those assets to exist in order to run during this slice.

## Testing

Targeted tests only. Skip Playwright.

- Hero defaults and period-chip behavior
- Loading button state
- Mock exhibit rendering
- Fallback rendering when optional artifact fields are missing
- Empty timeline state
- Dev panel tool-call rendering
