from __future__ import annotations

from pydantic import BaseModel, Field


class ExhibitRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    timePeriod: str | None = None
    artifactCount: int = Field(default=5, ge=1, le=10)


class ArtifactCaption(BaseModel):
    artifact_id: str
    caption: str


class LLMExhibitOutput(BaseModel):
    title: str
    intro: str
    captions: list[ArtifactCaption]
    limitations: list[str]


class ArtifactOut(BaseModel):
    id: str
    title: str
    caption: str = ""
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
    image_alt: str = ""
    rights: str = ""
    subject_tags: list[str] = []
    place_tags: list[str] = []


class ToolCallRecord(BaseModel):
    tool: str
    input: dict
    output_count: int


class DevInfo(BaseModel):
    tool_calls: list[ToolCallRecord] = []
    limitations: list[str] = []
    notices: list[str] = []


class TimelineEntry(BaseModel):
    date: str
    label: str


class ExhibitResponse(BaseModel):
    title: str
    intro: str
    artifacts: list[ArtifactOut]
    timeline: list[TimelineEntry]
    dev: DevInfo
