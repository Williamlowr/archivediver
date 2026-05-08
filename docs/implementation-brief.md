# ArchiveDiver Implementation Brief

A minimal plan for delivering the prototype described in `project-brief.md`. Optimized for a thin vertical slice first, then iteration.

## 1. Monorepo Structure

```
archivediver/
  apps/
    web/                 React + Vite + TypeScript, Tailwind, copy.ts for UI text
    api/                 Python FastAPI + LangChain agent
    mcp-smithsonian/     Python MCP server wrapping the Smithsonian Open Access API
  docs/                  project-brief.md, implementation-brief.md, prompt-log.md, etc.
  docker-compose.yml     Local orchestration of the three services
  README.md
  .env.example           Documents required env vars (no secrets committed)
```

Each subrepo owns its own dependencies, tests, and Dockerfile. No shared package layer in the MVP.

## 2. Context Map (Responsibilities and Boundaries)

| Service (Path)            | Owns                                                                 | Does not own                                  | Talks to                          |
| ------------------------- | -------------------------------------------------------------------- | --------------------------------------------- | --------------------------------- |
| frontend (`apps/web`)     | UI, form state, rendering exhibit, displaying tool-call trace        | API keys, agent logic, Smithsonian calls       | backend (HTTP/JSON only)          |
| backend (`apps/api`)      | LangChain agent loop, prompt templates, exhibit assembly, MCP client | Smithsonian HTTP details, raw API parsing      | frontend (HTTP), mcp-server (MCP) |
| mcp-server (`apps/mcp-smithsonian`) | Smithsonian REST calls, response normalization, MCP tool surface      | LLM logic, exhibit generation, UI concerns    | Smithsonian Open Access API       |

Hard rules:
- Smithsonian API key lives only in `mcp-server` env.
- Frontend never imports agent code and never calls Smithsonian.
- `backend` treats `mcp-server` as the only source of artifact data.

## 3. API and Data Flow

```
[user] -> [frontend form]
        -> POST /api/exhibit  (topic, period?, count<=10)
[backend FastAPI]
        -> LangChain agent
              -> MCP tool call: search_artifacts(query, period?, limit)
[mcp-server]
        -> Smithsonian Open Access REST
        -> normalize hits to artifact schema
        <- structured artifacts
[backend]
        -> agent composes title, intro, captions, timeline
        <- exhibit JSON + tool_trace
[frontend]
        <- renders ExhibitHeader, ArtifactCards, Timeline, DevDetails
```

Artifact schema (from Smithsonian normalization):
`id, title, date, creator, description, object_type, unit_name, image_url?, source_url, rights?`

Exhibit response shape:
`{ title, intro, artifacts[], timeline[], dev: { tool_calls[], limitations[] } }`

## 4. Path to MVP (Two Stages)

### Stage 1: API contract slice (no UI)

Goal: prove the backend-to-MCP-to-Smithsonian path end-to-end.

- mcp-server: implement one tool, `search_artifacts(query, limit, period?)`. Return normalized artifacts.
- backend: minimal `/api/exhibit` endpoint. LangChain agent with that single tool bound. Hardcoded prompt for title and intro. Pass through artifacts. Include `tool_calls` in response.
- Contract test: `curl -X POST /api/exhibit -d '{"topic":"apollo program","count":3}'` returns valid exhibit JSON with at least one artifact and a tool-call trace.
- Done when: backend test hits a real (or recorded) Smithsonian response via the MCP tool and produces the documented JSON shape.

### Stage 2: LLM backend finalization + frontend wiring

Goal: LLM generates exhibit content; frontend renders a live exhibit.

Backend (complete):
- Request fields renamed: `count` -> `artifactCount`, `period` -> `timePeriod`.
- Two-phase agent: Phase 1 calls `search_artifacts` via MCP. Phase 2 uses `with_structured_output(LLMExhibitOutput)` to generate title, intro, per-artifact captions, and limitations.
- `ArtifactOut` gains a `caption` field (LLM-generated). All other artifact fields are unchanged Smithsonian source data.
- `dev.limitations` now populated by the LLM with observed result gaps.
- Schema enforced in code via Pydantic `LLMExhibitOutput`, not only in the prompt.
- 503 errors returned on MCP or LLM failure.
- See `docs/frontend-contract.md` for the full response schema and frontend display requirements.

Frontend (pending):
- Form: topic input, optional `timePeriod` chips, `artifactCount` selector (1 to 10).
- POST to backend, render: header (title, intro), artifact cards (image, title, caption, date, creator, source link), simple timeline, DevDetails panel (tool-call trace, limitations).
- copy.ts for all UI strings.
- Done when: a user can type a topic, submit, and see a rendered exhibit using live backend data, with the dev panel showing tool calls and LLM-observed limitations.

## 5. Risks and Mitigations

| Risk                                                       | Mitigation                                                                 |
| ---------------------------------------------------------- | -------------------------------------------------------------------------- |
| Smithsonian results sparse or noisy for some queries        | Surface limitations in DevDetails. Cap count at 10. Allow empty timeline.  |
| LangChain tool-calling instability across model versions    | Pin model and LangChain versions in `backend/requirements.txt`.            |
| MCP transport choice churn (stdio vs HTTP)                  | Start with stdio in dev via subprocess; abstract behind one client module. |
| API key leakage                                             | Key only in `mcp-server` container env. `.env.example` lists var names only.|
| LLM cost or latency spikes during dev                       | Cache last response in dev; small default count; add a fixture mode.       |
| Image URLs missing or hotlink-restricted                    | Render placeholder; never block the card on image failure.                 |
| Scope creep into auth, persistence, sharing                 | Enforce out-of-scope list below in PR review.                              |

## 6. Acceptance Criteria

The MVP is accepted when all of the following are true:

1. A user can submit a topic (and optional period, count up to 10) from the frontend.
2. The backend returns a valid exhibit JSON containing title, intro, artifacts, timeline, and a dev section.
3. Artifacts originate from the Smithsonian Open Access API via the MCP server (verified by tool trace).
4. The Smithsonian API key is not present in any frontend bundle or response payload.
5. The DevDetails panel shows at least one tool call and any known limitations of the result set.
6. `docker-compose up` brings up all three services locally with a documented `.env` setup.
7. README documents how to run, test, and configure the project.

## 7. Out of Scope (MVP)

- Authentication, accounts, sessions.
- Persistence: no database, no saved exhibits, no history.
- Payments or quotas.
- Sharing, export (PDF, image), or social features.
- Multi-source aggregation beyond Smithsonian.
- Production hardening: rate limiting, observability stack, CDN, SSR.
- Frontend agent logic or direct Smithsonian calls from the browser.
- Internationalization.

## 8. Insights from the Project Brief

- The "clean agentic architecture" goal implies the MCP boundary is load-bearing. Treat it as a contract, not a convenience wrapper. Keep normalization logic in `mcp-server`, keep narrative logic in `backend`.
- The DevDetails section is a first-class deliverable, not a debug afterthought. It is how the agentic behavior becomes legible to the user.
- The 10-artifact cap is a useful forcing function: it bounds LLM context, latency, and Smithsonian rate-limit exposure for the prototype.
- Copy in `copy.ts` plus the no-emoji and no-em-dash rules suggest editorial tone matters; build the copy file early so review is centralized.
- `prompt-log.md` and handoff notes imply this repo will be picked up by other agents or contributors. Favor explicit contracts and small, testable modules over clever abstractions.
