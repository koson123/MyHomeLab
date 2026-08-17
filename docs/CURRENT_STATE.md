# Current State

**Audit date:** August 17, 2026  
**Purpose:** One authoritative record of what is actually deployed, what is healthy, what differs from the plan, and what remains to build.

## Status legend

- **Operational:** Running and verified during this audit.
- **Partial:** Running, but missing protection, configuration, or a planned component.
- **Planned:** Intentionally not deployed yet.
- **Unknown:** Must be checked when access is available.
- **Retired/legacy:** Preserved only for recovery or cleanup review.

## Immediate priorities

1. **Protect Nova NAS data.** Nova is RAID 0; failure of either disk loses the entire 3.6 TB volume. RAID is not a backup, but RAID 0 also provides no drive-failure tolerance.
2. **Deploy Proxmox Backup Server and scheduled jobs.** Neither Proxmox node currently has a backup job.
3. **Create application-level backups.** Paperless, Actual, Mealie, NPM, Crafty/game worlds, ARR configs, and media-service configs lack confirmed current backups.
4. **Copy the verified full Home Assistant backup off-VM before updating.** A 37.92 MB full local backup now exists; HA's repair warning had not yet refreshed immediately after creation.
5. **Assign stable DHCP reservations/static addresses** to infrastructure guests and both NAS devices.
6. **Expand unused LVM space** in `xps-life` and `xps-media` when convenient.

---

# 1. Physical infrastructure

## `pve-mini` — primary/core Proxmox node

**Status:** Operational

- Proxmox VE 9.2.4; kernel 7.0.14-4-pve
- AMD Ryzen 7 8845HS, 8 cores / 16 threads
- 28 GiB usable RAM
- 1 TB ZHITAI Ti600 NVMe
- `local`: about 98 GB, 11% used
- `local-lvm`: about 794 GB, 17% used
- Parent-network address: `192.168.40.67/24`
- Lab-network address: `10.50.0.2/24`
- Parent gateway: `192.168.40.1`
- Roughly 2.8 GiB RAM was available during the audit
- No Proxmox backup jobs
- No replication jobs

## `pve-xps` — application/media Proxmox node

**Status:** Operational

- Proxmox VE 9.2.4; kernel 7.0.14-4-pve
- Intel Core i7-4790, 4 cores / 8 threads
- 15 GiB usable RAM
- Proxmox system disk: 1 TB Samsung drive, SMART passed
- Additional 1 TB WD drive with old partitions; not mounted or configured as Proxmox storage, SMART passed
- `local`: about 98 GB, 9% used
- `local-lvm`: about 794 GB, 12% used
- Lab address: `10.50.0.10/24`
- Gateway: `10.50.0.1`
- Roughly 3 GiB RAM was available during the audit
- No Proxmox backup jobs
- No replication jobs

## Proxmox Backup Server laptop

**Status:** Planned; not installed or connected

Remaining work:

- Install PBS on the laptop.
- Create and validate a datastore.
- Connect both Proxmox nodes.
- Schedule VM/LXC backups.
- Define retention/pruning and verification jobs.
- Run and document restore tests.
- Remember that PBS protects guest disks, not NAS folders mounted inside guests.

## JK NAS / Mom's NAS

**Status:** Operational through SMB; hardware health pending access

- Address: `192.168.40.147`
- SMB share: `//192.168.40.147/main`
- Capacity: 11 TB
- Used: 2.5 TB (24%)
- Available: 8 TB
- Mounts successfully through systemd automount with no mount errors observed this boot
- The former `moms-nas.gardnergate.cc` DNS/public endpoint was intentionally removed; a stale NPM proxy-host configuration still needs deletion.

Stored Immich data:

- Trevor: 89 GB; 4,689 original/library files
- Gus: 81 GB; 9,463 original/library files
- Mom: 801 GB; 103,524 original/library files
- Mom Paperless NAS media: currently empty

Unknown until access is available:

- NAS manufacturer/model
- Disk count, models, sizes, temperatures, and SMART results
- RAID/pool and filesystem type
- Snapshots, replication, backup jobs, UPS status, and firmware state

## Nova NAS

**Status:** Operational, but critical protection risk

- Synology DS214
- DSM 7.1.1-42962 Update 9
- Marvell Armada XP MV78230, 2 cores at 1.07 GHz
- 512 MB RAM
- Address: `10.50.0.113` via DHCP
- 1 GbE, full duplex, MTU 1500
- Two WD Red `WD20EFRX-68EUZN0` drives, each reported as 1.8 TB
- Drive temperatures during audit: 39 C and 38 C
- Both drives reported healthy/normal
- Storage Pool 1: 3.6 TB RAID 0
- Volume 1: healthy, 2.3 TB used, 1.3 TB free, about 65% used
- SMB share mounted as `//10.50.0.113/Jellyfin`
- Enabled services include DSM, SMB, SNMP, WS-Discovery, iSCSI/SAN Manager, Synology Drive, NTP, and related Synology services

Critical note:

- RAID 0 has no redundancy. Either drive failing destroys the entire pool.
- No verified independent backup, snapshot schedule, or UPS protection was captured.
- Review DSM update/support options, unused exposed services, QuickConnect requirements, backups, and replacement storage design.

Media share contents:

- Movies: 198 files
- Shows: 1,383 files
- Music: 991 files
- Audiobooks: 2,197 files
- Books: 23 files
- Downloads: 137 files
- MusicVideos: 0 files
- SheetMusic: 129 files

---

# 2. Proxmox guests

## Guest map

| Node | ID | Type | Name | Address | Status |
|---|---:|---|---|---|---|
| `pve-mini` | 101 | VM | `mini-mom` | `192.168.40.252` | Operational/partial |
| `pve-mini` | 102 | VM | `mini-router` | WAN `192.168.40.166`; LAN `10.50.0.1` | Operational |
| `pve-mini` | 103 | VM | `mini-ha` | `10.50.0.159` | Operational/partial |
| `pve-mini` | 107 | VM | `mini-games` | `10.50.0.118` | Operational/partial |
| `pve-mini` | 109 | VM | `mini-networking` | `10.50.0.135` | Operational/partial |
| `pve-mini` | 110 | LXC | `mini-dns` | `10.50.0.134` | Operational |
| `pve-mini` | 111 | LXC | `mini-monitoring` | `10.50.0.143` | Operational/partial |
| `pve-xps` | 201 | VM | `xps-life` | `10.50.0.152` | Operational/partial |
| `pve-xps` | 202 | VM | `xps-arr` | `10.50.0.123` | Operational/critical gap |
| `pve-xps` | 203 | VM | `xps-media` | `10.50.0.126` | Operational/partial |

All ten current guests were running and configured with `onboot: 1` during the audit.

## `mini-router` — OPNsense

**Status:** Operational

- OPNsense 26.1.6_2
- 2 vCPU, 4 GB RAM, 64 GB disk
- WAN `192.168.40.166/24` on parent network
- LAN `10.50.0.1/24`
- WAN/default gateway `192.168.40.1`
- Firewall enabled; no state-table limit/memory failures reported
- About 20% disk used
- 59 local configuration-history snapshots
- Latest local config snapshot: August 6, 2026
- No off-VM config backup or PBS backup
- Temporary root/password SSH used for audit should remain disabled afterward

## `mini-mom`

**Status:** Operational/partial

- Ubuntu 24.04.4 LTS
- 2 vCPU, 4 GB RAM, 64 GB virtual disk
- Intentionally placed on parent network for easier access to Mom's NAS
- JK NAS mounted at `/mnt/moms-nas`
- No failed system services

Running stacks:

- Mom Immich v3 on port 2283: healthy
  - NAS media: `/mnt/moms-nas/all_photos_for_immich/mini-mom/immich`
  - Local PostgreSQL: `/opt/mom/immich/postgres`
  - Machine learning enabled
  - Daily Immich database dumps working
- Paperless-ngx on port 8000: healthy
  - NAS consume/media folders
  - Local data/export/database stack
  - No current Paperless backup/export automation found

Planned:

- Mom's custom organization/inventory application; only an empty placeholder directory currently exists.

## `mini-ha` — Home Assistant OS

**Status:** Operational/partial

- Home Assistant Core 2026.8.1; 2026.8.2 was available during audit
- Supervisor 2026.07.5, healthy and supported
- 128 GB data disk; 11.3 GB used
- Address: `10.50.0.159/24`, assigned automatically; gateway/DNS `10.50.0.1`
- Local partial backup: `Automatic backup 2026.8.1`, created August 17, 2026, 37.51 MB, protected
- Verified local full backup: `Full backup before updates 2026-08-17`, slug `c7271835`, 37.92 MB
- The full backup includes Home Assistant, all five apps/add-ons, and the `share`, `ssl`, and `media` folders
- Both backups are stored only in Home Assistant (`.local`); the full backup is not password-protected
- Home Assistant Resolution still showed stale `no_current_backup`/`create_full_backup` entries when checked immediately after the full backup completed

Running apps/add-ons:

- Matter Server 9.2.0
- ESPHome Device Builder 2026.7.4
- Music Assistant 2.9.12; 2.9.13 was available
- File Editor 6.1.0
- Mosquitto Broker 7.1.0

Remaining:

- Copy the verified full backup off-VM and verify its integrity
- Add automatic local and off-VM backups
- Restore test
- Stable address/DHCP reservation
- Apply Core 2026.8.2 and Music Assistant 2.9.13 updates only after a full backup exists
- Expand real home automations, PC power/control, ESPHome/Bluetooth proxies, cameras, presence, energy/water/gas, irrigation, and related planned projects

## `mini-games`

**Status:** Operational/partial

- Ubuntu 24.04.4 LTS
- 4 vCPU, about 10 GB RAM allocated
- Crafty Controller in Docker; UI on HTTPS port 8443
- 46 GB of server data; VM filesystem 61% used
- No NAS mount
- No real game-server backups
- `/opt/crafty/backups` is empty

Running Minecraft servers:

- Fabric server: 43 GB, port 25565, `-Xmx6000M`
- Paper server: 2.7 GB, port 25566, `-Xmx4000M`

Risks/remaining:

- Both servers together can request the VM's entire RAM allocation.
- Create scheduled world/config backups and copy them off-VM.
- Review the published `25500-25600` range and expose only required ports.
- Add Crafty/server monitoring.

## `mini-networking`

**Status:** Operational/partial

- Ubuntu 24.04.4 LTS
- 2 vCPU, 4 GB RAM, 80 GB virtual disk
- Nginx Proxy Manager is the only deployed stack
- NPM ports: 80, 81, 443
- Data and certificates stored locally under `/opt/nginx-proxy-manager`
- No confirmed NPM backup
- No general remote-access VPN/mesh service deployed

## `mini-dns`

**Status:** Operational

- Debian 12 LXC
- 1 vCPU, 512 MB RAM, 8 GB disk
- Native Pi-hole (not Docker)
- DNS port 53; web ports 80/443
- No NAS mount
- Uses DHCP-assigned address
- Pi-hole FTL v6.7
- Upstream resolvers: Google DNS `8.8.8.8` and `8.8.4.4`
- DNS resolution and blocking verified; `doubleclick.net` returned `0.0.0.0`
- DNSSEC disabled; query logging enabled; listening mode `LOCAL`
- Teleporter configuration backup created August 17, 2026 and copied outside LXC 110 to `pve-mini:/root/pihole-backups/`
- Backup file: `pi-hole_mini-dns_teleporter_2026-08-17_20-39-41_UTC.zip` (23,695 bytes)
- SHA-256: `1f3ba88919986fb636b5ec4ac248757f50846483e54efef510966665511eccf7`
- Backup is outside the container but still on the same physical host; PBS/off-host protection remains required

## `mini-monitoring`

**Status:** Operational/partial

- Debian 12 LXC
- 1 vCPU, 1 GB RAM, 12 GB disk
- Uptime Kuma in Docker on port 3001
- Exactly one configured monitor: `Gus Immich - Public`, HTTP check of `https://gus.gardnergate.cc`, active at a 60-second interval
- Zero notification channels are configured
- No other public services, internal services, hosts, NAS devices, DNS, or certificates are monitored yet
- Live SQLite database: `/opt/uptime-kuma/data/kuma.db`
- Consistent SQLite backup created August 17, 2026 and copied outside LXC 111 to `pve-mini:/root/uptime-kuma-backups/kuma-2026-08-17.db` (424 KB)
- Database SHA-256: `c2db9b6f216bf8527e9859fae81eaf30bd2c5f50563681bb469b4af340cb355b`
- Compose backup SHA-256: `3e60e60b480cffe1db73abb51c7625b50e65799e2fdb0d82a6ae1acaf54d8c9b`
- These copies remain on the same physical mini-PC; PBS/off-host protection is still required

## `xps-life`

**Status:** Operational/partial

- Ubuntu 24.04.4 LTS
- 4 vCPU; ballooned memory, about 3.8 GB visible during audit
- 250 GB virtual disk, but only a 100 GB logical volume is mounted
- 148 GB is free inside the LVM volume group and can be added to the filesystem later
- JK NAS mounted at `/mnt/jknas`

Running stacks:

- Trevor Immich v3 on port 2283, healthy, machine learning enabled
- Gus Immich v3 on port 2284, healthy, machine learning intentionally disabled to save RAM
- Actual Budget on port 5006, HTTP 200
- Mealie on port 9925, healthy

Backup state:

- Trevor and Gus daily Immich database dumps are working on JK NAS.
- Actual and Mealie only have their live databases; no independent backup copies were found.

Planned but absent:

- LibreCloset
- Vaultwarden
- Workout application
- Price Ghost
- Nutrition/macro tracker

Architecture deviation:

- Gus Immich was originally planned as its own VM but is currently isolated as a separate Compose project on `xps-life`. It is working; decide later whether separation into its own guest is still worth the RAM/storage overhead.

## `xps-arr`

**Status:** Operational with a critical gap

- Ubuntu 24.04.4 LTS
- 2 vCPU; ballooned to about 2.3 GB RAM during audit
- Only about 590 MB RAM available and nearly 1 GB swap used
- Nova NAS mounted at `/mnt/nas`

Running:

- qBittorrent
- Prowlarr
- Sonarr
- Radarr
- Seerr (in the existing Jellyseerr project/config path)
- Swiparr
- Shelfarr
- SoulSync
- slskd

Intentional temporary state:

- **Gluetun is absent by current decision.** Trevor does not want to pay for a commercial VPN yet, so qBittorrent remains direct until that decision changes.

Remaining later:

- When Trevor is ready to pay for a supported VPN, deploy Gluetun, enforce dependency/network isolation, and verify the kill switch.
- Back up all `/opt/arr` configuration/appdata.
- Review resource allocation and internal port exposure.

## `xps-media`

**Status:** Operational/partial

- Ubuntu 24.04.4 LTS
- 4 vCPU; about 4 GB visible RAM
- 200 GB virtual disk, but only a 99 GB logical volume is mounted
- 99 GB is free inside the LVM volume group
- Nova NAS mounted at `/mnt/nas`

Running:

- Jellyfin 10.11.6, healthy, host network, port 8096
- Audiobookshelf, port 13378
- Navidrome, port 4533
- Sheets app, port 5088

Planned but absent:

- Komga

Transcoding:

- No NVIDIA GPU is visible inside the VM.
- The only displayed graphics controller is the virtual Bochs adapter.
- Jellyfin has no Docker device mapping for hardware transcoding and should be treated as CPU-transcoding.

Backups/storage:

- A 6.15 GB native Jellyfin restore archive remains under `restore-staging`.
- No confirmed backups for Audiobookshelf, Navidrome, or Sheets.

---

# 3. Public reverse-proxy map

| Public hostname | Internal target |
|---|---|
| `swiparr.gardnergate.cc` | `10.50.0.123:4321` |
| `immich.gardnergate.cc` | `10.50.0.152:2283` |
| `budget.gardnergate.cc` | `10.50.0.152:5006` |
| `mealie.gardnergate.cc` | `10.50.0.152:9925` |
| `gus.gardnergate.cc` | `10.50.0.152:2284` |
| `paperless.gardnergate.cc` | `192.168.40.252:8000` |
| `mom-immich.gardnergate.cc` | `192.168.40.252:2283` |
| `ha.gardnergate.cc` | `10.50.0.159:8123` |
| `jellyfin.gardnergate.cc` | `10.50.0.126:8096` |
| `books.gardnergate.cc` | `10.50.0.126:13378` |
| `music.gardnergate.cc` | `10.50.0.126:4533` |
| `sheets.gardnergate.cc` | `10.50.0.126:5088` |
| `jellyseerr.gardnergate.cc` | `10.50.0.123:5055` |

Removed/stale:

- `moms-nas.gardnergate.cc` no longer exists by Trevor's decision. Delete its remaining NPM proxy-host entry; do not restore its DNS record.

Review later:

- Confirm which services truly need public exposure.
- Strongly review Paperless, Home Assistant, Immich, Actual, and Mealie exposure and authentication controls.
- Keep NPM administration internal/VPN-only.
- Back up NPM configuration and certificates.

---

# 4. Backup and recovery inventory

## Working

- Daily Immich PostgreSQL dumps for Trevor, Gus, and Mom.
- OPNsense keeps 59 local configuration-history snapshots.
- One-time July 8 Proxmox VMA/LXC backups exist on JK NAS.
- Legacy restore/config packs exist under `TrevorServerDONTTOUCH`.
- Gus's original 82 GB laptop backup remains retained.
- Jellyfin's 6.15 GB native restore archive remains retained.
- Pi-hole v6 Teleporter configuration export exists outside LXC 110 on `pve-mini`; SHA-256 recorded above.
- A consistent Uptime Kuma SQLite backup and Compose file exist outside LXC 111 on `pve-mini`; checksums recorded above.

## Not adequate/current

- No PBS installation.
- No scheduled Proxmox backup jobs.
- No Proxmox replication jobs.
- No independent backup of NAS-mounted media/photos/documents was verified.
- Nova NAS is RAID 0 with no verified second copy.
- No current Paperless database/export backup.
- Home Assistant has a verified 37.92 MB **full local** backup plus a protected 37.51 MB partial backup, but no off-VM copy yet.
- No Crafty/game-world backup.
- No NPM backup.
- No Actual or Mealie backup.
- No ARR appdata backup.
- No Audiobookshelf/Navidrome/Sheets backup.
- Uptime Kuma now has a one-time local host-level database/Compose backup, but no scheduled or off-host backup.
- No documented routine restore tests.

Legacy backup storage on JK NAS:

- `complete_backups`: 8.5 GB
- `proxmox-vm-shell-backups-2026-07-08`: 28 GB
- `proxmox-migration-2026-07-01_12-06`: 77 GB
- `laptop-friend-immich-backup-2026-07-01_17-53`: 82 GB
- Failed/older migration copies also remain in the NAS recycle area

Do not delete legacy backups until current replacement backups exist and restore tests pass.

---

# 5. Planned guests and hosted services not yet deployed

## Mini-PC guests not created

- Local AI/LLM helper VM
- Heavy/Future Apps VM:
  - Frigate
  - WorkAdventure
  - Nextcloud much later
- Random/Test VM:
  - Gridfinity stack
  - experiments and disposable tests

## Hosted infrastructure not deployed

- Proxmox Backup Server laptop
- Cluster backup schedules, prune/verify jobs, and restore testing
- General secure remote-access VPN/mesh solution
- Gluetun on ARR stack
- Central application/database backup automation
- NAS-to-NAS/offline backup strategy
- Central notification path for monitoring failures
- Stable IP/DHCP-reservation inventory
- Ansible/Git Infrastructure as Code
- Proxmox/API-safe AI operations with approvals
- Metrics/host monitoring beyond current Uptime Kuma checks
- UPS integration/shutdown plan
- Central secrets-management approach

## Life/personal services not deployed

- LibreCloset
- Vaultwarden
- Workout app
- Price Ghost
- Nutrition/macro tracker
- Mom's custom inventory application
- Komga

## Home/automation projects not deployed

- Morning motivational-video delivery from curated Immich media
- Daily guitar-practice-song delivery from curated Immich media
- Instagram Share Sheet/download-to-selected-Immich-album workflow
- Reel-to-show/anime/movie identification and approved request workflow
- Jarvis/proactive personal content-delivery hub
- Jarvis as orchestrator for teams of specialized AI workers/developers
- Gospel Library content mirror/search integration, subject to permitted access methods
- Windows PC Wake-on-LAN, safe sleep control, and approved app launching
- ESPHome/Bluetooth proxy expansion
- Garage-door control and position sensing
- Energy, water, and gas monitoring
- Smart irrigation
- Camera/Frigate/presence automations
- 24/7 Ecosystem OS server edition integration

## Long-term hardware/projects

- AMD Ryzen AI Halo-class future server upgrade
- Raven Resonance framework watch for future AR glasses
- AR glasses and wearable hardware
- OBD vehicle diagnostics hardware integration
- Modernizing/reusing old devices and iPads

---

# 6. Explicit exclusions and constraints

Do not re-add these merely because they appeared in old backups/plans:

- Authentik
- AdGuard Home; use Pi-hole instead
- LazyLibrarian
- Beets
- Bindery
- Homepage
- Homarr
- Old Home Assistant backup; HA was intentionally rebuilt fresh

NetBird remains optional only if a better/more secure remote-access solution is not chosen.

Core design rules:

- Local-first operation where practical
- No silent destructive automation
- Approval for consequential infrastructure actions
- Big media/photos/documents on mounted storage; OS/appdata/databases on guest disks
- PBS protects guest disks; NAS data requires a separate file-backup strategy
- Keep Mom's VM/data separable and easy to move later
- Keep Gus's Immich isolated from Trevor's and Mom's data

---

# 7. Ordered implementation backlog

## Phase A — Address current risks

1. Design a second-copy migration/backup for Nova's RAID 0 data.
2. Copy Home Assistant full backup `c7271835` off-VM and refresh/confirm the stale `no_current_backup` repair issue clears before applying updates.
3. Expand Kuma beyond its single Gus Immich monitor to all critical public/internal services, then configure and test notifications.

## Phase B — Establish recoverability

1. Deploy PBS laptop.
2. Back up all ten Proxmox guests on a schedule.
3. Add prune, verify, and alert jobs.
4. Add app-level backups for Paperless, Actual, Mealie, NPM, ARR, media configs, Crafty, and Kuma.
5. Export OPNsense configuration off-VM.
6. Back up NAS-hosted important data separately from guest backups.
7. Run representative restore tests: one LXC, one Linux VM, HA, OPNsense config, one app database, and sample NAS files.

## Phase C — Stabilize addressing, storage, and security

1. Create DHCP reservations/static addresses for hosts, guests, and NAS devices.
2. Expand 148 GB in `xps-life` and 99 GB in `xps-media` when needed.
3. Review XPS's unused 1 TB WD disk and decide whether to reuse, wipe later, or leave untouched.
4. Review public NPM hosts and restrict administrative/sensitive services.
5. Review Nova DSM update/support path, QuickConnect, firewall services, SNMP, iSCSI, and unused packages.
6. Capture JK NAS hardware/RAID/SMART/snapshot/backup/UPS status when access is available.
7. Plan UPS-backed graceful shutdown.

## Phase D — Finish the original hosted-service plan

1. Mom inventory app when ready.
2. Komga.
3. Choose and deploy only the Life apps Trevor still wants: LibreCloset, Vaultwarden, workout, Price Ghost, nutrition tracker.
4. Create Heavy/Future Apps VM only when Frigate/WorkAdventure/Nextcloud work is ready.
5. Create Random/Test VM when a sandbox is needed.
6. Create Local AI helper only when a real workload justifies its resources.
7. Decide whether Gus should remain on `xps-life` or move to a dedicated guest.

## Phase E — Automation and Jarvis foundation

1. Keep this inventory current.
2. Introduce Ansible in read-only/dry-run mode.
3. Build backup/status alerts and safe recovery workflows.
4. Implement curated morning motivation and guitar delivery.
5. Implement iPhone Share Sheet to Immich.
6. Implement Reel identification and approved media-request flow.
7. Expand Home Assistant and secure PC-control automations.
8. Add the Jarvis orchestration/capability layer with scoped permissions, logs, approvals, and local-first behavior.

---

# 8. Audit unknowns to close later

- JK NAS model, RAID/filesystem, disk health, firmware, snapshots, backups, and UPS
- Nova NAS snapshot/data-scrubbing schedule, backup jobs, UPS, and detailed SMART test schedule
- Complete Uptime Kuma monitor list and notification channels
- Cloudflare DNS record inventory and proxy/DNS-only status
- OPNsense firewall/NAT rule inventory and off-device config export
- Exact service-update policy and current package security state
- Whether public services have MFA, strong unique credentials, and rate limiting where supported
- Which Life apps remain desired versus merely historical ideas
- Physical switch/AP/router/mesh inventory and UPS/power topology
- Raspberry Pi 5 and old laptop/device current roles

