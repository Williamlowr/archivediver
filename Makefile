.PHONY: help \
        install install-web install-api install-mcp \
        dev dev-web dev-api dev-mcp \
        test test-web test-api test-mcp \
        lint lint-web lint-api lint-mcp \
        format format-web format-py \
        build clean

ifneq (,$(wildcard .env))
include .env
export
endif

WEB_PORT ?= 5173
API_PORT ?= 8000
MCP_PORT ?= 9000
MCP_HOST ?= 127.0.0.1
API_HOST ?= 127.0.0.1

PYTHON ?= python

help:
	@echo "ArchiveDiver Makefile targets:"
	@echo "  install         Install all workspace deps (web + api[dev] + mcp[dev])"
	@echo "  dev             Run web, api, and mcp concurrently"
	@echo "  dev-web         Run the Vite dev server (port $(WEB_PORT))"
	@echo "  dev-api         Run FastAPI with reload (port $(API_PORT))"
	@echo "  dev-mcp         Run the MCP Smithsonian server (port $(MCP_PORT))"
	@echo "  test            Run all test suites"
	@echo "  lint            Run all linters"
	@echo "  format          Format web (Prettier) and Python (Ruff)"
	@echo "  build           Build the web app"
	@echo "  clean           Remove build and cache artifacts"

install: install-web install-api install-mcp

install-web:
	npm install --prefix apps/web

install-api:
	$(PYTHON) -m pip install -e "apps/api[dev]"

install-mcp:
	$(PYTHON) -m pip install -e "apps/mcp-smithsonian[dev]"

dev:
	@echo "Starting web (:$(WEB_PORT)), api (:$(API_PORT)), mcp (:$(MCP_PORT)). Ctrl-C to stop."
	@trap 'kill 0' INT TERM EXIT; \
		$(MAKE) -s dev-mcp & \
		$(MAKE) -s dev-api & \
		$(MAKE) -s dev-web & \
		wait

dev-web:
	npm run dev --prefix apps/web

dev-api:
	$(PYTHON) -m uvicorn archivediver_api.main:app \
		--reload --host $(API_HOST) --port $(API_PORT)

dev-mcp:
	MCP_HOST=$(MCP_HOST) MCP_PORT=$(MCP_PORT) $(PYTHON) -m mcp_smithsonian.server

test: test-web test-api test-mcp

test-web:
	npm run test --prefix apps/web

test-api:
	$(PYTHON) -m pytest apps/api

test-mcp:
	$(PYTHON) -m pytest apps/mcp-smithsonian

lint: lint-web lint-api lint-mcp

lint-web:
	npm run lint --prefix apps/web

lint-api:
	$(PYTHON) -m ruff check apps/api

lint-mcp:
	$(PYTHON) -m ruff check apps/mcp-smithsonian

format: format-web format-py

format-web:
	npx --prefix apps/web prettier --write apps/web

format-py:
	$(PYTHON) -m ruff format apps/api apps/mcp-smithsonian

build:
	npm run build --prefix apps/web

clean:
	rm -rf apps/web/dist apps/web/node_modules/.vite
	find apps -type d -name __pycache__ -prune -exec rm -rf {} +
	find apps -type d -name .pytest_cache -prune -exec rm -rf {} +
	find apps -type d -name .ruff_cache -prune -exec rm -rf {} +
