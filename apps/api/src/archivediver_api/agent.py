from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

from archivediver_api.models import ArtifactCaption, LLMExhibitOutput

_SEARCH_SYSTEM_PROMPT = """\
You are a research assistant helping to build a Smithsonian exhibit.
Given a topic, use the available tools as many times as needed to gather relevant artifacts.
You may call search_items with different queries or use get_item_details to enrich results.
Stop calling tools when you have enough artifacts or no further queries would help.\
"""

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
    period_str = ""
    return LLMExhibitOutput(
        title=f"Exhibit: {topic.title()}",
        intro=f"A collection of {artifact_count} artifact{'s' if artifact_count != 1 else ''} exploring {topic}{period_str}.",
        captions=[],
        limitations=[reason],
    )


async def run_agent(
    topic: str,
    time_period: str | None,
    artifact_count: int,
    chat_model: Any = None,
    mcp_url: str = "http://localhost:9000/sse",
) -> tuple[list[dict], list[dict], LLMExhibitOutput]:
    """Run two-phase agent against the MCP server.

    Phase 1: tool call to search_items via MCP.
    Phase 2: structured output generation (title, intro, captions, limitations).

    Returns (artifacts, tool_calls, llm_output).
    """
    if chat_model is None:
        from langchain_anthropic import ChatAnthropic

        chat_model = ChatAnthropic(model="claude-haiku-4-5-20251001")

    # Phase 1: tool call
    mcp_client = MultiServerMCPClient(
        {"smithsonian": {"url": mcp_url, "transport": "sse"}}
    )
    tools = await mcp_client.get_tools()
    model_with_tools = chat_model.bind_tools(tools)

    period_clause = f" from the {time_period}" if time_period else ""
    search_prompt = (
        f"Search for {artifact_count} artifacts about {topic}{period_clause} "
        f"using the search_items tool."
    )
    messages = [
        SystemMessage(content=_SEARCH_SYSTEM_PROMPT),
        HumanMessage(content=search_prompt),
    ]

    artifacts: list[dict] = []
    tool_calls: list[dict] = []

    MAX_TOOL_ROUNDS = 5
    called_any = False

    for _ in range(MAX_TOOL_ROUNDS):
        response = await model_with_tools.ainvoke(messages)
        messages.append(response)

        if not response.tool_calls:
            break

        called_any = True
        for tc in response.tool_calls:
            tool_name = tc["name"]
            tool_args = tc["args"]
            tool_id = tc["id"]

            tool_fn = next((t for t in tools if t.name == tool_name), None)
            if tool_fn is None:
                messages.append(ToolMessage(content="Tool not found.", tool_call_id=tool_id))
                continue

            raw_result = await tool_fn.ainvoke(tool_args)
            messages.append(ToolMessage(content=str(raw_result), tool_call_id=tool_id))

            try:
                parsed = json.loads(raw_result)
                if isinstance(parsed, list):
                    artifacts.extend(parsed)
                    tool_calls.append(
                        {
                            "tool": tool_name,
                            "input": tool_args if isinstance(tool_args, dict) else {},
                            "output_count": len(parsed),
                        }
                    )
                else:
                    tool_calls.append(
                        {
                            "tool": tool_name,
                            "input": tool_args if isinstance(tool_args, dict) else {},
                            "output_count": 1,
                        }
                    )
            except (json.JSONDecodeError, TypeError):
                tool_calls.append({"tool": tool_name, "input": {}, "output_count": 0})

    if not called_any:
        return artifacts, tool_calls, _fallback_output(topic, 0, "Agent did not call search_items.")

    if not artifacts:
        return artifacts, tool_calls, _fallback_output(
            topic, 0, "No image-bearing artifacts found for this topic."
        )

    # Phase 2: structured exhibit generation
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

    return artifacts, tool_calls, llm_output
