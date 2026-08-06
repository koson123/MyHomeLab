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

## Planned disk allocations

| Workload | Planned allocation |
|---|---:|
| Home Assistant OS | 128 GB |
| Game server VM | 300 GB |
| Trevor Immich VM disk | 100 GB |
| Trevor Immich NAS data | 600 GB |
| Life Docker VM | 100 GB |

Treat these as planning targets, not verified current disk sizes.

## Future storage work

After the entire service restoration is stable, redesign Jellyfin/media storage for better efficiency and resilience. ZFS is a candidate, but the final choice must account for the actual disks, NAS hardware, RAM, backup strategy, and migration downtime.
