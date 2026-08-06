# Network

## Design

- The HomeLab runs on a dedicated network behind an OPNsense VM.
- Parent/home network and lab network are separated.
- Lab subnet currently observed: `10.50.0.0/24`.
- Parent-side NAS address observed: `192.168.40.147`.
- Services should keep working locally when the internet is unavailable wherever practical.

## Known addresses

| Address | Device/service | Confidence |
|---|---|---|
| `192.168.40.67` | `pve-mini` management address | Verified |
| `192.168.40.252` | `mini-mom` / VM 101 | Verified |
| `10.50.0.2` | `pve-mini` HomeLab-side address | Verified |
| `10.50.0.113` | Jellyfin/media SMB share | Verified by mounts |
| `10.50.0.118` | `mini-games` / VM 107 | Verified via guest agent |
| `10.50.0.126` | `xps-media` | Verified |
| `10.50.0.134` | `mini-dns` / CT 110 | Verified |
| `10.50.0.135` | Networking VM / Nginx Proxy Manager admin (`:81`) | Verified VM address; DHCP |
| `10.50.0.143` | `mini-monitoring` / CT 111 | Verified |
| `10.50.0.159` | `mini-ha` / VM 103 | Verified via guest agent |
| `10.50.0.152` | `xps-life` | Verified |
| `192.168.40.147` | Mom/Nova NAS SMB `main` share | Verified by mounts |
| `72.12.254.124` | Public address returned for `gardnergate.cc` subdomains | Observed 2026-08 |

Add DHCP reservations for infrastructure before treating addresses as permanent.

## DNS and reverse proxy

- Domain: `gardnergate.cc`
- Public DNS: Cloudflare
- Reverse proxy: Nginx Proxy Manager
- Internal DNS/filtering: Pi-hole
- HTTPS certificates and proxy definitions must be preserved during recovery.

Known public services/domains include:

- Jellyfin
- Audiobookshelf
- Navidrome
- Jellyseerr/Seerr
- Swiparr
- Sheets
- Immich
- Actual Budget
- Mealie (`mealie.gardnergate.cc`)

Mealie's working NPM settings:

- Scheme: HTTP
- Forward host: `10.50.0.152`
- Forward port: `9925`
- Force SSL: on
- Block Common Exploits: off
- WebSocket Support: off

## Exposure policy

### Public-facing

- Jellyfin
- Audiobookshelf
- Navidrome
- Jellyseerr/Seerr
- Swiparr
- Sheets

### Private/VPN-only target

- Proxmox
- Nginx Proxy Manager admin
- Sonarr
- Radarr
- Prowlarr
- qBittorrent admin
- Immich
- Shelfarr
- SoulSync/slskd
- Home Assistant administration
- Other admin panels

Some private targets may still be externally exposed today. Lock them down after WireGuard is working.

## VPN roles

Two VPN purposes must not be confused:

1. **WireGuard remote access** — free, hosted at home, lets Trevor's phone/laptop securely enter the HomeLab. Planned but not configured.
2. **Gluetun + commercial VPN** — outbound privacy for qBittorrent. Postponed because no paid provider has been selected.

WireGuard remote access does not hide qBittorrent's public IP.

## DNS observations and follow-up

A HomeLab client was observed using ISP IPv6 DNS `2605:5480:1f:160::1`. That resolver returned `NXDOMAIN` for Mealie during troubleshooting, while Cloudflare `1.1.1.1` resolved the hostname. However, Mealie began working only after Nginx Proxy Manager's **Block Common Exploits** and **WebSocket Support** options were disabled, so the incident must not be recorded as a proven DNS-caused outage.

Still audit OPNsense/Pi-hole DHCP and IPv6 router-advertisement settings so the intended DNS resolver is distributed consistently. Record the actual resolver configuration before changing it.

## Wi-Fi

- Goal: OpenWrt-based mesh/repeater system with seamless roaming
- Ethernet backhaul is unavailable for nodes
- Existing work: TP-Link TL-WR902AC V3.8 flashed with OpenWrt and configured to extend `HomeLab` using a relay bridge
- ASUS RT-N12 D1 was also integrated historically
- Travel router considered: GL.iNet Beryl AX (GL-MT3000)
- Longer-term interest: server-monitored mesh nodes and Bluetooth repeating
