# Trevor's Automations Roadmap

Last updated: August 16, 2026

## Purpose

Build a local-first automation layer connecting Trevor's homelab, Immich, Home Assistant, personal routines, media systems, and eventually Ecosystem OS. Automations should be reliable, private, auditable, and easy to override.

## Core rules

- Local-first: important routines must still work when the external internet is down.
- Human approval for consequential infrastructure actions.
- Curated personal media is trusted before automatically sourced internet content.
- No silent destructive actions; keep logs and provide clear failure reports.
- Store credentials with the minimum permissions needed.
- Avoid duplicates and preserve original files and metadata when archiving media.

## Phase 1 — Personal daily automations

### Personal Morning Delivery Hub

Status: Planned; expanded August 16, 2026 from the original morning motivation and guitar-practice automation requested August 6, 2026.

Goal: use the homelab as Trevor's personal morning launch system. It should help him wake up and get out of bed, provide the correct workout for that day, and deliver a short useful briefing without overwhelming him.

Every morning, deliver:

1. The correct workout for that day based on Trevor's current training plan, weekly rotation, recovery needs, equipment, and recent completion history.
2. One motivational video selected from Trevor's designated Immich motivation location.
3. One song to practice on guitar selected from Trevor's designated Immich guitar-practice location.
4. A concise morning information briefing containing only the modules Trevor approves.
5. A wake-up sequence designed to help Trevor actually get out of bed; the exact mechanism still needs to be designed and tested.

Workout requirements:

- Keep the active workout plan and weekly schedule in a structured source the server can read.
- Select the planned hard workout, recovery session, or rest/recovery variant for the correct day.
- Account for completed, missed, moved, or intentionally skipped sessions without silently doubling workouts.
- Present the exercises, sets, reps, rest periods, and any relevant warm-up or mobility work clearly.
- Allow Trevor to mark the workout started, completed, modified, skipped, or moved.
- Preserve completion history so Jarvis can report consistency and help adjust future plans after Trevor approves changes.

Wake-up assistance requirements:

- Explore a staged local wake-up routine using approved devices such as phone notifications, speakers, lights, blinds, Home Assistant devices, or a physical confirmation action.
- Begin gently, then escalate only through methods Trevor has explicitly enabled.
- Detect acknowledgement and stop the sequence once Trevor is genuinely up rather than continuing unnecessarily.
- Avoid unsafe, excessively disruptive, or impossible-to-disable behavior.
- Keep a simple backup alarm independent from the homelab so a server outage cannot cause Trevor to oversleep.

Morning briefing candidates:

- Current time, date, weather, and only schedule information relevant to the morning.
- Today's workout and first important responsibility.
- A short scripture, spiritual prompt, or reminder to pray and study.
- Important Home Assistant or homelab alerts that actually require Trevor's attention.
- A concise progress or accountability reminder based on his approved goals.
- Trevor will choose the final modules, ordering, delivery device, and maximum length before implementation.

Motivation and guitar requirements:

- Use the curated Immich collections as the authoritative source.
- Track delivery history so items do not repeat too frequently.
- Allow favorites, skips, difficulty, mood, and "show this again" feedback.
- Prefer guitar songs appropriate to Trevor's current ability, then gradually increase difficulty.
- If either collection is empty, report that clearly instead of substituting unreviewed internet content.

Later internet-discovery extension:

- Search for candidate motivational videos and guitar songs.
- Put candidates into an Immich review queue rather than delivering them automatically.
- Trevor approves or rejects each candidate.
- Only approved items enter the trusted daily rotation.
- Use approval history to rank future candidates, without treating an algorithm's idea of "motivational" as authoritative.

### Instagram saves to Immich

Status: Planned; added August 15, 2026.

Goal: archive selected Instagram Reels into Immich and organize them by purpose.

Recommended first version:

- Use an iPhone Share Sheet shortcut such as **Save to Immich**.
- Before downloading, show a menu that lets Trevor choose which Immich saved collection or album the Instagram video should go into.
- Populate the menu from Trevor's configured destinations, such as Projects, Motivation, Fitness, Ideas, and Funny, and include a safe way to add or select another destination.
- Send the Reel URL to a private homelab webhook.
- Download the permitted media, preserve its source URL and creator information, check for duplicates, and upload it to the selected Immich album.
- Remember the last-used destination for convenience, but always allow Trevor to change it before saving.
- Keep the webhook private through the internal network or VPN.

Possible later version:

- Investigate monitoring actual Instagram saved collections through an authenticated browser.
- Treat this as experimental because Instagram does not officially expose saved collections through its API; it would be fragile and could trigger account-security checks.

## Phase 2 — Home and device routines

### Home Assistant automation hub

Status: Planned foundation.

- Make Home Assistant the first-class bridge for hardware, sensors, cameras, media, scenes, and routines.
- Support presence-aware workflows and live events.
- Create and troubleshoot automations conversationally through the Ecosystem assistant.
- Keep local control available and record automation actions for auditing.

### PC power and launch control

Status: Planned.

- Wake the Windows PC using Wake-on-LAN through Home Assistant.
- Put the PC to sleep through a local authenticated agent or Home Assistant integration.
- Later, allow approved commands to open applications or perform defined desktop routines.
- An ESP32 keyboard-emulation device was considered, but a secure local PC agent should be evaluated first.
- Must continue working on the local network when internet access is unavailable.

### ESPHome and physical-home projects

Status: Later projects identified in existing plans.

- ESPHome devices and Bluetooth proxies.
- Garage-door control and position reporting.
- Whole-home energy monitoring and water/gas metering.
- Smart irrigation through MQTT/Home Assistant.
- Camera and presence events feeding safe household routines.

## Phase 3 — Homelab operations

### Ansible infrastructure as code

Status: Later phase, after the core homelab is stable.

- Centrally update Linux servers, Proxmox VMs/containers, and services.
- Deploy software and Docker Compose stacks.
- Manage users, permissions, and configuration consistently.
- Store playbooks and configuration in Git.
- Integrate with the Proxmox API, monitoring, and backups.
- Let the Ecosystem AI assistant propose or trigger safe actions with approval controls and failure reporting.

### Network-address foundation

Status: Planned prerequisite.

- Assign stable IPs or DHCP reservations to infrastructure devices and services.
- Maintain a single inventory used by DNS, monitoring, Ansible, backups, and documentation.

### Backup automation

Status: Planned/partially available.

- Schedule Proxmox Backup Server backups for the cluster.
- Back up Docker application data and native service data.
- Verify backup completion and report failures.
- Add periodic restore tests instead of assuming a successful backup is usable.

### Service health and recovery

Status: Planned direction.

- Monitor services and infrastructure with Uptime Kuma and system metrics.
- Notify Trevor when a service fails.
- Permit only explicitly approved low-risk automatic recovery, such as restarting a known container after health checks.
- Escalate repeated failures instead of creating restart loops.

## Phase 4 — Existing automated content pipelines

These are operational workflows to preserve and eventually manage from the same dashboard:

- Immich phone uploads, media processing, and backup monitoring.
- Paperless-ngx consume-folder import, OCR, and duplicate handling.
- Sonarr/Radarr/Prowlarr/qBittorrent media workflow with qBittorrent forced through Gluetun and its kill switch.
- Music and audiobook importing workflows through the planned media services.
- Periodic Immich/NAS integrity and storage-capacity checks.

## Phase 5 — Ecosystem-wide intelligence

Status: Long-term architecture.

- Provide one secure capability layer shared by voice, text, GUI, accessibility tools, and automations.
- Connect reminders, media control, file finding, device control, Home Assistant, and homelab actions.
- Use typed actions, scoped permissions, confirmations, logs, and undo/recovery where possible.
- Coordinate automations across the 24/7 server edition of Ecosystem OS and Trevor's personal devices.

## Watch and monitoring automations

Status: Future.

- Monitor the Raven Resonance `raven-framework` project for meaningful releases or changes relevant to the planned AR glasses.
- Monitor important self-hosted projects for security advisories and breaking releases before upgrades.
- Track infrastructure capacity so planned hardware upgrades, including a future AMD Ryzen AI Halo server option, can be evaluated when they become relevant.

## Recommended implementation order

1. Define the structured workout-plan source, approved briefing modules, wake-up stages, and delivery devices for the Personal Morning Delivery Hub.
2. Confirm the two existing Immich locations for motivation and guitar media.
3. Build and manually test the workout selector, morning briefing, motivation/guitar selector, history tracking, and acknowledgement flow.
4. Add the iPhone **Save to Immich** Share Sheet workflow.
5. Establish stable network addresses and a maintained infrastructure inventory.
6. Finish dependable backup schedules, alerts, and restore testing.
7. Expand Home Assistant routines and secure PC control.
8. Introduce Ansible with read-only inventory and dry runs before approved changes.
9. Add reviewed internet discovery for motivation and guitar content.
10. Connect everything to the Ecosystem assistant and unified dashboard.

## Decisions still needed

- Exact structured source for the active workout plan and how plan changes are approved.
- Which wake-up devices and escalation stages Trevor wants to test.
- What action proves Trevor is genuinely out of bed and stops the wake-up sequence.
- Which morning briefing modules are enabled, their order, and the maximum briefing length.
- Morning delivery time and whether it changes by A day, B day, Friday, weekend, or summer schedule.
- Delivery destination: phone notification, Home Assistant dashboard, Ecosystem dashboard, message, or a combination.
- Exact Immich album/location names for motivation and guitar practice.
- Whether the guitar choice should follow a structured learning sequence or rotate among approved songs.
- Retention rules for downloaded social-media videos and their source metadata.
