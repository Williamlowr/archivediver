# Time: 10:40 AM 05/08/2026
Tool: Cursor
Task: Created main AI rule files (AGENTS.md, CLAUDE.md, Cursor rules)
Prompt: 
create three main ai rule files (CLAUDE.md, cursor archivediver.mdc, and AGENTS.md) based on the project brief

claude and cursor .mdc rule files should point to the agents.md file

agents.md should outline:
style rules- no emojis, no em dashes, keep responses/documentation concise and practical for humans to understand, avoid corporate filler language

prompt logging rule-
after I send a prompt, add an entry to /docs/prompt-log.md logging the timestamp, the ai tool I'm using (cursor/codex/claude), and a short summary. I will put the actual prompt in this .md, the agents should not copy the prompt over
the entries should be formatted as:
Time: HH:MM DD/MM/YYYY
Tool: Cursor | Claude Code | Codex
Task: Short summary

time command should be
date +"%I:%M %p %d/%m/%Y"

project scope rules-
no auth, persistence, or payments
keep the smithsonian api secure
dont add agent logic or expose api keys in frontend

work rules-
plan before implementing
preserve file structure unless asked to change it
after changes, provide a summary of what was changed
use test suites to verify as we go

# Time: 10:44 AM 05/08/2026
Tool: Cursor (Opus)
Task: Drafted docs/implementation-brief.md from project-brief.md
Prompt: 
read project-brief.md and create a minimal implementation-brief.md outlining:
-monorepo structure as outlined in project-brief.md
-context map outlining subrepo responsibilities and boundaries
-api/data flow
-path to MVP/vertical slice test in two stages: api contract/minimal frontend ui wiring (one MCP tool, test langchain endpoint, basic frontend)
-risks/mitigations
-acceptance criteria 
-what’s purposely out of scope
-any other insights from project-brief.md

Follow agents.md

# Time: 10:51 AM 05/08/2026
Tool: Cursor (Codex)
Task: Implemented repo scaffolding for docs, env template, dependencies, and root scripts
Prompt: 
reference the implementation-brief.md and project-brief.md and plan for scaffolding the repo; include placeholder readmes, an env example with anthropic and smithsonian keys, dependency files, package scripts, a root readme

Follow agents.md

# Time: 10:55 AM 05/08/2026
Tool: Cursor (Codex)
Task: Added root gitignore for env, Python, Node, and local tooling artifacts
Prompt: 
create gitignore please


# Time: 11:19 AM 05/08/2026
Tool: Codex
Task: Investigated API provider-key fallback change request and validated current workspace contents
Prompt: 
reference the implementation-brief.md and project-brief.md; investigate the smithsonian open access API shape so we can plan implementation
confirm which operations and fields can reliably be used, then create smithsonian-data-notes.md 

we only want artifacts that actually have a usable image, items without an image url should be dropped at the mcp layer, not handed to the llm

Certain museums don’t have images available via api call even when marked with the online_media_type:Images, we need to confirm there’s a real, usable media url

If the api uses different field names, document the field found in the raw response and how we could map it into our normalized schema

optional useful fields could be: subject tags and any raw metadata fields for debugging

The .md should be short and practical, outlining:
-api operations needed
-fields available from search
-fields available for item results
-mapping raw fields to normalized fields
-which fields are unreliable/missing
-how to detect if an item has image/media available, what counts as usable
-how to build/extract the url for artifacts
-which smithsonian museums don’t reliably return usable images
-recommended normalized json shape for the mcp server
-assumptions that need to be tested with a live API check

Goal: understand smithsonian data before planning and building mcp/langchain tools

Keep data from the api separate from llm generated exhibit information
Follow agents.md
Start a file known-limitations.md from findings if needed

# Time: 11:41 AM 05/08/2026
Tool: Claude Code
Task: Implemented Stage 1 vertical slice: mcp-smithsonian server with search_artifacts tool, FastAPI backend with POST /api/exhibit, all four verification steps green, wrote docs/api-contract.md for Stage 2 handoff
Prompt: 
Use the implementation-brief.md, smithsonian-data-notes.md, and project-brief.md to finalize the backend API contract for a vertical slice MVP to make sure things work before we iterate

This is stage one: we need a minimum slice to verify that the LangChain backend, MCP server, and Smithsonian API can actually be connected

No frontend work needed yet, keep the vertical slice small (one MCP tool, one POST /api/exhibit endpoint)

Use mock anthropic until the final test; skip playwright verifications


Use targeted tests, after any failed live check, let’s stop and investigate what’s happening before continuing


Stop when stage 1 is green and create api-contract.md for stage 2 frontend handoff

Verify in order:
MCP unit tests
Smithsonian live test
API test with mocked MCP/LLM
One live backend POST route check


If verification isn’t going as expected, stop and let’s figure it out

# Time: 12:03 PM 05/08/2026
Tool: Codex
Task: Implemented Stage 2 frontend vertical slice MVP with mock-first UI, frontend contract, tests, and one live backend verification
Prompt: 
Use the api-contract.md, implementation-brief.md, smithsonian-data-notes.md, and project-brief.md to create the frontend for a vertical slice MVP to make sure things work before we iterate

This is stage two: we need a minimum slice with minimal ui and polish to just make sure things are working correctly

The style guide for the final ui that you should plan around is: 
Museum like web ui; parchment/paper palette and feel. Off white background, tan/brown accents. Serif historical type text, modern sans serif on exhibit cards
Layout centered, hero at the top that allows the topic, timeline, and artifact count with a build exhibit button that shows Diving… on click
Building an exhibit should show a results panel that looks like a curated exhibit with a grid of artifact cards
Artifacts cards should have an image, caption, and source details
The site should be warm, editorial, polished, and have some reactive ui hover and smooth ux
Lets use occasional tasteful icons from a library for display; not emojis
I will provide a favicon for the tab (svg) and two logos


Turn this into a frontend-contract.md that includes the style guide and outlining how to display the fields from api-contract.md

Also create an assets folder for me to drop the favicon and logo into


Don’t change backend behavior
Build the UI first against a mock API response using api-contract.md
Minimal ui


skip playwright verification


Use targeted tests, after any failed live check, let’s stop and investigate what’s happening before continuing

Verify in order:
Frontend builds
Render mock ui
Wire to real backend, test once


If verification isn’t going as expected, stop and let’s figure it out

# Time: 12:10 PM 05/08/2026
Tool: Cursor
Task: Default web app to live HTTP exhibit API
Prompt: 
the app is functioning but calling fake apollo test data; lets make it live

# Time: 12:16 PM 05/08/2026
Tool: Claude Code
Task: Finalized MCP server tools: renamed search_artifacts to search_items, added get_item_details and get_item_media, input validation, error handling, new tests, updated api-contract.md and agent.py
Prompt: 
Use the implementation-brief.md, smithsonian-data-notes.md, project-brief.md, and architecture.md to plan the finalization of the MCP server tools
Smithsonian-data-notes.md outlines the shape of the data from the api

- search_items - search api by topic and optional filters.
- get_item_details - fetch an item by Smithsonian ID, return normalized source data
- get_item_media - extract image, source, and citation metadata for a specific item

Requirements:
- API key only from env
- Validate inputs
- Normalize responses into stable JSON
- Handle missing fields gracefully
- Return image and source URLs when possible
- No curation logic in the MCP server, only wrapping the API, normalizing data, and exposing safe tools
- Add clear tool descriptions so the LangChain agent can use them reliably
- Include basic error handling
- Include test files

Follow agents.md
Update .mds as needed with changes

# Time: 12:21 PM 05/08/2026
Tool: Claude Code
Task: Stage 2 LLM backend finalization: two-phase agent with structured output, renamed request fields to artifactCount/timePeriod, added LLMExhibitOutput schema enforcement, per-artifact captions, populated dev.limitations, 503 error handling, created frontend-contract.md, updated api-contract.md and implementation-brief.md, 15 API tests green
Prompt: 
Use the implementation-brief.md, smithsonian-data-notes.md, project-brief.md, and architecture.md to plan the finalization of the LangChain LLM backend

Use POST /api/exhibit:
Request body should include topic, artifactCount, and timePeriod (optional)
Then the backend should load the MCP server tools, use the tools to search and inspect API items, select the best artifacts for the topic, and return a structured json response for the frontend to display (keeping source data and LLM generated data separate)

The agent must not invent fields or metadata; if a field is missing, mark as unknown

The backend plan should include request/response schema, a system prompt draft, tool usage strategy, error handling, frontend display requirements, and test files

Enforce the response schema in code, not only in the prompt

Follow agents.md
Create frontend-contract.md outlining the LangChain backend response schema
Update .mds as needed with changes

# Time: 12:48 PM 05/08/2026
Tool: Codex
Task: Finalized Stage 2 frontend exhibit UI, contract-aligned request handling, editorial exhibit layout, targeted tests, and frontend docs
Prompt: 
The MCP and backend are stable/finalized
Use the frontend-contract.md, implementation-brief.md, smithsonian-data-notes.md, project-brief.md, architecture.md, and api-contract.md to plan finalization of the frontend UI
Api-contract.md outlines the expected schema shape that will be returned from the backend; build the frontend ui around displaying these expected fields in an interactable way for the user
frontend-contract.md outlines the style guide and planned ui display for each field

Suggested changes: make the dev info default open
Lets make the site a bit wider, its compact right now
The cards are too narrow and the artifact description is very long right now; lets replace it with the AI generated caption
Overall the artifact cards arent presented great
The whole generated exhibit should feel like a cohesive panel of information built


lets use playwright to look at the site before, plan changes
then skip playwright verification after changes, ill review


I also have 3 assets in there that you should use. Logo1 and 2, both need a bit of cropping cause they have a lot of blank space around them
I also have a favicon for the tab to use


The frontend plan should include page layout, input fields, exhibit result sections, artifact card design, timeline display, source/citation display, loading state, error state, empty/weak results state, collapsible dev results underneath exhibit showing limitations and tool trace, responsive behavior, and frontend files/components to create

Requirements
- The frontend should not call the api directly and should not contain agent logic
- Render source metadata separately from generated captions
- Keep the UI polished and simple

Follow agents.md
Update .mds as needed with changes

# Time: 12:54 PM 05/08/2026
Tool: Claude Code
Task: Audited and finalized repo docs, shortened readmes and contracts, and added deployment and handoff guides
Prompt: 
Finalize all the docs in the repo as needed, audit all docs and ensure they’re concise and understandable for a human, minimal fluff or jargon:
Finalize known-limitations.md, then create a deployment.md and handoff.md file outlining how to deploy the app, and dev handoff. Finalize the readmes as needed. Update the other .mds if anything is outdated

Follow agents.md

concise and understandable is better than too much information I think

# Time: 1:05 PM 05/08/2026
Tool: Claude Code
Task: Fixed 8 frontend UI layout bugs
Prompt: 
a lot of things need improvement on the frontend

findings:
Build a small digital exhibit from a historical thread. is on like 10 lines
Time Period needs to be on one line, not two
the top bar looks really bad (the title is very small, the logo is small and can barely be seen, 

Smithsonian facts, generated captions, one readable exhibit panel. that part looks horrible and makes no sense
Apollo: Art and Myth from Renaissance to Space Age this exhibit title is on 4 lines
the artifacts label is under the first artifact
artifact one is gigantic and all the other ones are extremely thin and they mess up the photo entirely

this section needs better presentation:
Date
Creator
Museum
Object type
Rights

# Time: 1:16 PM 05/08/2026
Tool: Claude Code
Task: Fixed image sizing bug
Prompt: 
the images are cut off right now; the box needs to fit around the image; use auto sizing and contain