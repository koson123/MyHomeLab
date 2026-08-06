# Services

## Verified XPS services

| Service | Host | Compose path | Storage / notes |
|---|---|---|---|
| Immich (Trevor) | `xps-life` | `/opt/life/immich/docker-compose.yml` | Photos on `/mnt/jknas/all_photos_for_immich/Trevor` |
| Actual Budget | `xps-life` | `/opt/life/actual/docker-compose.yml` | Local app data |
| Mealie | `xps-life` | `/opt/life/mealie/docker-compose.yml` | `/opt/life/mealie/data` |
| qBittorrent | `xps-arr` | `/opt/arr/qbittorrent/docker-compose.yml` | Normal public IP; no Gluetun |
| Prowlarr | `xps-arr` | `/opt/arr/prowlarr/docker-compose.yml` | ARR network |
| Sonarr | `xps-arr` | `/opt/arr/sonarr/docker-compose.yml` | Media NAS |
| Radarr | `xps-arr` | `/opt/arr/radarr/docker-compose.yml` | Media NAS |
| Seerr/Jellyseerr | `xps-arr` | `/opt/arr/jellyseerr/docker-compose.yml` | Request frontend |
| Shelfarr | `xps-arr` | `/opt/arr/shelfarr/docker-compose.yml` | Books |
| SoulSync + slskd | `xps-arr` | `/opt/arr/soulstack/docker-compose.yml` | Music acquisition |
| Swiparr | `xps-arr` | `/opt/arr/swiparr/docker-compose.yml` | Discovery UI |
| Jellyfin | `xps-media` | `/opt/media/jellyfin/docker-compose.yml` | `/mnt/nas`; config/data/cache/log under `/opt/media/jellyfin` |
| Audiobookshelf | `xps-media` | `/opt/media/audiobookshelf/docker-compose.yml` | `/mnt/nas/Audiobooks`, `/mnt/nas/Books` |
| Navidrome | `xps-media` | `/opt/media/navidrome/docker-compose.yml` | Read-only `/mnt/nas/Music` |
| Sheets | `xps-media` | `/opt/media/sheetsapp/docker-compose.yml` | `/mnt/nas/SheetMusic` and local data |

Jellyfin currently has both explicit application directories and legacy Docker volumes mounted. Do not remove either until a deliberate migration confirms which data is authoritative.

## Network/platform services

| Service | Intended host | State |
|---|---|---|
| OPNsense | `mini-router` / VM 102 | VM verified running; application/config audit pending |
| Nginx Proxy Manager | `mini-networking` / VM 109 | VM and IP verified; application/config audit pending |
| Pi-hole | `mini-dns` / CT 110 | CT and IP verified; application/config audit pending |
| Uptime Kuma | `mini-monitoring` / CT 111 | CT and IP verified; application audit pending |
| WireGuard | Networking area | Planned |
| Home Assistant OS | `mini-ha` / VM 103 | VM and IP verified; application audit pending |
| Proxmox Backup Server | Old laptop | Needs current audit |

## Family/friend services

| Service | Intended host | State |
|---|---|---|
| Mom Immich | `mini-mom` / VM 101 | Verified healthy; port 2283 |
| Paperless-ngx | `mini-mom` / VM 101 | Verified healthy/running; port 8000 |
| Mom inventory app | `mini-mom` / VM 101 | `/opt/mom/inventory` exists; no running container observed; verify deployment |
| Gus/friend Immich | `mini-gus` | Dedicated VM not currently created |

Mom's services and storage should stay grouped so they can be moved later. Gus's Immich must remain separate from Mom's.

## Game services

- Crafty Controller is the selected manager.
- Planned worlds: cross-platform, shared modded Java, private modded Java.
- Cross-platform world name: **Velmora**
- Velmora Java port: TCP `25566`
- Velmora Bedrock port: UDP `19132`
- Geyser/Floodgate provides Java/Bedrock joining.
- Historical parent-router forwards included TCP `25565/25566`, UDP `19132`, and TCP `80/443` toward the lab gateway.
- Current Crafty, worlds, backups, plugins, memory limits, and external connectivity need verification.

## Future applications

- Komga (immediate)
- Vaultwarden
- LibreCloset
- Price Ghost
- Workout app
- Nutrition/macro tracker
- Frigate
- WorkAdventure
- Nextcloud
- Local LLM/assistant
- Gridfinity/testing services
