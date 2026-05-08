# Smithsonian Data Notes

Short reference for `apps/mcp-smithsonian`.

## Endpoints in use

- `search`: main path for artifact discovery
- `content/{id}`: fetch one item by canonical id when needed

## Normalization rules

- Use `row.url` as the canonical Smithsonian id.
- Use `record_link` as the public source URL.
- Use `indexedStructured` for tags where possible.
- Use `freetext` fields only as fallbacks because labels vary by museum unit.

## Media rule

Do not return an artifact unless it has a real usable image URL.

Check `descriptiveNonRepeating.online_media.media[]`, not just `indexedStructured.online_media_type`. Some units report `Images` without actual media.

Preferred image fallback order:

1. `Screen Image`
2. `High-resolution JPEG`
3. `media.content`
4. `media.thumbnail`

## Known Smithsonian quirks

- `record_ID` is not a safe lookup id for `content/{id}`.
- `online_media_type:Images` is only a hint, not proof.
- Dates, descriptions, and alt text are often sparse.
- `DEMO_KEY` is useful for spot checks but easy to rate-limit.
