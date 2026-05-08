from __future__ import annotations

from mcp_smithsonian.models import ArtifactResult


def _first_usable_media(
    media_list: list,
) -> tuple[str, str, str, str] | None:
    """Scan media entries for first one with a usable image URL.

    Returns (image_url, thumbnail_url, download_url, alt) or None.
    Fallback chain per entry: Screen Image -> High-resolution JPEG -> media.content -> media.thumbnail
    """
    for media in media_list:
        if not isinstance(media, dict):
            continue

        resources = media.get("resources") or []
        screen_url = ""
        hires_url = ""
        thumb_url = ""

        for r in resources:
            if not isinstance(r, dict):
                continue
            label = r.get("label", "")
            url = r.get("url", "")
            if not url:
                continue
            if label == "Screen Image" and not screen_url:
                screen_url = url
            elif label == "High-resolution JPEG" and not hires_url:
                hires_url = url
            elif label == "Thumbnail Image" and not thumb_url:
                thumb_url = url

        image_url = (
            screen_url
            or hires_url
            or media.get("content", "")
            or media.get("thumbnail", "")
        )

        if not image_url:
            continue

        thumbnail_url = thumb_url or media.get("thumbnail", "")
        alt = media.get("altTextAccessibility", "")
        return image_url, thumbnail_url, hires_url, alt

    return None


def normalize_row(row: dict) -> ArtifactResult | None:
    """Normalize one Smithsonian search row to ArtifactResult.

    Returns None if the row has no usable image.
    """
    content = row.get("content") or {}
    dnr = content.get("descriptiveNonRepeating") or {}
    indexed = content.get("indexedStructured") or {}
    freetext = content.get("freetext") or {}

    online_media = dnr.get("online_media") or {}
    media_list = online_media.get("media") or []
    media = _first_usable_media(media_list)
    if media is None:
        return None

    image_url, thumbnail_url, download_url, image_alt = media

    artifact_id = row.get("url") or row.get("id", "")
    if not artifact_id:
        return None

    record_id = dnr.get("record_ID", "")

    nested_title = dnr.get("title") or {}
    title = (
        nested_title.get("content", "") if isinstance(nested_title, dict) else ""
    ) or row.get("title", "")

    date_display = ""
    for d in freetext.get("date") or []:
        if isinstance(d, dict) and d.get("content"):
            date_display = d["content"]
            break

    date_indexed = indexed.get("date") or []
    if isinstance(date_indexed, str):
        date_indexed = [date_indexed]

    creator_parts = [
        n["content"]
        for n in (freetext.get("name") or [])
        if isinstance(n, dict) and n.get("content")
    ]
    creator_display = "; ".join(creator_parts)

    description = ""
    for note in freetext.get("notes") or []:
        if isinstance(note, dict) and note.get("label") in (
            "Description",
            "Abstract",
            "Caption",
        ):
            description = note.get("content", "")
            break

    obj_types = indexed.get("object_type") or []
    if not obj_types:
        obj_types = [
            n.get("content", "")
            for n in (freetext.get("objectType") or [])
            if isinstance(n, dict)
        ]
    object_type = "; ".join(t for t in obj_types if t)

    unit_code = dnr.get("unit_code") or row.get("unitCode", "")
    unit_name = dnr.get("data_source", "")
    if not unit_name:
        for ds in freetext.get("dataSource") or []:
            if isinstance(ds, dict) and ds.get("content"):
                unit_name = ds["content"]
                break

    source_url = dnr.get("record_link", "")

    rights = ""
    for r in freetext.get("objectRights") or []:
        if isinstance(r, dict) and r.get("content"):
            rights = r["content"]
            break
    if not rights:
        rights = (dnr.get("metadata_usage") or {}).get("access", "")

    subject_tags = indexed.get("topic") or []
    if isinstance(subject_tags, str):
        subject_tags = [subject_tags]

    place_tags = indexed.get("place") or []
    if isinstance(place_tags, str):
        place_tags = [place_tags]

    if not image_alt:
        image_alt = title

    return ArtifactResult(
        id=artifact_id,
        record_id=record_id,
        title=title,
        date_display=date_display,
        date_indexed=list(date_indexed),
        creator_display=creator_display,
        description=description,
        object_type=object_type,
        unit_code=unit_code,
        unit_name=unit_name,
        source_url=source_url,
        image_url=image_url,
        thumbnail_url=thumbnail_url,
        image_download_url=download_url,
        image_alt=image_alt,
        rights=rights,
        subject_tags=list(subject_tags),
        place_tags=list(place_tags),
    )
