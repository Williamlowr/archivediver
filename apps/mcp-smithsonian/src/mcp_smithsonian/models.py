from __future__ import annotations

from pydantic import BaseModel


class ArtifactResult(BaseModel):
    id: str
    record_id: str = ""
    title: str
    date_display: str = ""
    date_indexed: list[str] = []
    creator_display: str = ""
    description: str = ""
    object_type: str = ""
    unit_code: str = ""
    unit_name: str = ""
    source_url: str = ""
    image_url: str = ""
    thumbnail_url: str = ""
    image_download_url: str = ""
    image_alt: str = ""
    rights: str = ""
    subject_tags: list[str] = []
    place_tags: list[str] = []


class ItemMediaResult(BaseModel):
    item_id: str
    title: str = ""
    creator_display: str = ""
    image_url: str = ""
    thumbnail_url: str = ""
    image_download_url: str = ""
    image_alt: str = ""
    source_url: str = ""
    rights: str = ""
    unit_code: str = ""
    unit_name: str = ""
