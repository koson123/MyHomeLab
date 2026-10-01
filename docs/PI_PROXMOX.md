# Pi Proxmox inventory and runbook

Latest evidence: September 30–October 1, 2026, supplied command output and user-confirmed application tests. This is a targeted record, not a fresh whole-lab audit.

## Host and storage

- Raspberry Pi 5, 8 GB RAM, `pve-pi` (formerly `automation-01`); Debian 13 ARM64, community PXVIRT port.
- Cluster HomeLab: `pve-mini` `10.50.0.2`, `pve-xps` `10.50.0.10`, `pve-pi` `10.50.0.114`; three votes, quorum two.
- Static `10.50.0.114/24` on `vmbr0`, gateway `10.50.0.1`. Proxmox UI: `https://10.50.0.114:8006`.
- Kernel `6.18.39+rpt-rpi-v8`, 4096-byte pages, selected with `kernel=kernel8.img` in `/boot/firmware/config.txt`; ARM guest boot and `/dev/kvm` verified.
- Root `/dev/mmcblk0p2` and firmware `/dev/mmcblk0p1` remain on microSD. Do not migrate host boot to SSD: Trevor chose guest storage only.
- Kingston SA400S37480G USB SSD, 480 GB nominal / 447.1 GiB reported: GPT, single ext4 partition `/dev/sda1`, label `PI_SSD`.
- UUID `48620556-fec8-4e07-9d7e-1f80a246e812`; fstab mount `/mnt/pve/pi-ssd`, options `defaults,noatime,nofail`, fsck pass 2.
- Proxmox directory storage `pi-ssd` limited to `pve-pi`, content `images,rootdir,iso,vztmpl,backup`, `is_mountpoint=1`.
- `local-lvm` limited to `pve-mini,pve-xps`; no `pve/data` exists on the Pi. `pi-local` still points to microSD at `/var/lib/pve-pi-vm`; select `pi-ssd` for new guest disks.
- `/etc/hosts` resolves `pve-pi` to `10.50.0.114`. `/etc/cloud/cloud.cfg.d/99-pve-hostname.cfg` sets `manage_etc_hosts: false` and `preserve_hostname: true`.

## Guests and applications

| VM | Name | DHCP address / MAC | Workload | Last state |
|---|---|---|---|---|
| 104 | `pi-automation` | `10.50.0.200` / `BC:24:11:2A:D8:6E` | n8n and Discord bot | Running; user-tested |
| 105 | `pi-llm` | `10.50.0.119` / `BC:24:11:F3:00:E8` | Ollama | Intentionally stopped |

Both guests use Debian 13 ARM64 cloud images, UEFI/AAVMF firmware, virtio networking on `vmbr0`, and 60 GB qcow2 disks on `pi-ssd`. VM 104's filesystem expansion was verified (`/dev/vda1`, about 59 GB). Guest-agent installation was recorded; VM 105 backup freeze/thaw confirms its agent responded. Verify final CPU/RAM/balloon/autostart settings with `qm config` before reallocating resources.

Application paths inside the respective guests:

| Application | Image / project | Persistent data | Endpoint |
|---|---|---|---|
| n8n | `docker.n8n.io/n8nio/n8n:2.36.9`; `/srv/automation/compose/n8n` | `/srv/automation/data/n8n` → `/home/node/.n8n` | `http://10.50.0.200:5678` |
| Discord bot | Preserved custom `discord-bot-discord-bot:latest`; `/srv/automation/compose/discord-bot` | Original container had no mounts and no writable-layer changes; preserve image and project configuration | Outbound bot |
| Ollama | `ollama/ollama:0.33.2`; `/srv/automation/compose/ollama` | `/srv/automation/data/ollama` → `/root/.ollama` | `http://10.50.0.119:11434` when started |

The Ollama override uses matching `cpus: 3.5` and `deploy.resources.limits.cpus: "3.5"`, plus a 3 GB memory limit and equal memory+swap limit. Keep CPU limits within the guest's available CPU count and avoid conflicting Compose/deploy values.

`qwen3:1.7b` model data was transferred; local inference returned a valid response. VM 104 could reach VM 105's tags API. This verifies runtime/connectivity, not that n8n or another production workflow uses it. Current LLM consumers remain unconfirmed.

## Completed migration and cleanup

- Initial copy followed by stopped-service final sync preserved ownership/permissions and Compose configuration.
- Exact images transferred, including the custom bot image.
- User confirmed n8n and bot work in VM 104.
- Ollama separately verified in VM 105, then its old container/project/model data removed from VM 104.
- Pi host Docker/containerd packages purged, then `/srv/automation`, `/var/lib/docker`, and `/var/lib/containerd` removed.
- Backups retained. Do not rerun formatting, reinstall Proxmox, or repeat host application cleanup.
- Run Docker commands inside the application guest, not the Pi host.

## Backup inventory and limits

| Archive | Verification | Limitation |
|---|---|---|
| `/var/backups/pimox-20260930-174227` | Original 1.5 GB backup; off-Pi Windows copy recorded during preparation | Original host layout |
| `/mnt/pve/pi-ssd/dump/vzdump-qemu-104-2026_10_01-00_51_27.vma.zst` | About 8.1 GB; successful backup log and `zstd -t` | Predates LLM split; former combined services |
| `/mnt/pve/pi-ssd/dump/vzdump-qemu-105-2026_10_01-17_12_39.vma.zst` | 7.12 GB; successful snapshot job with freeze/thaw | Same SSD as guest disk |

Next: fresh post-split VM 104 backup, off-device copies for both guests, scheduled coverage, and isolated restore tests. Compressed archive integrity does not establish an application restore. Do not delete these archives before replacement protection is verified.

When restoring the old VM 104 archive, isolate networking first: it contains the Discord bot and Ollama and can activate duplicate services. Use a new VM ID and inspect guest identity/networking before connecting it to production.

## Read-only host checks

Run on `pve-pi`:

```bash
hostname
getent hosts pve-pi
findmnt /
findmnt /mnt/pve/pi-ssd
pvesm status
pvecm status
systemctl is-active pvestatd pvedaemon pveproxy pve-cluster corosync
qm status 104
qm status 105
qm config 104
qm config 105
free -h
swapon --show
vmstat 1 5
```

Guest-agent checks:

```bash
qm agent 104 ping
qm agent 105 ping
```

VM 105's agent will not respond while intentionally stopped. Check its configuration without starting it solely for monitoring.

## On-demand LLM operation

Run on `pve-pi` to ensure it stays off after host reboot:

```bash
qm set 105 --onboot 0
qm config 105
```

Start only when a workload needs it:

```bash
qm start 105
```

Then check the API from a LAN client:

```bash
curl -fsS --max-time 15 http://10.50.0.119:11434/api/tags
```

Stop gracefully when finished:

```bash
qm shutdown 105 --timeout 60
qm status 105
```

Avoid force-stop while a model is writing/downloading. Reserve the guest's DHCP address and review n8n/bot clients before relying on this endpoint.

## Known issues and pending acceptance

- `pvestatd` failed early in boot with IPC Connection refused and caused Unknown node status. Restart restored Active. Check logs and ordering if it recurs; final completed-configuration host reboot is not verified.
- PXVIRT emits uninitialized-value multiplication warnings from `PVE/QemuServer.pm` lines 2862–2867 despite reporting guest state. A Cloudinit.pm line 115 warning was also observed. Preserve logs and verify affected metrics; do not claim fixed or patch vendor code blindly.
- Last memory sample: 7.8 GiB total, 5.1 GiB available, VM 105 stopped. Sole active swap was 2 GiB `/dev/zram0`, about 859 MiB used; later vmstat samples showed no swap traffic. This is compressed RAM swap, not microSD writes. Residual usage need not promptly fall while the host has ample memory.
- DHCP reservations for both guests and VM 105 `onboot=0` still require confirmation.
- Final controlled host reboot must verify SSD mount, cluster quorum, hostname, bridge, status daemon, VM 104 autostart/application health, and intentional VM 105 shutdown.
- Ansible remains pending. Proposed control environment: VM 104, keeping the host focused on Proxmox. Begin with inventory/check mode; updates require explicit playbooks, scheduling, and health checks.
