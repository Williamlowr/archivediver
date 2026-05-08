# Known Limitations

## Smithsonian Open Access API
- `indexedStructured.online_media_type: Images` is not enough to prove a usable image exists.
- `SIL` was confirmed by live search on 2026-05-08 to return rows marked as `Images` without `descriptiveNonRepeating.online_media`.
- Broad cross-unit spot checks were cut short by `OVER_RATE_LIMIT` on `DEMO_KEY`.
- Untested units must stay marked as unverified, not blacklisted.

## Handling rule for this repo
- Drop image-less artifacts in the MCP layer.
- Do not hand artifacts without a real usable media URL to the backend or LLM.
- Do not rely on frontend placeholders to cover Smithsonian media gaps.
