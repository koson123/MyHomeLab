# automation-01

Portable automation and lightweight AI node currently hosted on a Raspberry Pi 5.

## Current host

- Hostname: `automation-01`
- Address: `10.50.0.114`
- Architecture: ARM64
- Operating system: Debian 13
- Application root: `/srv/automation`

## Services

| Service | Purpose | Internal endpoint |
|---|---|---|
| n8n | Automation workflows | `http://automation-01.local:5678` |
| Ollama | Local lightweight LLM API | `http://10.50.0.114:11434` |

Ollama currently uses `qwen3:1.7b`, loads models only when requested, and unloads them afterward.

## Storage layout

- Compose definitions: `/srv/automation/compose`
- Persistent application data: `/srv/automation/data`
- Secrets: `/srv/automation/secrets`
- Backups: `/srv/automation/backups`

Only sanitized configuration belongs in Git. Secrets, live application data, backups, and model files must remain excluded.

## Migration design

The node is designed to move later from ARM64 Raspberry Pi hardware to an x86-64 Proxmox VM:

1. Provision Debian or Ubuntu with Docker.
2. Restore `/srv/automation/data` and secrets from backups.
3. Copy or clone these Compose definitions.
4. Pull images compatible with the new architecture.
5. Start the stacks with Docker Compose.
6. Update internal DNS or reverse-proxy records.
7. Verify workflows before retiring the Pi deployment.
