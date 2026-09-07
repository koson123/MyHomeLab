# Octo-Fiesta Music Integration

## Decision

**Status: planned / worth testing.**

Octo-Fiesta is a strong fit for the existing Navidrome-based music stack. It acts as a Subsonic/OpenSubsonic proxy in front of Navidrome. A compatible client connects to Octo-Fiesta instead of directly to Navidrome; local-library results still come from Navidrome, while missing music can be searched from a configured external provider, streamed, downloaded, tagged, and then retained in the local music library for later playback.

This directly supports the long-term Jarvis music goal: Trevor should eventually be able to ask for a song, artist, album, playlist, mood, or other music request and have the self-hosted system search the local library first, then use an approved acquisition path for missing music.

## Why it fits this homelab

- Navidrome is already running on `xps-media` and exposes the Subsonic-compatible API Octo-Fiesta expects.
- Feishin is listed as a compatible desktop client, so the existing planned/manual player workflow should fit.
- Octo-Fiesta is designed for Docker/Compose deployment, matching the existing media-stack operating model.
- It can retain downloaded tracks in an organized `Artist/Album/Track` structure with metadata and artwork rather than acting only as a temporary streaming bridge.
- It can expose external playlists and synced lyrics where the provider/client combination supports them.
- It gives Jarvis a cleaner future interface: local-first search and playback can remain deterministic through Navidrome/OpenSubsonic while Octo-Fiesta handles the external-provider layer.

## Important current limitation

Do **not** design the homelab around SquidWTF as the provider. The Octo-Fiesta project currently marks SquidWTF as deprecated because its public upstream music services are no longer a reliable full-track source. The planned deployment should use a supported native provider account such as Deezer, Qobuz, Tidal, or Yandex Music, subject to Trevor's account/subscription and the provider's terms.

External provider authentication tokens are secrets. They must stay out of Git, be stored in the normal homelab secrets mechanism, and be replaceable without changing the rest of the music architecture.

## Proposed architecture

```text
Feishin / approved Subsonic clients / Jarvis Music
                    |
                    v
              Octo-Fiesta
               /       \
              v         v
        Navidrome     Approved music provider
              |         |
              |         +--> missing track stream/download
              v
       Local music library on NAS
```

The current Navidrome container sees `/mnt/nas/Music` read-only. Keep Navidrome read-only. If Octo-Fiesta is deployed on `xps-media`, give **only Octo-Fiesta** the minimum required write access to a dedicated import/download directory on the music NAS, for example a future `/mnt/nas/Music/OctoFiesta` path. Navidrome can then scan/read that directory without gaining write access to the whole library.

## Deployment target

Preferred first test location: `xps-media`, beside Navidrome, unless the full server reconciliation identifies a better placement or insufficient headroom.

Do not deploy it during the current stabilization/reconciliation work. Treat this as a later music-stack enhancement after backups, storage, networking, and service health are in a known-good state.

## Test plan before making it primary

- [ ] Re-check the current Octo-Fiesta release, provider support, known issues, and client compatibility immediately before deployment.
- [ ] Select one supported native provider account for the first test; do not rely on SquidWTF.
- [ ] Deploy Octo-Fiesta in Docker/Compose with secrets outside Git.
- [ ] Connect it to the existing Navidrome instance.
- [ ] Give Octo-Fiesta write access only to a dedicated music import/download directory; keep Navidrome read-only.
- [ ] Test local-library search and playback through the proxy.
- [ ] Test search, immediate playback, download, metadata, cover art, lyrics, and later replay of a missing track.
- [ ] Test Feishin and at least one iPhone-compatible client Trevor actually wants to use.
- [ ] Test external playlists and verify whether the chosen client exposes them cleanly.
- [ ] Measure RAM/CPU/network use during searches and downloads and watch NAS growth.
- [ ] Check for duplicate tracks, bad metadata, failed downloads, token-expiration behavior, and provider/API breakage.
- [ ] Add Uptime Kuma monitoring and a basic health check if the test becomes permanent.
- [ ] Document backup requirements for Octo-Fiesta configuration/secrets while treating downloaded music according to the normal media backup policy.
- [ ] Only after the test is stable, route normal Subsonic clients through Octo-Fiesta instead of directly to Navidrome.

## Jarvis integration direction

Jarvis should not receive unrestricted filesystem access just to obtain music. The future flow should be typed and deterministic:

1. Search local Navidrome library.
2. If the requested music is already local, play it directly.
3. If it is missing, query Octo-Fiesta/external-provider search.
4. Present or automatically use the result according to Trevor's configured approval policy.
5. Start playback through the approved client/device.
6. Let Octo-Fiesta persist the track locally when configured to do so.
7. Rescan/update Navidrome and make the local copy the preferred source for later playback.

This should complement SoulSync/slskd rather than automatically deleting that existing acquisition path. After Octo-Fiesta is proven, compare reliability, catalog coverage, metadata quality, automation friendliness, and storage behavior before deciding whether one path should become primary.

## Upstream project

- Project: `V1ck3s/octo-fiesta`
- License: GPL-3.0
- Role: Subsonic/OpenSubsonic proxy and external music-provider bridge for Navidrome-compatible libraries.
