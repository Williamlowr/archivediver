# Smithsonian Data Notes

Purpose: define the Smithsonian API contract for `apps/mcp-smithsonian` before MCP and LangChain implementation.

Keep Smithsonian data separate from LLM output. The MCP server should return normalized artifact facts only. Exhibit title, intro, captions, and timeline stay backend-generated.

## API operations needed
- `GET /openaccess/api/v1.0/search`
  - Primary read path for MVP.
  - Pass `q`, `rows`, `start`, `sort=relevancy`, `type=edanmdm`, `row_group=objects`.
  - Search rows already include the nested `content` payload needed for normalization.
- `GET /openaccess/api/v1.0/content/{id}`
  - Optional follow-up lookup when we need to re-fetch one object.
  - Not required for normal search normalization.
- `GET /openaccess/api/v1.0/terms/{category}`
  - Useful for diagnostics and future filter UIs.
  - Relevant categories from the official client: `culture`, `data_source`, `date`, `object_type`, `online_media_type`, `place`, `topic`, `unit_code`.
- Official but not needed for MVP:
  - `GET /openaccess/api/v1.0/stats`
  - `GET /openaccess/api/v1.0/category/{category}/search`

## Fields available from search
Each search row can include:
- Top level: `id`, `title`, `unitCode`, `type`, `url`, `hash`, `docSignature`, `timestamp`, `lastTimeUpdated`, `version`
- `content.freetext`
  - Human-readable arrays such as `date`, `name`, `notes`, `place`, `topic`, `dataSource`, `objectType`, `objectRights`, `identifier`
  - Useful for display values, but labels vary by unit
- `content.indexedStructured`
  - More stable indexed arrays such as `date`, `name`, `place`, `topic`, `object_type`, `online_media_type`
  - Best source for tags and structured filtering
- `content.descriptiveNonRepeating`
  - Best source for stable singletons such as `record_ID`, `unit_code`, `data_source`, `record_link`, `metadata_usage`, and `online_media`

## Fields available from item results
The live `content/{id}` sample returned the same practical structure as search rows:
- Same top-level row fields
- Same nested `content.freetext`
- Same nested `content.indexedStructured`
- Same nested `content.descriptiveNonRepeating`

Practical implication: for MVP, `search` is enough for normalization and media filtering. `content/{id}` is a re-fetch path, not the normal path.

## Raw to normalized mapping

| Normalized field | Raw field | Notes |
| --- | --- | --- |
| `id` | `row.url` | Preferred canonical lookup id, for example `edanmdm:chndm_1901-39-3309` |
| `record_id` | `content.descriptiveNonRepeating.record_ID` | Keep for debugging and display, not for `content/{id}` lookups |
| `title` | `content.descriptiveNonRepeating.title.content` fallback `row.title` | Prefer nested title when present |
| `date_display` | first useful `content.freetext.date[].content` | Human-readable date string |
| `date_indexed` | `content.indexedStructured.date` | Keep as array |
| `creator_display` | joined `content.freetext.name[].content` | Join with `; `. Labels vary: `Designer`, `Author`, `Creator`, etc. |
| `description` | first matching `content.freetext.notes[].content` where label is `Description`, `Abstract`, or `Caption` | Do not treat all notes as descriptions |
| `object_type` | joined `content.indexedStructured.object_type` fallback `content.freetext.objectType[].content` | Join with `; ` and keep full raw values in `raw_debug` |
| `unit_code` | `content.descriptiveNonRepeating.unit_code` fallback `row.unitCode` | Stable code |
| `unit_name` | `content.descriptiveNonRepeating.data_source` fallback first `content.freetext.dataSource[].content` | Display name, not a formal unit id |
| `source_url` | `content.descriptiveNonRepeating.record_link` | Public Smithsonian page for the object |
| `image_url` | derived from `content.descriptiveNonRepeating.online_media.media[]` | See media rule below |
| `thumbnail_url` | `online_media.media[].resources[]` labeled `Thumbnail Image` fallback `media.thumbnail` | Thumbnail-safe URL |
| `image_download_url` | `online_media.media[].resources[]` labeled `High-resolution JPEG` | Best direct download candidate |
| `image_alt` | `online_media.media[].altTextAccessibility` fallback title | Accessibility text is often blank |
| `rights` | first `content.freetext.objectRights[].content` fallback `content.descriptiveNonRepeating.metadata_usage.access` | Keep raw rights text when available |
| `subject_tags` | `content.indexedStructured.topic` | Start with topic only in v1 |
| `place_tags` | `content.indexedStructured.place` | Keep as array |
| `raw_debug` | selected raw Smithsonian fields | Debug only, never passed to the LLM by default |

## Which fields are unreliable or missing
- `content.freetext.*` labels are unit-specific and not stable enough to treat as schema.
- `content.indexedStructured.online_media_type` is not enough to prove a real image exists.
- `content.descriptiveNonRepeating.record_ID` is not a safe `content/{id}` lookup key by itself.
- `altTextAccessibility` and descriptive media text are often blank.
- `unit_name` is really `data_source` display text, not a canonical museum-name field.

## How to detect usable image/media
Drop items at the MCP layer unless all of the following are true:
- `content.descriptiveNonRepeating.online_media.media` exists and has at least one entry
- At least one media entry has a usable URL from this fallback chain:
  1. `media.resources[]` item labeled `Screen Image`
  2. `media.resources[]` item labeled `High-resolution JPEG`
  3. `media.content`
  4. `media.thumbnail`

If no URL survives that chain, do not return the item to the backend or LLM.

Do not trust `indexedStructured.online_media_type` alone. Live checks confirmed false positives.

## How to build/extract URLs
- Artifact source URL:
  - Use `content.descriptiveNonRepeating.record_link`
- Canonical Smithsonian lookup id:
  - Use `row.url`
  - URL-encode it when calling `content/{id}`
- Confirmed `content/{id}` behavior from live checks:
  - `row.url` worked
  - top-level `row.id` also worked in the sampled object
  - `record_ID` alone returned `404`, so do not use it as the lookup id
- Image URL:
  - Use the first usable media URL from the fallback chain above
- Thumbnail URL:
  - Prefer `Thumbnail Image` resource, else `media.thumbnail`
- Direct download URL:
  - Prefer `High-resolution JPEG`

`media.content` and `media.thumbnail` were returned as `https://ids.si.edu/ids/deliveryService?id=...` URLs in the live image-bearing sample. `resources[].url` can provide more specific renditions.

## Museum/unit reliability
- Confirmed good live sample:
  - `CHNDM` returned `online_media.media[]`, `mediaCount`, IDS URLs, and downloadable resources
- Confirmed unreliable for `online_media_type:Images`:
  - `SIL` returned rows tagged with `indexedStructured.online_media_type: Images` but no `descriptiveNonRepeating.online_media`
- All other units are unverified in this repo so far
  - Broad spot checks hit `OVER_RATE_LIMIT` on `DEMO_KEY`
  - Do not blacklist untested units yet

## Recommended normalized JSON shape
```json
{
  "id": "edanmdm:chndm_1901-39-3309",
  "record_id": "chndm_1901-39-3309",
  "title": "Thirteen Apollo Subjects for Ceiling",
  "date_display": "early 19th century",
  "date_indexed": ["1800s"],
  "creator_display": "Felice Giani, Italian, 1758-1823",
  "description": "Center, octagonal representation of Apollo and Muses.",
  "object_type": "Figures (representations); Drawings",
  "unit_code": "CHNDM",
  "unit_name": "Cooper Hewitt, Smithsonian Design Museum",
  "source_url": "https://collection.cooperhewitt.org/view/objects/asitem/id/10032",
  "image_url": "https://ids.si.edu/ids/download?id=CHSDM-3D4BA7C1D0CE2-000001_screen",
  "thumbnail_url": "https://ids.si.edu/ids/download?id=CHSDM-3D4BA7C1D0CE2-000001_thumb",
  "image_download_url": "https://ids.si.edu/ids/download?id=CHSDM-3D4BA7C1D0CE2-000001.jpg",
  "image_alt": "THIRTEEN APOLLO SUBJECTS FOR CEILING",
  "rights": "CC0",
  "subject_tags": [],
  "place_tags": ["Italy"],
  "raw_debug": {}
}
```

## Assumptions to re-test with a live key
- Search rows will keep including full nested `content`, so MCP can avoid a per-item `content/{id}` call in normal flow
- `row.url` will remain the safest lookup id across units
- `record_ID` will keep failing as a standalone `content/{id}` lookup id
- `SIL` false-positive image behavior is not unique among archive and library units
- `subject_tags` can stay limited to `indexedStructured.topic` in v1 without losing too much useful metadata

### Live-key results (2026-05-08)
- Search rows included nested `content` (sample: `apollo`, `rows=2`), including `descriptiveNonRepeating`, `indexedStructured`, and `freetext`.
- `content/{id}` lookup behavior:
  - `row.url`: worked (HTTP 200) in sampled object and across multiple unit spot checks.
  - top-level `row.id`: also worked (HTTP 200) in sampled object and across multiple unit spot checks.
  - `content.descriptiveNonRepeating.record_ID`: failed as a standalone lookup id (HTTP error).
- SIL image false positives:
  - Query `unit_code:SIL AND online_media_type:Images` returned rows with **no** `descriptiveNonRepeating.online_media.media` (25/25 in a quick probe).
  - Confirms we must validate real media via `descriptiveNonRepeating.online_media.media` (not `indexedStructured.online_media_type`).
- `subject_tags` from `indexedStructured.topic`:
  - Present in some rows, but not guaranteed (1/2 rows in the `apollo` sample had non-empty `topic`).

## Sources
- Official API client and operation list:
  - [Smithsonian/smithsonian-openaccess](https://github.com/Smithsonian/smithsonian-openaccess)
  - [si_openaccess.py](https://raw.githubusercontent.com/Smithsonian/smithsonian-openaccess/main/src/si_openaccess/si_openaccess.py)
- Official Smithsonian docs:
  - [Open Access developer tools](https://www.si.edu/openaccess/devtools)
  - [EDAN Open Access docs](https://edan.si.edu/openaccess/docs/)
- Live checks run on 2026-05-08 with `DEMO_KEY`:
  - `search?q=apollo&rows=2`
  - `terms/online_media_type`
  - `terms/unit_code`
  - `content/{id}` using `row.url`, top-level `id`, and `record_ID`
