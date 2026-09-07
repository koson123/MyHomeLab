# Game Hub

## Goal

Build a self-hosted control plane that knows every game Trevor owns or can currently access, where each copy came from, which devices can run it, and which launch paths are available.

Game Hub is broader than RomM. RomM is one provider for retro/ROM content; modern storefronts, consoles, subscriptions, physical games, and local installations are separate providers feeding one canonical library.

## Core requirements

1. **Scan accounts and libraries** — ingest games from Steam, Epic, GOG, Xbox/Microsoft, PlayStation, Nintendo, EA, Ubisoft, Battle.net, Amazon Games, itch.io, RomM, Playnite, and future providers.
2. **Normalize duplicates** — one canonical game can have many entitlements, platforms, editions, and installations.
3. **Track access type** — distinguish purchased/owned, subscription, physical, free/redeemed, ROM/homebrew, and manual records.
4. **Track devices** — know what is installed, where it is installed, and whether a device has a launch agent.
5. **Launch safely** — dispatch a launch request only to explicitly registered/allow-listed agents; represent unsupported console launch flows honestly as manual or remote-session-only.
6. **Expose an API** — Jarvis, dashboards, Home Assistant, and other automations use Game Hub rather than scraping storefront UIs.
7. **Keep credentials out of Git** — tokens, cookies, API keys, and account sessions live only in protected runtime secret stores.
8. **Do not automate unauthorized acquisition or DRM bypassing** — Game Hub catalogs and launches games Trevor owns/is authorized to use.

## Architecture

```text
Storefronts / consoles / RomM / Playnite / physical catalog
                         |
                  Provider scanners
                         |
                         v
                +-----------------+
                |    Game Hub     |
                | API + database  |
                +--------+--------+
                         |
              +----------+----------+
              |                     |
        Device inventory       Launch orchestrator
              |                     |
              +----------+----------+
                         |
                 Registered agents
                         |
        Gaming PC / future game runner / clients
```

## Canonical data model

### Game
The title-level identity. One record should represent the same game even when Trevor owns it on multiple storefronts/platforms.

Important fields:
- canonical title/key
- optional metadata IDs (IGDB or other future canonical IDs)
- sort title

### Provider account
One connected source such as a Steam account, Playnite bridge, RomM instance, Xbox identity, PlayStation identity, or manual/physical collection.

### Entitlement
A relationship between a game and a provider account.

Examples:
- Cyberpunk 2077 — Steam — `owned`
- Minecraft — Xbox — `owned`
- Forza Horizon — Game Pass — `subscription`
- Zelda cartridge — Nintendo Switch — `physical`
- Pokemon Emerald dump — RomM — `rom`

### Device
A machine or console Game Hub knows about. Devices may expose a trusted launch agent URL.

### Installation
Records that a particular game/provider copy is installed on a device.

### Launch target
Describes a concrete launch route for a game on a device. Capability is explicit:
- `full` — Game Hub can request a direct launch.
- `remote_session` — Game Hub can open/wake/connect to the system but may not select the exact title.
- `manual` — Game Hub can show where/how to play but cannot launch it programmatically.

## Provider strategy

Do not make one brittle mega-scanner. Each provider implements the same ingestion contract and can be replaced independently.

Initial provider list:
- manual / physical
- Playnite bridge
- Steam
- Epic
- GOG
- Xbox/Microsoft
- PlayStation
- Nintendo
- EA
- Ubisoft
- Battle.net
- Amazon Games
- itch.io
- RomM

The preferred early broad-coverage path is a Windows Playnite bridge plus direct APIs where they are more reliable. Direct provider connectors can progressively replace or supplement Playnite data.

## Launch strategy

Game Hub itself runs on Linux and must not pretend it can launch a Windows game locally. Instead, a registered device agent receives a bounded launch request.

Foundation protocol:

```text
POST <device-agent>/v1/launch
Authorization: Bearer <shared-agent-token>

{
  "game_id": 123,
  "title": "Example Game",
  "provider": "steam",
  "launch_ref": "steam://rungameid/12345"
}
```

Security rules:
- Game Hub API requires its own API key.
- Agent calls require a separate bearer token.
- Game Hub refuses dispatch to agent hosts not in `GAMEHUB_ALLOWED_AGENT_HOSTS`.
- Windows agent only opens URI schemes explicitly allowed in its configuration.
- Dry-run mode is the default for the Windows agent until the device is intentionally enabled.
- Future agents should use per-device credentials instead of one shared token.

## Implementation phases

### Phase 0 — foundation (current)
- [x] Define Game Hub architecture and canonical model.
- [x] Add runnable FastAPI + PostgreSQL service skeleton.
- [x] Add provider registry and API endpoints.
- [x] Add device/install/launch-target records.
- [x] Add bounded server-to-agent launch dispatch.
- [x] Add Windows URI-launch agent skeleton with dry-run default.
- [ ] Deploy foundation on a test host and verify database persistence.

### Phase 1 — first real scanner
- [ ] Build a Playnite sync bridge/exporter for broad Windows/storefront coverage.
- [ ] Import games, provider IDs, installed state, playtime where available, and launch references.
- [ ] Add deterministic duplicate matching and a manual merge/override UI/API.
- [ ] Add Steam direct scan as the first official/direct connector.

### Phase 2 — device control
- [ ] Install the agent on Trevor's main gaming PC.
- [ ] Register the PC in Game Hub.
- [ ] Verify safe launch of an installed Steam title.
- [ ] Add Wake-on-LAN and online/offline heartbeat.
- [ ] Add Playnite-native launch integration so Epic/GOG/EA/Ubisoft/etc. do not rely on guessed URI formats.
- [ ] Add Sunshine/Moonlight handoff for remote play.

### Phase 3 — console/library coverage
- [ ] Xbox account/library connector and available launch/remote-play routes.
- [ ] PlayStation account/library connector and supported remote-session routes.
- [ ] Nintendo library tracking; treat direct remote launch as manual unless a supported path exists.
- [ ] Physical-game barcode/manual ingestion.
- [ ] Subscription catalog state for Game Pass/PlayStation Plus/etc. without counting it as permanent ownership.

### Phase 4 — retro integration
- [ ] Deploy RomM when hardware/storage requirements are acceptable.
- [ ] Import RomM as another provider rather than making it the master catalog.
- [ ] Sync saves/states where supported.

### Phase 5 — Jarvis and UX
- [ ] Build Game Hub web UI.
- [ ] Expose search, ownership, installation, and launch capabilities to Jarvis.
- [ ] Support requests such as `Do I own Elden Ring?`, `show every Pokemon game`, and `play Cyberpunk downstairs`.
- [ ] Add policy/approval/audit integration before Jarvis can install/uninstall or change platform/account state.

## Immediate next build task

After the foundation is deployed, implement the **Playnite sync bridge** because it gives the fastest path to a large modern PC/storefront library while the direct provider connectors are built behind the same API contract.
