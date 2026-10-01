# Storage and Backups

## Pi storage and backups — October 1, 2026

- Host root remains `/dev/mmcblk0p2` on microSD; firmware remains `/dev/mmcblk0p1`. The SSD is not the boot drive.
- Entire Kingston SSD is one GPT/ext4 partition, `/dev/sda1`, label `PI_SSD`, UUID `48620556-fec8-4e07-9d7e-1f80a246e812`, mounted at `/mnt/pve/pi-ssd`.
- Proxmox `pi-ssd`: directory storage limited to `pve-pi`, supports images/rootdir/ISO/templates/backups, `is_mountpoint=1`. This prevents storage activation on an unmounted directory on microSD.
- VM 104 and 105 each have a 60 GB guest disk here. `pi-local` still points to `/var/lib/pve-pi-vm` on microSD; do not select it for new VM disks.
- `local-lvm` is restricted to `pve-mini,pve-xps` because the Pi has no `pve/data` thin pool.
- VM 104 backup: `dump/vzdump-qemu-104-2026_10_01-00_51_27.vma.zst`, about 8.1 GB; successful log and `zstd -t` confirmed. **Predates the LLM split** and contains the former all-three-service layout.
- VM 105 backup: `dump/vzdump-qemu-105-2026_10_01-17_12_39.vma.zst`, 7.12 GB; snapshot completed with guest-agent freeze/thaw.
- Original pre-migration backup retained at `/var/backups/pimox-20260930-174227`; off-Pi Windows copy was recorded during preparation.
- Both VM archives currently reside on the same SSD as the guest disks. A fresh post-split VM 104 backup, off-device VM archive copies, schedules, and restore tests remain required.
- Restore the old VM 104 archive on an isolated network: it includes the old Ollama copy and bot, so avoid duplicate bot activation or conflicting service addresses.

See [PI_PROXMOX.md](PI_PROXMOX.md) for checks and recovery commands.

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

The Proxmox virtual disk and LVM physical volume are 64 GB/62 GB. On 2026-08-06, the root logical volume and ext4 filesystem were expanded online from approximately 31 GB to approximately 62 GB using the existing free extents in `ubuntu-vg`. No Proxmox disk enlargement or partition growth was required. After expansion, `/` reported 61 GB usable, 25 GB used, 34 GB available, and 44% usage.

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

- Old laptop is designated for Proxmox Backup Server; verify current installation, datastore, and coverage before changing it.
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
| Raspberry Pi test VM on mini (optional) | TBD |
| **Total excluding test VM** | **826 GB** |

### Pi (separate from mini allocation)

| Workload | Guest disk | Storage |
|---|---:|---|
| VM 104 / `pi-automation` | 60 GB | `pi-ssd` |
| VM 105 / `pi-llm` | 60 GB | `pi-ssd` |

Local backups share this SSD; they are not an independent protected copy.

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
