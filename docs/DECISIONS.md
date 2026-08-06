# Decisions

## Active decisions

### Virtualization and host roles

- Use Proxmox on the mini PC and Dell XPS.
- Use the old laptop as dedicated Proxmox Backup Server.
- Keep containers as containers where practical; use VMs for isolation and portability.
- Use OVMF/UEFI, Q35, QEMU guest agent, and SSD discard for normal VM builds.

### Network and access

- OPNsense is the lab router/firewall.
- Keep the lab on a separate network from the parent/home network.
- Use Pi-hole, not AdGuard.
- Use Nginx Proxy Manager for HTTPS reverse proxying.
- Use WireGuard for free remote access into the HomeLab.
- Do not confuse WireGuard remote access with an outbound privacy VPN.
- Delay Gluetun until a commercial VPN provider is selected.
- Private/admin services should become VPN-only after WireGuard is proven.
- Prefer local/offline operation when possible.

### Service placement

- Keep Mom's services together and easy to move.
- Keep Gus/friend Immich separate from Mom's services.
- Place Mom's VM on the parent-network side/in front of OPNsense when needed for simple NAS access.
- Crafty Controller is the game server manager.
- Home Assistant OS receives a dedicated VM.
- Nextcloud and Frigate are later workloads, not restoration blockers.

### Recovery

- Do not restore old Authentik.
- Keep old NetBird only as an optional reference if no better VPN is chosen.
- Do not restore AdGuard, LazyLibrarian, Beets, Bindery, Homepage, or Homarr.
- Build Home Assistant from scratch unless a newer explicit decision changes this.
- Do not redesign Jellyfin storage until the current service restoration is complete.

### Documentation

- This repository is the canonical homelab record.
- Status claims must distinguish verified, known operating, needs verification, planned, and postponed.
- Never store secrets in Git.
