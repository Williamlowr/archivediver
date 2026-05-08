from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient


async def run_agent(
    topic: str,
    period: str | None,
    count: int,
    chat_model: Any = None,
    mcp_url: str = "http://localhost:9000/sse",
) -> tuple[list[dict], list[dict]]:
    """Run one tool-use round against the MCP server.

    Returns (artifacts, tool_calls) where artifacts is a list of raw dicts
    from the search_artifacts tool output and tool_calls is a list of
    ToolCallRecord-compatible dicts for the dev trace.
    """
    if chat_model is None:
        from langchain_anthropic import ChatAnthropic

        chat_model = ChatAnthropic(model="claude-haiku-4-5-20251001")

    mcp_client = MultiServerMCPClient(
        {"smithsonian": {"url": mcp_url, "transport": "sse"}}
    )
    tools = await mcp_client.get_tools()
    model_with_tools = chat_model.bind_tools(tools)

    period_clause = f" from the {period}" if period else ""
    prompt = (
        f"Search for {count} artifacts about {topic}{period_clause} "
        f"and return them using the search_artifacts tool."
    )
    messages = [HumanMessage(content=prompt)]
    response = await model_with_tools.ainvoke(messages)

    artifacts: list[dict] = []
    tool_calls: list[dict] = []

    if not response.tool_calls:
        return artifacts, tool_calls

    messages.append(response)

    for tc in response.tool_calls:
        tool_name = tc["name"]
        tool_args = tc["args"]
        tool_id = tc["id"]

        tool_fn = next((t for t in tools if t.name == tool_name), None)
        if tool_fn is None:
            continue

        raw_result = await tool_fn.ainvoke(tool_args)
        messages.append(
            ToolMessage(content=str(raw_result), tool_call_id=tool_id)
        )

        try:
            rows = json.loads(raw_result)
            artifacts.extend(rows)
            tool_calls.append(
                {
                    "tool": tool_name,
                    "input": tool_args if isinstance(tool_args, dict) else {},
                    "output_count": len(rows),
                }
            )
        except (json.JSONDecodeError, TypeError):
            tool_calls.append(
                {"tool": tool_name, "input": {}, "output_count": 0}
            )

    return artifacts, tool_calls
