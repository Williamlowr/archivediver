# Frontend Contract

Stage 2 frontend contract for the ArchiveDiver vertical slice MVP. This UI is intentionally minimal and exists to prove the browser flow before iteration.

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

## Inputs

The hero form posts the existing API request shape:

```json
{
  "topic": "apollo program",
  "period": "1900s",
  "count": 5
}
```

### Input rules

- `topic`
  - Required free-text input.
  - Placeholder should guide toward a historical topic or keyword.
- `period`
  - Presented as preset chips, not free text.
  - Values:
    - `Any` -> `null`
    - `1600s`
    - `1700s`
    - `1800s`
    - `1900s`
    - `2000s`
- `count`
  - Integer control from 1 to 10.
  - Default 5.
- Submit button label:
  - Idle: `Build Exhibit`
  - Loading: `Diving…`

## Response Mapping

The frontend consumes the current `ExhibitResponse` shape exactly. No backend changes are required.

### Exhibit header

- `title`
  - Primary exhibit heading.
- `intro`
  - Introductory paragraph under the title.

### Artifact cards

Each artifact card renders:

- Image:
  - Use `image_url` as the primary display image.
  - Use `image_alt` for alt text.
- Card title:
  - `title`
- Card caption:
  - Derived in the frontend as `description || title`
  - Do not add a `caption` field to the API.
- Source details:
  - Date: `date_display || date_indexed[0] || ""`
  - Creator: `creator_display`
  - Museum/source: `unit_name`
  - Object type: `object_type`
  - Rights: `rights`
  - Source link: `source_url`
- Optional metadata chips:
  - `subject_tags`
  - `place_tags`

Missing optional fields should simply disappear from the card instead of rendering placeholders.

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
- If `dev.limitations` is empty, show a quiet “No limitations reported” state.

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
