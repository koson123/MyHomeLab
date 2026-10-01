# Game Hub Windows client

`GameHubClient.exe` is the easy-setup Windows companion for Trevor Game Hub.

## What the EXE does

- provides a small setup window for the Game Hub URL, API key, agent token, device name, and Playnite path
- stores secrets encrypted for the current Windows user with DPAPI
- copies itself to `%LocalAppData%\TrevorGameHub\GameHubClient.exe`
- installs/updates the bundled Playnite 10 `Game Hub Sync` plugin
- registers the background launch agent at Windows sign-in for the current user
- starts a local HTTP launch agent on port `8790` by default
- keeps remote launches in dry-run mode by default
- only permits `playnite://` and `steam://` launch URIs

## Expected setup flow

1. Deploy the Game Hub server and configure its API key and agent token.
2. Run `GameHubClient.exe` on the gaming PC.
3. Enter the server URL and matching secrets.
4. Confirm the detected Playnite Extensions path.
5. Leave dry-run enabled for the first test.
6. Click **Install / Update**.
7. Restart Playnite and run **Update Game Library** once.
8. Verify the Game Hub library is populated and test one launch in dry-run mode.
9. Only then disable dry-run for real launches.

The standard installed Playnite extensions folder is `%AppData%\Playnite\Extensions`. Portable Playnite users can choose its local `Extensions` folder in the setup UI.

## Build

GitHub Actions publishes a self-contained `win-x64` single-file executable, so the target PC does not need Python or a separately installed .NET runtime.
