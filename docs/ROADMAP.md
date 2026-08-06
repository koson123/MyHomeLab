# Roadmap

## Documentation audit — 2026-08-06

- [x] Reconcile XPS service status against supplied `docker`/mount/storage output.
- [x] Record corrected intended XPS allocations: 250 GB / 200 GB / 200 GB.
- [x] Separate verified, known-operating, needs-verification, planned, and postponed states.
- [x] Correct the Mealie incident record: working change was in Nginx Proxy Manager; DNS was an observation, not a proven root cause.
- [ ] Capture fresh Proxmox and guest evidence for every remaining unverified claim.

## Phase 1 — live inventory and finish service restoration

- [ ] Export both Proxmox node inventories: Mini-PC complete; XPS still required.
- [ ] Capture `lsblk`, LVM, filesystem, memory, mounts, Compose, and container health from all three XPS guests.
- [ ] Temporarily mount the backup NAS on `xps-media`.
- [ ] Search the `xps-media` backup for Komga.
- [ ] Restore or install Komga without touching the four healthy media services.
- [ ] Verify Komga library paths and HTTPS proxy.
- [ ] Remove temporary `/mnt/server` mounts from completed VMs.
- [ ] Re-check all XPS services after a reboot.

## Phase 2 — audit the mini-PC side

- [x] Inventory every existing mini-PC VM/CT, ID, IP, CPU, RAM, disk, network, and autostart setting.
- [ ] Verify OPNsense configuration and backups.
- [ ] Verify Nginx Proxy Manager, certificates, proxy hosts, and backup.
- [ ] Verify Pi-hole, upstream resolvers, DHCP integration, and persistence.
- [ ] Verify Uptime Kuma.
- [ ] Mom Immich and Paperless-ngx verified; verify/deploy the inventory app.
- [ ] Verify Home Assistant OS.
- [ ] Verify Crafty Controller and every game world.
- [ ] Verify Gus/friend Immich is separate from Mom's stack.
- [ ] Verify Proxmox Backup Server and recent backup jobs.

- [ ] Install and enable `qemu-guest-agent` in `mini-mom`.
- [ ] Expand `mini-mom`'s 31 GB root LVM/filesystem to use the 64 GB virtual disk.
- [ ] Detach stale installer ISOs from VMs after confirming normal disk boot.

## Phase 3 — reconcile VM storage

- [ ] Confirm Proxmox shows `xps-life` at 250 GB, `xps-arr` at 200 GB, and `xps-media` at 200 GB.
- [ ] Inspect the partition, LVM, and filesystem layout inside each XPS guest.
- [ ] Back up each VM before changing its storage layout.
- [ ] Expand each guest from roughly 97 GB usable to its full assigned virtual disk.
- [ ] Confirm services and mounts still work after expansion and reboot.

## Phase 4 — make networking durable

- [ ] Assign DHCP reservations/static addresses to infrastructure.
- [ ] Correct IPv4 and IPv6 DNS distribution to clients.
- [ ] Set up WireGuard remote access.
- [ ] Test WireGuard from phone and laptop outside HomeLab Wi-Fi.
- [ ] Move private/admin services to VPN-only access.
- [ ] Confirm public services remain reachable and HTTPS certificates renew.
- [ ] Document firewall, NAT, DNS, and port-forward rules.

## Phase 5 — monitoring and backups

- [ ] Add every VM, NAS, service, domain, and certificate to Uptime Kuma.
- [ ] Configure weekly PBS backups.
- [ ] Add application-aware backups for databases and Compose data.
- [ ] Perform sample restore tests.
- [ ] Document recovery time and dependencies for each critical service.

## Phase 6 — planned applications

- [ ] Vaultwarden
- [ ] LibreCloset
- [ ] Price Ghost
- [ ] Workout/fitness app
- [ ] Nutrition/macro tracker
- [ ] Frigate and local cameras
- [ ] WorkAdventure
- [ ] Local LLM/AI assistant VM
- [ ] Gridfinity/random project stack
- [ ] Nextcloud later

## Phase 7 — later infrastructure improvements

- [ ] Select an outbound commercial VPN before enabling Gluetun.
- [ ] Route only qBittorrent through Gluetun; keep ARR UIs locally reachable.
- [ ] Reassess `xps-arr` RAM due to swap pressure.
- [ ] Redesign Jellyfin/media storage, possibly with ZFS.
- [ ] Finish OpenWrt wireless mesh and seamless roaming.
- [ ] Explore local Bluetooth repeating through network nodes.
- [ ] Improve offline/local operation for Home Assistant and PC control.
