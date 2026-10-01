# Pi automation guest configuration

Latest update: October 1, 2026. The directory name `automation-01` is retained for existing links; the physical host is now `pve-pi` and applications run inside guests.

## Current placement

| Workload | Guest | Address | State |
|---|---|---|---|
| n8n and Discord bot | VM 104 `pi-automation` | `10.50.0.200` | Migrated and user-tested |
| Ollama / `qwen3:1.7b` | VM 105 `pi-llm` | `10.50.0.119` | Inference verified; intentionally stopped |
| Virtualization | Pi host `pve-pi` | `10.50.0.114` | HomeLab cluster member; host Docker removed |

Guests are Debian 13 ARM64 with 60 GB guest disks on the Pi's 480 GB USB SSD. The physical host still boots from microSD. DHCP reservations for guest addresses are not confirmed.

## Configuration examples

- `compose/n8n/compose.yaml` is a sanitized deployment example for VM 104.
- `compose/ollama/compose.yaml` is a sanitized deployment example for VM 105.
- These files are not a complete export of the live Compose configuration. Inspect live settings and credentials before replacing a working stack.
- The Discord bot uses a preserved custom image and its existing private project configuration; a sanitized reproducible build remains to be documented.
- n8n URL examples now use the guest IP. Check live webhook URLs/credentials and update consumers deliberately; no new internal DNS record or production LLM integration is confirmed.

## Paths inside the relevant guest

- Compose: `/srv/automation/compose/<project>`
- Persistent data: `/srv/automation/data/<service>`
- Secrets: `/srv/automation/secrets`

Only sanitized configuration belongs in Git. Secrets, application data, backups, custom image archives, and model files remain excluded.

## Operations and pending work

Ollama is available at `http://10.50.0.119:11434` when VM 105 is started. It is currently stopped to conserve RAM; verify autostart is disabled. n8n is at `http://10.50.0.200:5678`.

See [Pi Proxmox runbook](../../docs/PI_PROXMOX.md) for backups, commands, and remaining acceptance checks. Create a fresh post-split VM 104 backup and copy both guest archives off the SSD.

Ansible installation is still pending; recommended placement is VM 104 rather than the Pi virtualization host. Installing Ansible alone does not schedule updates.
