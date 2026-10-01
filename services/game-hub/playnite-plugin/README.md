# Game Hub Sync for Playnite 10

This is the first broad modern-library scanner for Game Hub. It targets **Playnite 10.x** and PlayniteSDK `6.16.0` on .NET Framework 4.6.2.

Playnite 11 is currently a separate alpha rewrite with an incompatible plugin API, so this bridge intentionally keeps the server contract independent of Playnite internals. A future Playnite 11 client can send the same `/api/v1/import/playnite` payload.

## What it sends

For each Playnite library entry:

- Playnite database ID
- provider/store game ID when present
- plugin ID
- source/store name
- platform names
- installed state and install directory
- playtime and play count
- last activity
- hidden/favorite flags
- sorting name

The Game Hub server converts this into canonical games, provider entitlements, device installations, and Playnite launch targets.

**Important:** Playnite-derived entitlements are initially classified as `library_access`, not guaranteed permanent ownership. Direct provider connectors will later refine purchased/subscription/redeemed/physical status.

## Configuration

The plugin creates `gamehub.json` in its Playnite plugin user-data folder on first load. Use **Extensions -> Game Hub -> Open Game Hub config folder** to find it.

Example:

```json
{
  "GameHubUrl": "http://gamehub.internal:8787",
  "ApiKey": "replace-with-gamehub-api-key",
  "DeviceName": "Gaming-PC",
  "AgentUrl": "http://gaming-pc.internal:8790",
  "SyncOnLibraryUpdated": true
}
```

Never commit a real API key.

## Build

Requirements:

- Windows
- Visual Studio 2022 (or another IDE/build environment with reliable .NET Framework 4.6.2 targeting support)
- Playnite 10.x

Build the project and place `GameHubSync.dll` plus `extension.yaml` in a Playnite extension directory, or use Playnite Toolbox to package/install the extension once the first local build has been verified.

Restart Playnite after installing/updating the plugin.

## First test order

1. Start Game Hub and verify `/health`.
2. Configure the Windows launcher agent with dry-run still enabled and `GAMEHUB_AGENT_ALLOWED_SCHEMES=steam,playnite`.
3. Edit `gamehub.json` with the Game Hub URL/API key and this PC's device/agent names.
4. In Playnite: **Extensions -> Game Hub -> Sync library to Game Hub**.
5. Query Game Hub `/api/v1/games`, `/api/v1/installations`, and `/api/v1/launch-targets`.
6. Trigger one installed game's Game Hub launch target. Confirm the Windows agent returns `dry-run` for the expected `playnite://playnite/start/<database-guid>` URI.
7. Only after the exact URI is verified should launcher dry-run be disabled.

Automatic sync runs after a Playnite library update when `SyncOnLibraryUpdated` is true.
