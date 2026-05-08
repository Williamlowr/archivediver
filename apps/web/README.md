# Web App

React + Vite frontend for ArchiveDiver.

## Owns

- topic, period, and artifact-count inputs
- exhibit rendering
- backend HTTP requests only

## Run

- `npm install --prefix apps/web`
- `npm run dev --prefix apps/web`

## Env

- `VITE_USE_MOCK=true`: use mock exhibit data
- `VITE_API_BASE_URL`: optional absolute API base URL
- `VITE_API_PROXY_TARGET`: Vite dev proxy target, default `http://127.0.0.1:8000`

## Commands

- `npm run test --prefix apps/web`
- `npm run build --prefix apps/web`
- `npm run lint --prefix apps/web`
