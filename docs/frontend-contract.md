# Frontend Contract

Current frontend contract for `apps/web`.

## Request shape

Frontend posts this body to `POST /api/exhibit`:

```json
{
  "topic": "apollo program",
  "timePeriod": "1900s",
  "artifactCount": 5
}
```

- `topic` is required
- `timePeriod` can be `null`
- `artifactCount` stays within `1` to `10`

## Response assumptions

Frontend expects:

- `title` and `intro`
- `artifacts[]` with normalized Smithsonian fields plus `caption`
- `timeline[]`
- `dev.tool_calls[]` and `dev.limitations[]`

`image_download_url` and other MCP-only fields are not part of the frontend contract.

## Rendering rules

- The first artifact is featured.
- Remaining artifacts render as secondary cards.
- Caption is optional and should not fall back to description text.
- Empty optional metadata should disappear cleanly.
- Timeline can be empty.
- Dev panel should show tool calls and limitations, and default open.

## Client boundary

- `src/api.ts` is the fetch boundary.
- Presentation components should not translate API shapes.
- Default live path is relative `/api/exhibit`.
- Mock mode is controlled in one place with `VITE_USE_MOCK=true`.

## Frontend env vars

- `VITE_USE_MOCK`: use mock data instead of HTTP
- `VITE_API_BASE_URL`: optional absolute API base URL
- `VITE_API_PROXY_TARGET`: dev proxy target for Vite, defaults to `http://127.0.0.1:8000`

## Test focus

- request-shape mapping
- loading and error states
- artifact rendering with missing optional fields
- empty timeline state
- dev panel rendering
