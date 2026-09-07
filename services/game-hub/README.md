# Game Hub service

This directory contains the first runnable Game Hub foundation.

## What exists now

- FastAPI control-plane API
- PostgreSQL persistence
- canonical games, provider accounts, entitlements, devices, installations, and launch targets
- provider capability registry
- API-key protection for `/api/v1/*`
- allow-listed server-to-device launch dispatch
- Windows launch-agent skeleton with dry-run enabled by default

## Start the server

1. Copy `.env.example` to `.env`.
2. Replace the example secrets.
3. Set `GAMEHUB_ALLOWED_AGENT_HOSTS` only when a device agent is ready.
4. Run:

```bash
docker compose up -d --build
```

Health check:

```bash
curl http://SERVER:8787/health
```

List providers:

```bash
curl -H "X-GameHub-Key: YOUR_KEY" http://SERVER:8787/api/v1/providers
```

## First useful workflow

Create a game, register a provider account, attach an entitlement, register a device, then create a launch target. The first Windows agent accepts bounded URI-launch requests and defaults to dry-run mode.

Game Hub is intentionally not exposed publicly yet. Keep it on trusted LAN/VPN networks until authentication, authorization, audit logging, and per-device credentials are expanded.

## Directory layout

```text
services/game-hub/
├── app/                    # API service
├── agents/windows/         # first device-agent skeleton
├── docker-compose.yml
└── .env.example
```

See `docs/GAME_HUB.md` for the architecture and phased build plan.
