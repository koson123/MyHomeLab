# Trevor's HomeLab

This repository is the source of truth for Trevor Gardner's home server, network, services, storage, restoration progress, and future work.

> Last documentation audit: 2026-08-06 (America/Denver)

## Current headline

The core XPS application VMs are online. The most recently verified stacks are:

- `xps-life`: Immich, Actual Budget, and Mealie
- `xps-arr`: qBittorrent, Prowlarr, Sonarr, Radarr, Seerr, Shelfarr, SoulSync, slskd, and Swiparr
- `xps-media`: Jellyfin, Audiobookshelf, Navidrome, and Sheets
- Network core known operating: OPNsense, Nginx Proxy Manager, Pi-hole, HomeLab Wi-Fi, public DNS, and HTTPS proxying

The immediate next task is a live infrastructure audit, beginning with the Proxmox inventories and then restoring/installing Komga on `xps-media`. Documentation is internally reconciled, but items marked **Needs verification** are not considered confirmed until live command output is collected.

## Documentation

- [Current state](docs/CURRENT_STATE.md) — what is verified, unverified, missing, or postponed
- [Architecture](docs/ARCHITECTURE.md) — hardware and VM/container layout
- [Network](docs/NETWORK.md) — subnets, routing, DNS, domains, exposure policy, and known IPs
- [Services](docs/SERVICES.md) — service inventory, hosts, ports, and status
- [Storage and backups](docs/STORAGE_BACKUPS.md) — NAS mounts, allocations, restore rules, and backup plan
- [Roadmap](docs/ROADMAP.md) — ordered backlog and longer-term projects
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
