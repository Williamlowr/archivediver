from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
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

app = FastAPI(title="ArchiveDiver API", version="0.2.0")

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
    try:
        raw_artifacts, raw_tool_calls, llm_output = await run_agent(
            topic=req.topic,
            time_period=req.timePeriod,
            artifact_count=req.artifactCount,
            mcp_url=MCP_URL,
        )
    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail="MCP server unavailable") from exc
    except Exception as exc:
        msg = str(exc).lower()
        if "connect" in msg or "mcp" in msg:
            raise HTTPException(status_code=503, detail="MCP server unavailable") from exc
        raise HTTPException(status_code=503, detail="LLM unavailable") from exc

    caption_map = {c.artifact_id: c.caption for c in llm_output.captions}

    artifacts: list[ArtifactOut] = []
    for raw in raw_artifacts:
        a = ArtifactOut(**raw)
        a.caption = caption_map.get(a.id, "")
        artifacts.append(a)

    timeline = _build_timeline(artifacts)
    tool_call_records = [ToolCallRecord(**tc) for tc in raw_tool_calls]
    dev = DevInfo(tool_calls=tool_call_records, limitations=llm_output.limitations)

    return ExhibitResponse(
        title=llm_output.title,
        intro=llm_output.intro,
        artifacts=artifacts,
        timeline=timeline,
        dev=dev,
    )
