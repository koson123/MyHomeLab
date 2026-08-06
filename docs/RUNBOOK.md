# Runbook

## Proxmox inventory check

Run on each Proxmox node before changing VM allocations:

```bash
hostname
pveversion
pvesh get /cluster/resources --type vm --output-format json-pretty
pvesm status
ip -brief address
ip -brief link
```

For each VM/CT, record its ID, name, running state, CPU, RAM, configured disks, network bridge, and startup policy. Do not treat a planned disk size as actual until Proxmox configuration confirms it.

## Ubuntu storage-layout check

Run inside each XPS guest before any disk expansion:

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
sudo pvs
sudo vgs
sudo lvs -a -o +devices
df -hT
```

Back up the VM before resizing partitions, LVM, or filesystems.

## Basic VM health check

```bash
hostname
hostname -I
df -h /
free -h
docker version
docker compose version
docker compose ls
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker ps -a --filter status=exited
docker ps --filter status=restarting
findmnt
```

## Safe restoration order

1. Inspect the running VM.
2. Inspect Compose paths, containers, mounts, volumes, and timestamps.
3. Mount backup storage temporarily.
4. Inspect the exact backup structure.
5. Stop only the service being restored.
6. Copy to a staging directory when practical.
7. Preserve ownership and permissions.
8. Start and inspect logs.
9. Test locally by IP and port.
10. Test through Nginx Proxy Manager/HTTPS.
11. Verify old accounts/data before declaring success.
12. Remove the temporary backup mount.

## Nginx Proxy Manager troubleshooting

An error class identifies the layer:

- `ERR_NAME_NOT_RESOLVED`: DNS resolution problem; compare system DNS with `1.1.1.1`.
- `502 Bad Gateway`: DNS/proxy reached, but upstream service/port/network failed.
- Certificate warning: proxy certificate or DNS validation issue.
- Local IP works but domain does not: inspect DNS and NPM.
- Domain works off-network but not on HomeLab: inspect internal DNS/hairpin NAT.

Useful client checks:

```powershell
ipconfig /flushdns
nslookup service.gardnergate.cc
nslookup service.gardnergate.cc 1.1.1.1
```

For Mealie specifically, Block Common Exploits and WebSocket Support had to be disabled in NPM.

## When SSH is unavailable

- Confirm the client is connected to the HomeLab Wi-Fi.
- Open the VM's Proxmox console.
- Confirm the VM is running.
- Use graceful Shutdown then Start if the console is frozen.
- Avoid force Stop unless graceful shutdown fails.

## Docker safety

Do not run during recovery without an explicit data-deletion decision:

```bash
docker compose down -v
docker system prune --volumes
```

Do not reinstall a working platform simply because a proxy or DNS check fails.

## Secret handling

Never paste or commit:

- `.env` contents
- CIFS/SMB passwords
- VPN private keys
- Cloudflare API tokens
- GitHub tokens
- NPM database credentials
- Home Assistant long-lived tokens

It is safe to document credential file paths, but not their contents.

## Change log practice

After each work session, update:

- `CURRENT_STATE.md` with verified changes
- `SERVICES.md` for ports/hosts/storage
- `NETWORK.md` for addresses and exposure
- `ROADMAP.md` checkboxes
- `DECISIONS.md` for lasting choices
