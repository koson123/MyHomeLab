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

- [x] Install `qemu-guest-agent` in `mini-mom` and verify the service is active; confirm Proxmox-side agent response next.
- [x] Expand `mini-mom`'s root LVM/filesystem from approximately 31 GB to approximately 62 GB.
- [ ] Detach stale installer ISOs from VMs after confirming normal disk boot.

## Phase 3 — reconcile VM storage

- [ ] Confirm Proxmox shows `xps-life` at 250 GB, `xps-arr` at 200 GB, and `xps-media` at 200 GB.
- [ ] Inspect the partition, LVM, and filesystem layout inside each XPS guest.
- [ ] Back up each VM before changing its storage layout.
- [ ] Expand each guest from roughly 97 GB usable to its full assigned virtual disk.
- [ ] Confirm services and mounts still work after expansion and reboot.

## Phase 4 — make networking durable

- [ ] Give all permanent homelab infrastructure stable IP addresses later, using documented static assignments and/or DHCP reservations as appropriate; cover Proxmox hosts, VMs/CTs, NAS devices, Raspberry Pis, network infrastructure, and other long-lived servers/services.
- [ ] Create and maintain a documented IP/address allocation map so new infrastructure does not conflict with existing assignments.
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
- [ ] Local LLM/AI assistant VM running the modular homelab Jarvis foundation described in [JARVIS.md](JARVIS.md)
- [ ] Trusted local Gospel Content Library sourced from official Church content for Jarvis search, study, audio, and automations
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

## Phase 8 — centralized Infrastructure as Code and automation

Implement this only after the homelab architecture, addressing, service placement, storage, and backup strategy are stable enough that automation will not be constantly rewritten.

- [ ] Establish an Ansible control node for centralized homelab administration.
- [ ] Keep inventories, playbooks, roles, templates, and non-secret configuration under Git version control.
- [ ] Group managed systems by role, including Proxmox hosts, Mini-PC VMs/containers, XPS VMs, Raspberry Pis, networking/services, media, games, and experimental nodes.
- [ ] Automate Linux package updates and routine maintenance across supported nodes.
- [ ] Automate software/package deployment and baseline machine configuration.
- [ ] Automate Docker/Compose deployment and controlled service restarts where appropriate.
- [ ] Automate user accounts, SSH keys, sudo policy, and host-access configuration.
- [ ] Automate repeatable firewall and network configuration where safe and supported.
- [ ] Automate configuration backups and validation of expected machine state.
- [ ] Integrate Proxmox API workflows for repeatable VM/CT provisioning and lifecycle actions where they provide an advantage over SSH-only automation.
- [ ] Add dry-run/check-mode, staged rollouts, backups, and explicit safeguards before broad or destructive changes.
- [ ] Build health checks and post-change verification so playbooks confirm services actually return to a healthy state.
- [ ] Document one-command runbooks for common tasks such as `update all Linux nodes`, `deploy a service`, `rotate an SSH key`, and `restart a stack`.
- [ ] Design the automation layer so the future Ecosystem AI can invoke approved playbooks through a constrained interface instead of receiving unrestricted shell/root access.

## Phase 9 — Jarvis music and Spotify-like experience

This is a future music-system upgrade, separate from the automations roadmap. The goal is to make Trevor's self-hosted music experience feel more like Spotify while keeping the library and core playback local-first.

- [ ] Upgrade the music side around Navidrome and its Subsonic-compatible API, with SoulSync supporting the planned acquisition/import workflow.
- [ ] Make the Jarvis Music dashboard the primary music interface while retaining Feishin as a manual/browser player.
- [ ] Let the local LLM/Jarvis understand natural-language music requests based on mood, activity, genre, energy, era, similarity, or a description of what Trevor wants to hear.
- [ ] Let Jarvis find exact songs, artists, albums, and existing playlists and start background playback on approved devices.
- [ ] Create and maintain personalized playlists from Trevor's library, including mood mixes, activity mixes, rediscovery playlists, favorites, recently added music, and guitar-practice playlists.
- [ ] Use favorites, skips, repeats, listening history, playlist edits, and explicit feedback to improve recommendations.
- [ ] Balance familiar music, rediscovery, and exploration while preventing generated playlists from becoming repetitive.
- [ ] Recommend music already in the library and identify missing songs or artists for Trevor to review before importing.
- [ ] Keep deterministic search, playlist storage, and ordinary playback functional without the LLM or external internet.
- [ ] Eventually expose the same music controls through Trevor's desktop, phone, Home Assistant, Roku/media devices where supported, and Jarvis interfaces.

### Future transition into Ecosystem OS

Jarvis begins as an independent homelab assistant so it can be useful long before Ecosystem OS is ready. Once Ecosystem OS has a mature intelligence service, capability system, permissions, device integration, and Server Edition, migrate or port Jarvis into Ecosystem rather than maintaining two competing assistants.

- [ ] Keep Jarvis interfaces and homelab integrations modular enough to migrate later.
- [ ] Preserve Jarvis's established music, media, Home Assistant, Immich, file-finding, and homelab abilities during the transition.
- [ ] Map Jarvis actions to Ecosystem's typed capabilities, permissions, confirmations, and audit records.
- [ ] Give the Ecosystem version deeper system and device control, broader context, and more user-approved autonomy than the standalone homelab version can safely have.
- [ ] Retire or reduce the standalone Jarvis only after the Ecosystem version reaches feature parity and the migration is verified.

## Phase 10 — Jarvis core, proactive AI, and trusted Gospel content

Implement the detailed architecture and phased plan in [JARVIS.md](JARVIS.md).

- [ ] Build Jarvis as a modular homelab service in the planned 100 GB `mini-llm` VM.
- [ ] Start with an authenticated deterministic core, typed capabilities, policy/approvals, audit logs, dashboard, and kill switch.
- [ ] Connect Home Assistant, the Personal Morning Delivery Hub, Immich, notifications, workouts, music/media, and read-only homelab status in controlled phases.
- [ ] Add proactive behavior through explicit event rules, quiet hours, cooldowns, acknowledgement, deduplication, and per-rule disable controls.
- [ ] Build the trusted local Gospel Content Library from official Church sources with metadata, citations, offline search, update previews, and selected downloadable audio/video.
- [ ] Add a local LLM only as a replaceable interpretation, retrieval, summary, recommendation, and planning component; keep execution and permissions outside the model.
- [ ] Add voice and distributed panels after measuring hardware and selecting the wake-word, speech-to-text, and text-to-speech stack.
- [ ] Preserve portable contracts and data so the proven homelab Jarvis can later migrate into Ecosystem OS.

## Related roadmaps

- [Automations Roadmap](AUTOMATIONS_ROADMAP.md) — personal routines, Home Assistant workflows, content pipelines, and later homelab automation.
