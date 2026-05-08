# ArchiveDiver
## Project Overview
A simple rapid prototype that generates a digital exhibit from a user input topic using the Smithsonian Open Access API.

## Core User Flow
A user should be able to enter a historical topic/keyword, optional time period, and number of artifacts (10 max)

The app will use an LLM backend using LangChain to tool call an MCP server that wraps the Smithsonian public REST API.

Output should be an interactive mini-exhibit for the user

## User Inputs
- Historical topic or keyword
- Optional time period
- Number of artifacts, maximum 10

## Expected Output
The generated exhibit should include:
- Exhibit title
- Short introduction
- Artifact cards
- Source metadata
- Generated captions
- Simple timeline
- Dev info section showing result limitations and tool-call trace

## Expected Smithsonian format:
- artifact titles
- dates
- creators or makers
- descriptions
- object types
- museum or Smithsonian unit names
- image or thumbnail URLs when available
- source URLs
- rights, license, or usage text when available

## Goal
The goal is clean agentic architecture going from Smithsonian public REST API, to an MCP wrapper service, that gets called by a LangChain backend, and presented as a simple frontend experience

## Agent Rules
Agents working in the repo should document architecture, setup, deployment considerations, and handoff notes
We will also be using a prompt-log.md file to log prompts

### Format

Time: HH:MM DD/MM/YYYY
Tool: Cursor | Claude Code | Codex
Task: Short summary of the requested work

Use following for time:
date +"%I:%M %p %d/%m/%Y"

### API
Keep the Smithsonian key server side; don't expose API key In the frontend or call Smithsonian API in the frontend

## Planned structure:
archivediver/
    frontend/ 
        React + Vite + TypeScript
        Tailwind CSS
        Copy.ts for UI text
        Rules: no emojis, no em dashes
    backend/
        Python FastAPI
        LangChain agent
    mcp-server/
        Python MCP server wrapping Smithsonian Public API
    docs/
      project-brief.md
      prompt-log.md
      etc
    docker-compose.yml
    README.md
    .env.example