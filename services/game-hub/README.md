# Game Hub service

This directory contains the first runnable Game Hub foundation and the first modern-library bridge.

## What exists now

- FastAPI control-plane API
- PostgreSQL persistence
- canonical games, provider accounts, entitlements, devices, installations, and launch targets
- provider capability registry
- API-key protection for `/api/v1/*`
- allow-listed server-to-device launch dispatch
- Windows launch agent with dry-run enabled by default
- Playnite 10 sync plugin source
- bulk `POST /api/v1/import/playnite` ingestion
- Playnite imports for provider/store IDs, platforms, installed state, playtime, play count, last activity, favorites, and release year
- exact `playnite://playnite/start/<database-guid>` launch targets for installed Playnite games

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

1. Deploy the server on a test host.
2. Run the Windows agent on the main gaming PC with dry-run enabled.
3. Build/install `playnite-plugin/` on Playnite 10.
4. Configure the plugin's `gamehub.json`.
5. Sync the Playnite library.
6. Verify `/api/v1/games`, `/api/v1/entitlements`, `/api/v1/installations`, and `/api/v1/launch-targets`.
7. Dispatch one installed game's Playnite launch target and verify the exact URI in dry-run mode before enabling real launch.

Playnite-derived access is intentionally classified as `library_access` until direct platform connectors can distinguish purchased, redeemed, subscription, and other entitlement types.

Game Hub is intentionally not exposed publicly yet. Keep it on trusted LAN/VPN networks until authentication, authorization, audit logging, and per-device credentials are expanded.

## Directory layout

```text
services/game-hub/
├── app/                    # API service
├── agents/windows/         # bounded Windows launcher agent
├── playnite-plugin/        # Playnite 10 library sync bridge
├── docker-compose.yml
└── .env.example
```

See `docs/GAME_HUB.md` for the architecture and phased build plan.
