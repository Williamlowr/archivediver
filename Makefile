.PHONY: dev dev-web dev-api dev-mcp test test-web test-api test-mcp lint lint-web lint-api lint-mcp format

dev:
	@echo "Starting all services (placeholder scaffold)"
	@echo "Run in separate terminals:"
	@echo "  make dev-web"
	@echo "  make dev-api"
	@echo "  make dev-mcp"

dev-web:
	npm run dev --prefix apps/web

dev-api:
	@echo "API scaffold: add app entrypoint, then run uvicorn archivediver_api.main:app --reload --port 8000"

dev-mcp:
	@echo "MCP scaffold: add app entrypoint, then run python -m mcp_smithsonian"

test: test-web test-api test-mcp

test-web:
	npm run test --prefix apps/web

test-api:
	python -m pytest apps/api

test-mcp:
	python -m pytest apps/mcp-smithsonian

lint: lint-web lint-api lint-mcp

lint-web:
	npm run lint --prefix apps/web

lint-api:
	python -m ruff check apps/api

lint-mcp:
	python -m ruff check apps/mcp-smithsonian

format:
	@echo "Formatting scaffold:"
	@echo "  npx prettier --write apps/web"
	@echo "  python -m ruff format apps/api apps/mcp-smithsonian"
