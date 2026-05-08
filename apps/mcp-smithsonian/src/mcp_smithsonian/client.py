from __future__ import annotations

import os
import urllib.parse

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
        try:
            response = await client.get(f"{SMITHSONIAN_BASE}/search", params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Smithsonian search error {exc.response.status_code} for query {query!r}"
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"Network error during Smithsonian search: {exc}") from exc
        data = response.json()

    return data.get("response", {}).get("rows") or []


async def get_item_raw(item_id: str) -> dict:
    """Fetch one item from content/{id}. Raises RuntimeError on HTTP errors."""
    encoded = urllib.parse.quote(item_id, safe="")
    params = {"api_key": _api_key()}

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{SMITHSONIAN_BASE}/content/{encoded}", params=params
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Smithsonian API error {exc.response.status_code} for item {item_id!r}"
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"Network error fetching item {item_id!r}: {exc}") from exc

    return response.json().get("response", {})
