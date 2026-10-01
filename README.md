# Trevor's HomeLab

This repository is the source of truth for Trevor Gardner's home server, network, services, storage, restoration progress, and future work.

> Latest targeted update: 2026-10-01 (America/Denver). Last broad live audit: 2026-08-17; older evidence still needs a fresh full-lab check.

## Current headline

The core XPS application VMs are online. The most recently verified stacks are:

- `xps-life`: Immich, Actual Budget, and Mealie
- `xps-arr`: qBittorrent, Prowlarr, Sonarr, Radarr, Seerr, Shelfarr, SoulSync, slskd, and Swiparr
- `xps-media`: Jellyfin, Audiobookshelf, Navidrome, and Sheets
- Network core known operating: OPNsense, Nginx Proxy Manager, Pi-hole, HomeLab Wi-Fi, public DNS, and HTTPS proxying

The Raspberry Pi is now the third HomeLab cluster node, `pve-pi`. It boots from microSD and uses its 480 GB USB SSD for guests. VM 104 (`pi-automation`, `10.50.0.200`) runs n8n and the Discord bot; VM 105 (`pi-llm`, `10.50.0.119`) holds the tested Ollama runtime and is intentionally stopped. Docker and application files have been removed from the Pi host.

Next: fresh/off-device guest backups, stable guest addresses, reboot recovery and monitoring, then Ansible and postponed services. See the ordered backlog in [Roadmap](docs/ROADMAP.md). This update reconciles supplied session evidence; it does not claim a fresh whole-lab audit.

## Documentation

- [Current state](docs/CURRENT_STATE.md) — what is verified, unverified, missing, or postponed
- [Architecture](docs/ARCHITECTURE.md) — hardware and VM/container layout
- [Network](docs/NETWORK.md) — subnets, routing, DNS, domains, exposure policy, and known IPs
- [Services](docs/SERVICES.md) — service inventory, hosts, ports, and status
- [Storage and backups](docs/STORAGE_BACKUPS.md) — NAS mounts, allocations, restore rules, and backup plan
- [Roadmap](docs/ROADMAP.md) — ordered backlog and longer-term projects
- [Automations roadmap](docs/AUTOMATIONS_ROADMAP.md) — personal, Home Assistant, content, and homelab automations
- [Jarvis and proactive AI](docs/JARVIS.md) — assistant architecture, capabilities, proactive behavior, trusted Gospel content, permissions, and implementation phases
- [Pi Proxmox runbook](docs/PI_PROXMOX.md) — SSD, ARM guests, migration, backups, and remaining checks
- [Runbook](docs/RUNBOOK.md) — safe operating and troubleshooting procedures
- [Decisions](docs/DECISIONS.md) — decisions that should not be repeatedly revisited

## Status vocabulary

- **Verified** — confirmed during the current restoration/audit with command output
- **Known operating** — recently observed working, but not fully audited in the current sweep
- **Needs verification** — previously restored or planned, but current health is not confirmed
- **Planned** — intended future work
- **Postponed** — intentionally deferred

## Safety rules

- Never commit passwords, API tokens, VPN keys, private keys, or CIFS credential contents.
- Inspect existing containers, Compose files, mounts, and backups before overwriting anything.
- Never use `docker compose down -v` during recovery unless data deletion is explicitly intended.
- Temporary backup mounts such as `/mnt/server` should be removed after a VM is restored.
- Permanent service mounts such as `/mnt/jknas` and `/mnt/nas` must remain.
