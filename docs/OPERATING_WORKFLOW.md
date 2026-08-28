# Homelab Operating Workflow

Last updated: August 27, 2026

## Purpose

Create a repeatable way to operate, document, troubleshoot, and automate the homelab without losing important context between sessions. The repository should be the durable source of truth rather than depending on conversational memory.

## Core operating rule

Before adding major new services or infrastructure, reconcile the real running environment with the documentation. After each meaningful work session, update the repository so the next session can resume from verified facts rather than assumptions.

## Session-start workflow

At the beginning of a serious homelab session:

1. Read `CURRENT_STATE.md` for the latest verified state.
2. Read the top priority/current phase in `ROADMAP.md`.
3. Check `SERVICES.md`, `ARCHITECTURE.md`, `NETWORK.md`, and `STORAGE_BACKUPS.md` for dependencies relevant to the task.
4. Check `DECISIONS.md` before changing an architectural choice that may already have been settled.
5. Check `AUTOMATIONS_ROADMAP.md` when the work affects automation, Jarvis, notifications, recovery, or scheduled behavior.
6. Verify the live system before assuming documentation is still correct when the task is operationally significant.
7. Work in dependency order and avoid starting unrelated new work until the current bounded task reaches a clear stopping point.

## Session-end workflow

At the end of a meaningful homelab session:

1. Record what was actually changed.
2. Record what was verified healthy and what remains unverified.
3. Update service, VM/container, storage, network, and backup status where applicable.
4. Record new architectural decisions in `DECISIONS.md` when appropriate.
5. Update `ROADMAP.md` checkboxes and the immediate next actions.
6. Update `CURRENT_STATE.md` with the newest verified reality.
7. Record blockers, risks, exact commands or paths needed for continuation, and anything that must not be repeated.
8. Leave a clear next-action sequence so the next session can resume without reconstructing the project from chat history.

## Immediate full-server reconciliation pass

This is the next major homelab task before broad new expansion.

### 1. Physical and virtualization inventory

- Verify every physical server, NAS, Raspberry Pi, network appliance, UPS-capable device, and other always-on node.
- Verify both Proxmox hosts and any backup host.
- Enumerate every VM and LXC, including ID, name, host, CPU, RAM, virtual disk, network, IP, autostart setting, and purpose.
- Identify abandoned, duplicate, stale, or undocumented guests.

### 2. Service inventory and health

- Enumerate every Docker/Compose stack, native service, appliance service, and externally exposed endpoint.
- Compare the live inventory against `SERVICES.md`, `CURRENT_STATE.md`, and the roadmap.
- Identify services that should be running but are stopped, missing, unhealthy, obsolete, or intentionally postponed.
- Verify application health rather than only process/container state.
- Verify databases, queues, mounts, storage paths, certificates, and persistent-data paths used by each critical service.

### 3. Dependency and interconnection audit

For every service, record and verify its important dependencies, including:

- DNS and hostnames.
- Reverse proxy and TLS.
- Storage/NAS mounts.
- Databases and caches.
- Authentication where applicable.
- Home Assistant links.
- ARR/media relationships.
- Jellyfin and media-library relationships.
- Immich storage and database relationships.
- Monitoring targets.
- Backup targets.
- Notification paths.
- Jarvis/automation integrations.

Where two systems are intended to interoperate but are not currently connected, explicitly track the missing integration and the dependency order needed to implement it.

### 4. Networking audit

- Verify IPs, DHCP/static assignments, gateways, DNS, VLANs, firewall rules, NAT/port forwards, VPN policy, and reverse-proxy routes.
- Eliminate undocumented address assumptions.
- Record intended public, VPN-only, LAN-only, IoT-local-only, and IoT-cloud exposure classes.
- Confirm external-access policy matches the actual configuration.

### 5. Storage, backup, and recovery audit

- Verify every NAS/share/mount used by the homelab.
- Verify filesystem capacity and failure risks.
- Verify which data is irreplaceable versus reproducible.
- Verify PBS coverage and application-aware backups.
- Identify anything important with no off-host or second copy.
- Perform restore tests for representative critical workloads.
- Document dependency-aware recovery order.

### 6. Monitoring and observability audit

- Ensure every important host, VM/CT, service, domain, certificate, storage dependency, backup job, and critical automation has an appropriate health signal.
- Configure actionable notifications instead of collecting silent dashboards.
- Distinguish between process-up, service-healthy, dependency-healthy, and end-to-end-user-working checks.

## Automation strategy

The long-term goal is to automate as much routine homelab operation as is practical while preserving human control for consequential actions.

### Automate by default when low risk and reversible

Examples:

- Health checks and status collection.
- Inventory generation and drift detection.
- Backup execution and verification.
- Certificate/endpoint monitoring.
- Storage-capacity warnings.
- UPS power-failure handling and graceful shutdown sequencing.
- Routine report generation.
- Safe container/service restart after bounded health checks.
- Configuration validation.
- Package/update discovery and staged maintenance preparation.
- Post-change verification.

### Require human approval for consequential actions

Examples:

- Destructive storage operations.
- Firewall or exposure changes that could open services publicly.
- Deleting data, VMs, containers, backups, or snapshots.
- Broad production updates with meaningful outage risk.
- Credential/security-policy changes.
- Major network topology changes.
- Automatic remediation after repeated or ambiguous failures.
- Any action where the system cannot confidently determine blast radius.

### Preferred automation architecture

1. Git repository stores desired state, inventory, runbooks, and non-secret configuration.
2. Monitoring detects drift, failure, capacity problems, and backup issues.
3. Ansible or another deterministic automation layer performs repeatable infrastructure tasks.
4. Proxmox, Docker/Compose, Home Assistant, NUT, and service APIs are used through constrained interfaces rather than unrestricted remote shell where practical.
5. Jarvis becomes an orchestration and natural-language layer over approved typed actions, not an unrestricted root user.
6. Every consequential automated action has logs, clear inputs, result verification, and a failure/rollback path.
7. Human approval is requested only at defined decision gates rather than for every harmless read or health check.

## Source-of-truth hierarchy

When sources disagree, prefer them in this order:

1. Freshly verified live-system evidence.
2. `CURRENT_STATE.md` after it has been updated from that evidence.
3. Architecture/service/network/storage documents.
4. Roadmap and planned-state documents.
5. Old conversation history or unverified assumptions.

## Definition of a healthy operating state

The homelab should eventually reach a state where:

- Every physical node and guest has a documented purpose.
- Every intended service is either healthy, intentionally stopped, or explicitly planned/postponed.
- Dependencies and integrations are documented and tested.
- Important services have monitoring, backups, and recovery instructions.
- Networking and exposure policy are explicit and reproducible.
- Major configuration is represented in Git and increasingly managed as code.
- Routine maintenance and recovery are automated where safe.
- Consequential actions have deliberate human approval gates.
- A new work session can determine the real current state and next actions by reading the repository instead of reconstructing the project from memory.
