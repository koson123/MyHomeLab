# Storage and Backups

## Current mounts

### `xps-life`

Permanent:

```text
/mnt/jknas -> //192.168.40.147/main
```

Used by Trevor's Immich library. The CIFS credential file is `/root/.jknas-credentials`; never commit or print it.

Temporary `/mnt/server` was removed after restoration.

### `xps-arr`

Permanent media mount:

```text
/mnt/nas -> //10.50.0.113/Jellyfin
```

Temporary backup mount was last observed as:

```text
/mnt/server -> //192.168.40.147/main
```

Remove `/mnt/server` after the remaining restore work no longer needs it.

### `xps-media`

Permanent media mount:

```text
/mnt/nas -> //10.50.0.113/Jellyfin
```

There is no permanent `/mnt/server` entry. `/root/.nova-nas-credentials` exists for a temporary backup mount.

Safe temporary mount pattern:

```bash
sudo mkdir -p /mnt/server
sudo mount -t cifs //192.168.40.147/main /mnt/server \
  -o credentials=/root/.nova-nas-credentials,vers=3.0,uid=1000,gid=1000,file_mode=0664,dir_mode=0775,noperm
```

Unmount after use:

```bash
sudo umount /mnt/server
sudo rmdir /mnt/server
```

### `mini-mom`

Permanent Mom NAS mount:

```text
/mnt/moms-nas -> //192.168.40.147/main
```

Verified capacity: 11 TB total, 2.5 TB used, 8.0 TB available.

The Proxmox virtual disk and LVM physical volume are 64 GB/62 GB. Ubuntu's `ubuntu-vg` contains a 31 GB root logical volume plus 31 GB unallocated free extents. Root is 87% full, so the root LV/filesystem can be extended using existing volume-group space; no Proxmox disk enlargement or partition growth is required.

Observed root-space concentration: `/var` 13 GB (primarily `/var/lib`) and `/opt` 5.5 GB, including 5.4 GB in `/opt/mom/immich/postgres`. Docker also stores several large application images plus an approximately 824 MB Immich model-cache volume; there was no build cache.

## Backup location observed

```text
/mnt/server/TrevorServerDONTTOUCH/complete_backups/<vm-name>
```

Never overwrite a healthy live stack before inspecting:

- Active Compose files
- Container health and network modes
- Bind mounts and volumes
- Backup directory structure and timestamps
- NAS mounts and free space

## Backup plan

- Old laptop runs Proxmox Backup Server.
- Desired: weekly full-cluster backups through PBS.
- Also keep recoverable application-level backups of Docker data and important native services.
- Validate restores, not just backup job success.
- Preserve Nginx Proxy Manager data and certificates.
- Keep Home Assistant rebuild-from-scratch policy unless a newer explicit decision replaces it.
- Old Authentik data is not required.
- Keep only Pi-hole from older DNS stacks; do not restore AdGuard.
- Do not restore LazyLibrarian, Beets, Bindery, Homepage, or Homarr.
- NetBird backup is optional only if it is still useful; WireGuard is the current remote-access plan.

## Intended virtual-disk allocations

### Mini PC

| Workload | Intended allocation |
|---|---:|
| Mom VM | 64 GB |
| OPNsense | 64 GB |
| Home Assistant OS | 128 GB |
| Local LLM VM | 100 GB |
| Life-heavy VM | 100 GB |
| Random/testing VM | 30 GB |
| Game server VM | 200 GB |
| Gus Immich VM | 40 GB |
| Networking VM | 80 GB |
| Pi-hole CT | 8 GB |
| Uptime Kuma CT | 12 GB |
| Raspberry Pi test VM | TBD |
| **Total excluding test VM** | **826 GB** |

### XPS

| Workload | Intended allocation |
|---|---:|
| `xps-life` | 250 GB |
| `xps-arr` | 200 GB |
| `xps-media` | 200 GB |
| **Total** | **650 GB** |

The XPS allocations above supersede the older 100/120/100 GB plan. Recent `df -h /` output showed roughly 97 GB usable inside each XPS guest. Treat that as a guest partition/LVM/filesystem expansion issue until Proxmox confirms otherwise; it does not change the intended 250/200/200 GB allocations.

Large data such as Immich photos, media libraries, Frigate recordings, and large backups should primarily live on NAS storage rather than filling VM boot disks.

## Future storage work

- After service restoration, verify the Proxmox virtual-disk sizes for all three XPS VMs.
- Expand the Ubuntu partition, LVM physical volume/logical volume, and filesystem as appropriate so each guest can use its full assigned disk.
- Back up and inspect the exact block/LVM layout before running expansion commands.
- After the entire service restoration is stable, redesign Jellyfin/media storage for better efficiency and resilience. ZFS is a candidate, but the final choice must account for the actual disks, NAS hardware, RAM, backup strategy, and migration downtime.
