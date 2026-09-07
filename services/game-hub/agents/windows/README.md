# Windows Game Hub Agent

This is the first bounded launcher endpoint for a Windows gaming PC.

It does **not** accept arbitrary shell commands or executable paths. It only opens URI schemes explicitly allow-listed by configuration. The default allowed schemes are `steam` and `playnite`, and dry-run is enabled by default.

## Install

From PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set runtime variables for the current test session:

```powershell
$env:GAMEHUB_AGENT_TOKEN="replace-with-the-same-agent-token-used-by-game-hub"
$env:GAMEHUB_AGENT_DRY_RUN="true"
$env:GAMEHUB_AGENT_ALLOWED_SCHEMES="steam,playnite"
uvicorn agent:app --host 0.0.0.0 --port 8790
```

Then register the device in Game Hub with an `agent_url` such as `http://gaming-pc.internal:8790` and add that exact hostname to the server's `GAMEHUB_ALLOWED_AGENT_HOSTS`.

## Safe enablement order

1. Verify `/health` locally.
2. Keep `GAMEHUB_AGENT_DRY_RUN=true` and verify Game Hub can dispatch a test request.
3. Sync Playnite and select one installed game's `playnite://playnite/start/<database-guid>` launch target, or create a Steam target such as `steam://rungameid/<app-id>`.
4. Confirm the dry-run response contains exactly the intended URI.
5. Only then set `GAMEHUB_AGENT_DRY_RUN=false` and retest.

The Playnite route is preferred for broad PC-storefront launching because Playnite already knows how each imported library entry should start. Future work can replace or supplement the URI bridge with deeper Playnite-native install/status controls.
