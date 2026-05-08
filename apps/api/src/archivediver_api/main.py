from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from archivediver_api.agent import run_agent
from archivediver_api.models import (
    ArtifactOut,
    DevInfo,
    ExhibitRequest,
    ExhibitResponse,
    TimelineEntry,
    ToolCallRecord,
)

app = FastAPI(title="ArchiveDiver API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

MCP_URL = os.environ.get("MCP_URL", "http://localhost:9000/sse")


def _build_timeline(artifacts: list[ArtifactOut]) -> list[TimelineEntry]:
    entries = []
    for a in artifacts:
        date = a.date_display or (a.date_indexed[0] if a.date_indexed else "")
        if date:
            entries.append(TimelineEntry(date=date, label=a.title))
    entries.sort(key=lambda e: e.date)
    return entries


@app.post("/api/exhibit", response_model=ExhibitResponse)
async def create_exhibit(req: ExhibitRequest) -> ExhibitResponse:
    raw_artifacts, raw_tool_calls = await run_agent(
        topic=req.topic,
        period=req.period,
        count=req.count,
        mcp_url=MCP_URL,
    )

    artifacts = [ArtifactOut(**a) for a in raw_artifacts]

    period_clause = f" from the {req.period}" if req.period else ""
    title = f"Exhibit: {req.topic.title()}"
    intro = (
        f"A collection of {len(artifacts)} artifact"
        f"{'s' if len(artifacts) != 1 else ''} exploring "
        f"{req.topic}{period_clause}."
    )

    timeline = _build_timeline(artifacts)

    tool_call_records = [ToolCallRecord(**tc) for tc in raw_tool_calls]
    dev = DevInfo(tool_calls=tool_call_records)

    return ExhibitResponse(
        title=title,
        intro=intro,
        artifacts=artifacts,
        timeline=timeline,
        dev=dev,
    )
