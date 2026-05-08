from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

from archivediver_api.models import LLMExhibitOutput

_EXHIBIT_SYSTEM_PROMPT = """\
You are a museum curator writing content for a Smithsonian digital exhibit.

Rules:
- Base the title and intro only on what the artifacts actually show.
- Write one caption per artifact (1-2 sentences). Use only fields present in the artifact data.
- If creator, date, or description is missing or empty, write "unknown" in the caption rather than guessing.
- Limitations must note concrete gaps: sparse results, missing dates, empty descriptions, few artifacts found.
- Be concise. No em dashes. No emojis.\
"""


def _fallback_output(topic: str, artifact_count: int, reason: str) -> LLMExhibitOutput:
    return LLMExhibitOutput(
        title=f"Exhibit: {topic.title()}",
        intro=f"A collection of {artifact_count} artifact{'s' if artifact_count != 1 else ''} exploring {topic}.",
        captions=[],
        limitations=[reason],
    )


def _detect_period_fallback(time_period: str | None, tool_calls: list[dict]) -> str | None:
    if not time_period:
        return None
    search_calls = [tc for tc in tool_calls if tc["tool"] == "search_items"]
    period_miss = any(
        tc["input"].get("period") and tc["output_count"] == 0 for tc in search_calls
    )
    if not period_miss:
        return None
    broad_retry = any(not tc["input"].get("period") for tc in search_calls)
    if broad_retry:
        return f'No results found for time period "{time_period}". Showing results across all time periods.'
    return None


async def _invoke_tool(tool_map: dict, name: str, args: dict) -> tuple[Any, dict]:
    """Invoke a named MCP tool and return (parsed_result, tool_call_record)."""
    fn = tool_map.get(name)
    if fn is None:
        return None, {"tool": name, "input": args, "output_count": 0}
    try:
        raw = await fn.ainvoke(args)
        parsed = json.loads(raw)
        count = len(parsed) if isinstance(parsed, list) else (0 if parsed is None else 1)
        return parsed, {"tool": name, "input": args, "output_count": count}
    except (json.JSONDecodeError, TypeError, Exception):
        return None, {"tool": name, "input": args, "output_count": 0}


async def run_agent(
    topic: str,
    time_period: str | None,
    artifact_count: int,
    chat_model: Any = None,
    mcp_url: str = "http://localhost:9000/sse",
) -> tuple[list[dict], list[dict], LLMExhibitOutput, list[str]]:
    """Two-phase agent: code-driven MCP tool calls, then LLM exhibit generation."""
    if chat_model is None:
        from langchain_anthropic import ChatAnthropic
        chat_model = ChatAnthropic(model="claude-haiku-4-5-20251001")

    mcp_client = MultiServerMCPClient(
        {"smithsonian": {"url": mcp_url, "transport": "sse"}}
    )
    tools = await mcp_client.get_tools()
    tool_map = {t.name: t for t in tools}

    artifacts: list[dict] = []
    tool_calls: list[dict] = []

    # Phase 1a: search
    search_args: dict = {"query": topic, "limit": artifact_count}
    if time_period:
        search_args["period"] = time_period
    search_result, search_record = await _invoke_tool(tool_map, "search_items", search_args)
    tool_calls.append(search_record)

    if isinstance(search_result, list):
        artifacts = search_result

    if not artifacts:
        return artifacts, tool_calls, _fallback_output(topic, 0, "No image-bearing artifacts found for this topic."), []

    # Phase 1b: enrich each artifact with details and media
    for i, artifact in enumerate(artifacts):
        item_id = artifact.get("id", "")
        if not item_id:
            continue

        details, details_record = await _invoke_tool(tool_map, "get_item_details", {"item_id": item_id})
        tool_calls.append(details_record)
        if isinstance(details, dict) and "id" in details:
            artifacts[i] = {**artifact, **details}

        media, media_record = await _invoke_tool(tool_map, "get_item_media", {"item_id": item_id})
        tool_calls.append(media_record)
        if isinstance(media, dict):
            artifacts[i] = {**artifacts[i], **media}

    # Phase 2: LLM generates title, intro, captions, limitations
    artifact_summary = json.dumps(
        [
            {
                "id": a.get("id", ""),
                "title": a.get("title", ""),
                "date_display": a.get("date_display", ""),
                "creator_display": a.get("creator_display", ""),
                "description": a.get("description", ""),
                "object_type": a.get("object_type", ""),
                "unit_name": a.get("unit_name", ""),
            }
            for a in artifacts
        ],
        indent=2,
    )

    exhibit_prompt = (
        f"Topic: {topic}\n"
        f"Period filter: {time_period or 'none'}\n"
        f"Artifact count returned: {len(artifacts)}\n\n"
        f"Artifacts:\n{artifact_summary}\n\n"
        "Generate the exhibit title, intro, one caption per artifact (keyed by artifact id), "
        "and a list of limitations."
    )

    structured_model = chat_model.with_structured_output(LLMExhibitOutput)
    try:
        llm_output: LLMExhibitOutput = await structured_model.ainvoke(
            [
                SystemMessage(content=_EXHIBIT_SYSTEM_PROMPT),
                HumanMessage(content=exhibit_prompt),
            ]
        )
    except Exception:
        llm_output = _fallback_output(
            topic,
            len(artifacts),
            "Exhibit content generation failed; using fallback template.",
        )

    notices: list[str] = []
    fallback_notice = _detect_period_fallback(time_period, tool_calls)
    if fallback_notice:
        notices.append(fallback_notice)

    return artifacts, tool_calls, llm_output, notices
