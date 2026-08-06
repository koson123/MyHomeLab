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

| VM / CT | Purpose | Intended disk | State |
|---|---|---:|---|
| VM 1 / `mini-mom` | Paperless-ngx, Mom Immich, custom inventory app | 64 GB | Needs audit |
| VM 2 / `mini-router` | OPNsense router/firewall | 64 GB | Known operating |
| VM 3 / `mini-ha` | Home Assistant OS | 128 GB | Known operating; audit |
| `mini-llm` | Local assistant/LLM | 100 GB | Planned |
| VM 4 / `mini-life-heavy` | Frigate, WorkAdventure, Nextcloud later | 100 GB | Planned |
| VM 5 / `mini-random` | Gridfinity and experiments | 30 GB | Planned |
| VM 6 / `mini-games` | Crafty Controller and game servers | 200 GB | Needs audit |
| VM 7 / `mini-gus` | Friend/Gus Immich | 40 GB | Needs verification |
| Networking VM | Nginx Proxy Manager and WireGuard | 80 GB | NPM operating; WireGuard planned |
| DNS CT | Pi-hole | 8 GB | Known operating; audit |
| Monitoring CT | Uptime Kuma | 12 GB | Needs verification |
| VM 12 | Raspberry Pi OS testing | TBD | Not created/optional |

Planned mini-PC allocation is 826 GB excluding VM 12. These are intended virtual-disk sizes and still need to be reconciled against the actual Proxmox configuration.

Mom's VM is intentionally placed on the parent-network side/in front of OPNsense so Mom's NAS is easier to mount and her services remain portable.

### XPS layout

| VM | Purpose | Intended virtual disk | State |
|---|---|---:|---|
| `xps-life` | Trevor Immich, Mealie, Actual; later lifestyle apps | 250 GB | Verified services; guest currently exposes about 97 GB usable |
| `xps-arr` | Download and media automation stack | 200 GB | Verified services; guest currently exposes about 97 GB usable |
| `xps-media` | Jellyfin, Audiobookshelf, Navidrome, Sheets, Komga | 200 GB | Verified except Komga; guest currently exposes about 97 GB usable |

The XPS VMs were allocated 650 GB total in Proxmox. The roughly 97 GB filesystems observed inside each Ubuntu guest likely mean their partitions/LVM logical volumes/filesystems have not yet been expanded to consume the full virtual disks. Verify the Proxmox disk sizes first, then expand each guest safely after service restoration.

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
