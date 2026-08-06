# Architecture

## Physical hardware

### GMKtec K8 Plus-style mini PC

Primary compact Proxmox host. Purchased with included RAM and SSD.

Intended workloads:

- OPNsense
- Home Assistant OS
- Mom's services
- Local LLM
- Heavy/later services
- Game servers
- Friend/Gus Immich
- Experiments

### Dell XPS 8700

- Intel Core i7-4790 @ 3.60 GHz
- 16 GB RAM
- NVIDIA GTX 745
- Proxmox host for the main Docker application VMs

### Old laptop

- 16 GB RAM
- Dedicated Proxmox Backup Server (PBS)

### Raspberry Pi 5

- 8 GB RAM
- Available for edge/network/testing projects

### Storage

- Mom's NAS: approximately 11 TB total; `192.168.40.147` observed
- Nova/media NAS or file server: Jellyfin share observed at `10.50.0.113`
- Older Synology DS214: 2 x 2 TB, historical/possible auxiliary storage

### Network hardware

- 8-port unmanaged office switch
- 5-port unmanaged server switch
- OpenWrt/mesh and travel-router work in progress

## Logical layout

### Mini-PC planned layout

| VM / area | Purpose | State |
|---|---|---|
| `mini-mom` | Paperless-ngx, Mom Immich, custom inventory app | Needs audit |
| `mini-router` | OPNsense router/firewall | Known operating |
| `mini-ha` | Home Assistant OS; 2 cores, 4 GB RAM, 128 GB disk planned | Known operating; audit |
| `mini-llm` | Local assistant/LLM | Planned |
| `mini-life-heavy` | Frigate, WorkAdventure, Nextcloud later | Planned |
| `mini-random` | Gridfinity and experiments | Planned |
| `mini-games` | Crafty Controller and game servers; 300 GB planned | Needs audit |
| `mini-gus` | Friend/Gus Immich | Needs verification |
| Networking area / VM 109 | Pi-hole, Uptime Kuma, VPN endpoint, NPM | Partly operating; audit |

Mom's VM is intentionally placed on the parent-network side/in front of OPNsense so Mom's NAS is easier to mount and her services remain portable.

### XPS layout

| VM | Purpose | State |
|---|---|---|
| `xps-life` | Trevor Immich, Mealie, Actual; later lifestyle apps | Verified |
| `xps-arr` | Download and media automation stack | Verified |
| `xps-media` | Jellyfin, Audiobookshelf, Navidrome, Sheets, Komga | Verified except Komga |
| `xps-net` | Earlier plan for Pi-hole, Uptime Kuma, VPN, NPM | Reconcile with current VM 109 |
| `xps-pi-test` | Raspberry Pi OS testing | Optional/planned |

## Platform standards

Preferred VM baseline:

- Ubuntu 24.04 Server currently used, despite a general Debian preference
- OVMF/UEFI
- Q35 machine type
- QEMU guest agent
- `discard=on` for SSD-backed virtual disks
- Docker Compose projects stored under `/opt/<group>/<service>`
- CIFS mounts for NAS storage

Do not over-allocate RAM to game servers; the hosts have limited memory.
