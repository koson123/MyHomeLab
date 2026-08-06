# Current State

Last documentation audit: 2026-08-06.

The documents have been cross-checked against the command output currently available. This is a documentation audit, not a substitute for a new live audit of Proxmox, the mini-PC workloads, PBS, or service logins.

This file separates confirmed reality from older plans.

## Verified running

### `xps-life` — complete

Host IP: `10.50.0.152`

| Service | State | Port / notes |
|---|---|---|
| Trevor Immich | Verified healthy | `2283`; four-container stack; v3.0.2 observed |
| Actual Budget | Verified running | `5006` |
| Mealie | Verified healthy | `9925 -> 9000` |
| Trevor photo NAS mount | Verified mounted | `/mnt/jknas` -> `//192.168.40.147/main` |
| Trevor photo library | Verified | 85 GB at `/mnt/jknas/all_photos_for_immich/Trevor` |

The temporary backup mount `/mnt/server` was removed. Do not remove `/mnt/jknas` or `/root/.jknas-credentials`.

### `xps-arr` — complete for now

| Service | State | Host port |
|---|---|---:|
| qBittorrent | Verified running | 8080; peer 6881 TCP/UDP |
| Prowlarr | Verified running | 9696 |
| Sonarr | Verified running | 8989 |
| Radarr | Verified running | 7878 |
| Seerr/Jellyseerr | Verified healthy | 5055 |
| Shelfarr | Verified running | 5056 |
| SoulSync web UI | Verified healthy | 8008; also 8888-8889 |
| slskd | Verified healthy | 5030; peer 50300 |
| Swiparr | Verified healthy | 4321 |

All containers had been up for 13 days with no exited or restarting containers. Local root storage was 17% used (77 GB free). The media NAS had 1.4 TB free.

Important:

- qBittorrent is **not** routed through Gluetun.
- qBittorrent currently uses the home public IP.
- Gluetun is postponed until a commercial VPN provider is chosen.
- `/mnt/server` was still mounted at the last check; remove it after restoration work is fully finished.
- The VM was observed with only 2 GB RAM and heavy swap use; reassess memory later.

### `xps-media` — mostly complete

Host IP: `10.50.0.126`

| Service | State | Host port |
|---|---|---:|
| Jellyfin | Verified healthy | Host networking/no published port shown |
| Audiobookshelf | Verified running | 13378 -> 80 |
| Navidrome | Verified running | 4533 |
| Sheets | Verified running | 5088 -> 8080 |
| Komga | Missing | Restore/install next |

`/mnt/nas` is verified mounted from `//10.50.0.113/Jellyfin`. No failed or restarting containers were present. Root storage had 70 GB free.

A temporary `/mnt/server` mount is not currently present. The credential file `/root/.nova-nas-credentials` exists and can be used to mount the backup NAS temporarily without exposing its contents.

## Known operating, not fully audited in the current sweep

- OPNsense router/firewall
- Nginx Proxy Manager
- Pi-hole
- HomeLab Wi-Fi/network
- Public DNS and HTTPS proxying
- Proxmox hosts
- Home Assistant OS VM
- Minecraft/Crafty environment (historically working; current worlds need verification)

Nginx Proxy Manager was recently reachable at `10.50.0.135:81`. That VM appeared to use DHCP and should receive a reservation.

## Previously restored but needs verification

- Mom's Immich
- Paperless-ngx
- Mom's custom inventory app
- Uptime Kuma
- Home Assistant OS
- Gus's/friend's Immich and whether its dedicated VM exists
- Crafty Controller and all game servers/worlds
- Pi-hole persistence and upstream DNS configuration
- Nginx Proxy Manager backups, certificates, and all proxy hosts

## Verification boundary

The current evidence directly verifies the three XPS application stacks and their observed mounts/status at the time shown. It does **not** yet verify:

- Actual Proxmox virtual-disk sizes, VM IDs, CPU/RAM assignments, bridges, or autostart settings
- Guest partition/LVM capacity beyond the observed approximately 97 GB root filesystems
- Mini-PC VM/CT health and placement
- PBS job recency and restoreability
- Public-domain reachability for every service
- Application-level data/login checks after a reboot

These must remain open until live outputs are captured.

## Missing or planned

- Komga
- WireGuard remote access
- Static DHCP reservations for infrastructure
- IPv6 DNS correction on HomeLab DHCP
- Vaultwarden
- LibreCloset
- Price Ghost
- Workout/fitness app
- Nutrition/macro tracker
- Frigate and camera system
- WorkAdventure
- Nextcloud (later)
- Local LLM/AI assistant VM
- Gridfinity/random-project stack
- Test Raspberry Pi VM, if still useful

## Postponed

- Gluetun/commercial outbound VPN
- Jellyfin/media storage redesign (possibly ZFS), until the complete server is stable
- Nextcloud
