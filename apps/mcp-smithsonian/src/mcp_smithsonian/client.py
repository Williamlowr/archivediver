from __future__ import annotations

import os

import httpx

SMITHSONIAN_BASE = "https://api.si.edu/openaccess/api/v1.0"


def _api_key() -> str:
    return os.environ.get("SMITHSONIAN_API_KEY", "DEMO_KEY")


async def search_artifacts_raw(
    query: str,
    limit: int = 5,
    period: str | None = None,
) -> list[dict]:
    """Call Smithsonian search endpoint and return raw rows."""
    # online_media_type:Images biases toward image-bearing units (e.g. NASM).
    # Some units (SIL, SIA) tag items with this despite having no actual media;
    # the normalizer drops those at the image-validation step.
    base = f'{query} online_media_type:Images'
    q = f'{base} date:"{period}"' if period else base

    # Fetch extra rows to buffer for units (like SIL) that tag items as having
    # images but have no actual online_media. After normalization the caller
    # trims to the requested limit.
    fetch_rows = min(max(limit, 1) * 4, 50)

    params = {
        "q": q,
        "rows": str(fetch_rows),
        "start": "0",
        "sort": "relevancy",
        "type": "edanmdm",
        "row_group": "objects",
        "api_key": _api_key(),
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{SMITHSONIAN_BASE}/search", params=params)
        response.raise_for_status()
        data = response.json()

    return data.get("response", {}).get("rows") or []
