# Architecture

## Physical hardware

### GMKtec K8 Plus-style mini PC

Primary compact Proxmox host. Purchased with included RAM and SSD.

Verified host facts (2026-08-06):

- Hostname: `pve-mini`
- Proxmox VE 9.2.4
- AMD Ryzen 7 8845HS, 8 cores / 16 threads
- 28 GiB usable RAM
- 1 TB NVMe; approximately 794 GB in `local-lvm`
- Two-node Proxmox cluster, healthy and quorate

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
| VM 101 / `mini-mom` | Paperless-ngx, Mom Immich, custom inventory app | 64 GB | Running; Immich/Paperless verified; inventory app unverified |
| VM 102 / `mini-router` | OPNsense router/firewall | 64 GB | Running; 2 vCPU / 4 GB RAM; dual bridge; starts first |
| VM 103 / `mini-ha` | Home Assistant OS | 128 GB | Running; 2 vCPU / 4 GB RAM; `10.50.0.159` |
| `mini-llm` | Modular homelab Jarvis core, proactive-event engine, trusted Gospel index, and replaceable local model runtime | 100 GB | Planned |
| VM 4 / `mini-life-heavy` | Frigate, WorkAdventure, Nextcloud later | 100 GB | Planned |
| VM 5 / `mini-random` | Gridfinity and experiments | 30 GB | Planned |
| VM 107 / `mini-games` | Crafty Controller and game servers | 200 GB | Running; 4 vCPU / 10 GB RAM; `10.50.0.118`; app audit pending |
| VM 7 / `mini-gus` | Friend/Gus Immich | 40 GB | Not currently created |
| VM 109 / `mini-networking` | Nginx Proxy Manager and WireGuard | 80 GB | Running; 2 vCPU / 4 GB RAM; `10.50.0.135` |
| CT 110 / `mini-dns` | Pi-hole | 8 GB | Running; 1 vCPU / 512 MB; `10.50.0.134` |
| CT 111 / `mini-monitoring` | Uptime Kuma | 12 GB | Running; 1 vCPU / 1 GB; `10.50.0.143`; app audit pending |
| VM 12 | Raspberry Pi OS testing | TBD | Not created/optional |

Planned mini-PC allocation is 826 GB excluding VM 12. The seven existing guests total 556 GB of virtual-disk allocations. The LLM, life-heavy, random, Gus, and Raspberry Pi test VMs are not currently created. With only about 2.4 GiB host RAM available during the audit, RAM must be planned before adding guests.

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


## Jarvis deployment boundary

The planned `mini-llm` VM hosts the modular homelab Jarvis services described in [JARVIS.md](JARVIS.md). Home Assistant remains on HAOS, large media remains on NAS storage, and Jarvis connects to other services through scoped APIs. The LLM is replaceable and does not receive unrestricted shell, Docker, Proxmox, Home Assistant, file, or credential access.
