# Roadmap

## Phase 1 — finish service restoration

- [ ] Temporarily mount the backup NAS on `xps-media`.
- [ ] Search the `xps-media` backup for Komga.
- [ ] Restore or install Komga without touching the four healthy media services.
- [ ] Verify Komga library paths and HTTPS proxy.
- [ ] Remove temporary `/mnt/server` mounts from completed VMs.
- [ ] Re-check all XPS services after a reboot.

## Phase 2 — audit the mini-PC side

- [ ] Inventory every mini-PC VM/CT, ID, IP, CPU, RAM, disk, network, and autostart setting.
- [ ] Verify OPNsense configuration and backups.
- [ ] Verify Nginx Proxy Manager, certificates, proxy hosts, and backup.
- [ ] Verify Pi-hole, upstream resolvers, DHCP integration, and persistence.
- [ ] Verify Uptime Kuma.
- [ ] Verify Mom Immich, Paperless-ngx, and inventory app.
- [ ] Verify Home Assistant OS.
- [ ] Verify Crafty Controller and every game world.
- [ ] Verify Gus/friend Immich is separate from Mom's stack.
- [ ] Verify Proxmox Backup Server and recent backup jobs.

## Phase 3 — make networking durable

- [ ] Assign DHCP reservations/static addresses to infrastructure.
- [ ] Correct IPv4 and IPv6 DNS distribution to clients.
- [ ] Set up WireGuard remote access.
- [ ] Test WireGuard from phone and laptop outside HomeLab Wi-Fi.
- [ ] Move private/admin services to VPN-only access.
- [ ] Confirm public services remain reachable and HTTPS certificates renew.
- [ ] Document firewall, NAT, DNS, and port-forward rules.

## Phase 4 — monitoring and backups

- [ ] Add every VM, NAS, service, domain, and certificate to Uptime Kuma.
- [ ] Configure weekly PBS backups.
- [ ] Add application-aware backups for databases and Compose data.
- [ ] Perform sample restore tests.
- [ ] Document recovery time and dependencies for each critical service.

## Phase 5 — planned applications

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

## Phase 6 — later infrastructure improvements

- [ ] Select an outbound commercial VPN before enabling Gluetun.
- [ ] Route only qBittorrent through Gluetun; keep ARR UIs locally reachable.
- [ ] Reassess `xps-arr` RAM due to swap pressure.
- [ ] Redesign Jellyfin/media storage, possibly with ZFS.
- [ ] Finish OpenWrt wireless mesh and seamless roaming.
- [ ] Explore local Bluetooth repeating through network nodes.
- [ ] Improve offline/local operation for Home Assistant and PC control.
