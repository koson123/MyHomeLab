# Homelab Jarvis and Proactive AI Plan

## Status and purpose

Status: Planned architecture; detailed planning started August 16, 2026.

Jarvis will begin as Trevor's independent, always-available homelab assistant. It should help with daily life, trusted knowledge, media, Home Assistant, personal content, and server operation before Ecosystem OS is ready.

Jarvis is not simply a chatbot and the LLM is not the control plane. Jarvis is a collection of deterministic services, typed capabilities, policies, context, and interfaces. A replaceable local LLM helps interpret natural language, summarize information, rank choices, and create plans. Approved service adapters perform actions.

When Ecosystem OS is mature, the proven Jarvis capabilities and user experience should migrate into Ecosystem's intelligence layer. The standalone homelab version stays operational until the Ecosystem version reaches verified feature parity.

## Primary goals

- Work locally for important commands and routines when the external internet is unavailable.
- Accept voice, text, dashboard, phone, automation, and physical-device input.
- Be proactive when a useful event or scheduled moment occurs, without becoming noisy or controlling.
- Understand Trevor's approved schedule, workouts, projects, routines, media, devices, and homelab state.
- Explain what it knows, why it made a suggestion, what source it used, and what action it wants to take.
- Use official Church content as a trusted authoritative source for gospel-related retrieval and selections.
- Keep every capability modular so it can later move into Ecosystem OS.

## Non-goals for the first version

- Unrestricted root, shell, Proxmox, Docker socket, Home Assistant, camera, account, or file access for an LLM.
- Silent destructive actions or broad autonomous infrastructure changes.
- Treating guesses, generated text, or internet content as verified facts.
- Recording every conversation, sound, screen, location, or activity forever.
- Replacing reliable alarms, safety systems, or essential manual controls.

## High-level architecture

### 1. Jarvis gateway

The single authenticated entry point for approved clients.

Responsibilities:

- Receive text, voice transcripts, dashboard actions, webhooks, schedules, and Home Assistant events.
- Identify the requesting user, device, location, and available permissions.
- Rate-limit requests and reject unauthenticated network access.
- Return structured responses that clients can display or speak.
- Expose a local API that remains stable even if the LLM or interface changes.

### 2. Intent and planning layer

Converts a request or event into a structured plan.

- Deterministic intent matching handles known commands first.
- The local LLM handles natural phrasing, ambiguity, summaries, recommendations, and multi-step planning.
- Plans contain typed actions with explicit parameters, not free-form shell commands.
- Jarvis shows assumptions or asks for missing information when an action cannot be safely inferred.
- The system can fall back to deterministic commands if the LLM is offline.

### 3. Capability registry

Each integration exposes a limited set of named actions and read operations.

Initial capability groups:

- Home Assistant: read state, run approved scenes/scripts, control allowed lights/media/devices.
- Morning Hub: select workout, briefing, scripture/talk, motivation video, and guitar song; record acknowledgement and completion.
- Immich: search Trevor's library, retrieve curated collections, add approved items to selected albums.
- Music: search Navidrome, play/pause/queue, create or update playlists, capture feedback.
- Media: search and control Jellyfin, Audiobookshelf, Navidrome, and supported playback targets.
- Gospel Library: search trusted local content, retrieve passages/talks, generate source-grounded study selections, and play stored audio.
- Calendar/tasks/reminders: read relevant schedule state and create approved reminders when integrations are available.
- Homelab: read monitoring, storage, backup, container, and VM status; propose bounded recovery actions.
- PC agent: wake, sleep, and launch only predefined approved desktop actions.
- Notifications: send to approved phones, dashboards, speakers, and panels.

Every capability defines its inputs, output, timeout, permissions, confirmation rule, audit data, and failure behavior.

### 4. Policy and approval engine

Jarvis assigns each action to a risk level.

- Level 0 — answer only: search, explain, summarize, and recommend.
- Level 1 — reversible personal action: play media, adjust an allowed light, create a draft, or update a personal playlist.
- Level 2 — consequential but bounded action: change a routine, control broader home scenes, move files, restart one known service, or alter an automation. Requires confirmation unless Trevor explicitly pre-approves that exact rule.
- Level 3 — privileged/high impact: deploy services, modify networking, change permissions, create/delete VMs, update infrastructure, expose services, or affect security/data. Always requires a clear preview and explicit approval.
- Prohibited: actions outside registered capabilities, bypassing authentication, requesting secrets, disabling safeguards, or destructive behavior without a recoverable and explicitly approved workflow.

Approvals should name the exact target, action, expected effect, and recovery path.

### 5. Proactive event engine

Proactivity should be event-driven and policy-controlled rather than the LLM continuously deciding what to do.

Trigger sources:

- Schedules and deadlines.
- Home Assistant presence, device, and sensor events.
- Workout and routine state.
- New Immich/media content.
- Uptime Kuma, backup, storage, certificate, and service-health events.
- Explicit watchlists or approved periodic checks.
- Listening, completion, favorites, skips, and feedback events.

Every proactive rule specifies:

- Why it exists.
- When it is allowed to trigger.
- Required context and confidence.
- Quiet hours and cooldown.
- Notification priority and destination.
- Whether Jarvis may act, ask, suggest, or only record.
- Deduplication and escalation rules.
- How Trevor disables or snoozes it.

The first proactive features should be the Personal Morning Delivery Hub, genuinely important server alerts, and requested reminders. Broader suggestions come later after the signal-to-noise ratio is proven.

### 6. Context and memory

Use different memory classes instead of one unlimited assistant memory.

- Current-session context: temporary conversation and active task state.
- Operational state: device states, active playback, current workout, service health, and pending approvals.
- Explicit preferences: facts Trevor asks Jarvis to remember, such as briefing modules or music feedback.
- History: bounded workout completion, delivered content, acknowledged alerts, and automation runs.
- Knowledge indexes: trusted documents and media metadata with source and update time.
- Sensitive data: credentials and secrets remain outside model prompts and are retrieved only by the service that needs them.

Trevor must be able to inspect, correct, export, or delete stored preferences and history. Temporary access to a screen, camera, file, or conversation does not automatically become long-term memory.

### 7. Audit and observability

For every tool use or proactive event, record:

- Time, requester/trigger, capability, parameters with secrets removed, approval state, result, duration, and error.
- Which deterministic rule, source document, or model contributed to the decision.
- Notification delivery and acknowledgement.
- Recovery or rollback result when applicable.

Provide a dashboard for pending approvals, recent actions, failed automations, memory/preferences, and proactive-rule controls.

## Trusted local Gospel Content Library

### Trust and source policy

Official content published by The Church of Jesus Christ of Latter-day Saints is an approved trusted source for Trevor's Jarvis. The local library should preserve the official title, author/speaker, publication, date, language, source URL, and retrieval/update time.

Jarvis may summarize or recommend official content, but gospel answers should cite the specific scripture, talk, manual, or other source used. Generated commentary must be distinguishable from the source itself.

### Initial collection

- Standard works and study helps.
- General Conference talks in text, starting with a manageable approved year range and expanding later.
- Selected conference audio/video where the official source provides a download.
- Come, Follow Me manuals.
- Preach My Gospel.
- Teachings of Church Presidents and other approved manuals/books Trevor chooses.
- Hymns and approved Church media that are useful for study or morning delivery.

### Storage and indexing

- Store normalized text and metadata in a local content store.
- Keep original official URLs and content hashes.
- Store audio/video separately from the text index.
- Use full-text search first; add semantic/vector search only as a secondary retrieval method.
- Preserve paragraphs, scripture references, speakers, topics, dates, and publication hierarchy.
- Back up the index metadata and configuration; large reproducible media may use a separate retention policy.
- Detect updates without silently replacing a source used in saved notes or study history.

### Update process

- Use official Church pages and officially offered downloads.
- Begin with a curated importer rather than attempting an uncontrolled full-site mirror.
- Periodically check approved collections for new or changed content.
- Produce an update preview listing additions, changes, removals, and storage impact.
- Automatically ingest low-risk new official text only after the update policy is approved; ask before large audio/video downloads.
- Retain source attribution and avoid redistributing the private archive publicly.

### Jarvis and automation uses

- Select a morning scripture, conference quote, or short spiritual prompt.
- Build topic-based study queues from scriptures, talks, and manuals.
- Find talks by speaker, conference, date, subject, or referenced scripture.
- Play downloaded talk or scripture audio locally.
- Recommend related official sources while showing why they are related.
- Track what Trevor has read/listened to and reduce unwanted repetition.
- Ground gospel-related Jarvis answers in retrieved official sources.
- Work during an internet outage using the locally stored collection.

## Interfaces

Planned clients:

- Responsive local web dashboard.
- Home Assistant dashboard cards and actionable notifications.
- Phone notifications and shortcuts.
- Voice satellites/speakers after the wake-word, speech-to-text, and text-to-speech stack is chosen.
- Old iPads using stock iPadOS, Safari/Home Screen, and Guided Access as Jarvis/Home Assistant panels.
- Windows PC agent for approved local commands and background playback.
- Later, Ecosystem OS native interfaces.

All interfaces use the same gateway, capabilities, approvals, history, and proactive rules.

## Deployment direction

- Run Jarvis core services in the planned 100 GB `mini-llm` Ubuntu Server VM.
- Do not assume all components require the LLM; split gateway, event engine, capability adapters, database, search, and model runtime into replaceable services.
- Keep Home Assistant on HAOS and connect through scoped API credentials.
- Keep large media on NAS storage instead of the VM disk.
- Avoid exposing Jarvis administrative interfaces publicly; use the local network or VPN.
- Back up configuration, preferences, histories, indexes that are not easily reproducible, and the capability/policy definitions.
- Plan RAM carefully before creating the VM because the mini-PC had limited free memory during the last audit.

## Suggested internal components

Names are architectural roles, not final software selections:

- `jarvis-gateway`
- `jarvis-orchestrator`
- `jarvis-events`
- `jarvis-policy`
- `jarvis-memory`
- `jarvis-notify`
- `jarvis-homeassistant`
- `jarvis-immich`
- `jarvis-media`
- `jarvis-music`
- `jarvis-gospel`
- `jarvis-homelab`
- `jarvis-pc-agent`
- local model runtime
- speech-to-text, wake-word, and text-to-speech services later

## Implementation phases

### J0 — decisions and contracts

- Define the initial three user-facing use cases.
- Define capability/action schemas and approval levels.
- Choose the local database and service communication pattern.
- Define memory retention and audit policy.
- Choose the first dashboard and notification client.
- Measure available mini-PC RAM/CPU before selecting a model.

### J1 — deterministic Jarvis core

- Deploy authenticated gateway, orchestrator, policy engine, audit log, and dashboard.
- Implement deterministic commands without an LLM.
- Connect Home Assistant read-only state, notifications, and one harmless approved action.
- Add health checks, backups, and a kill switch.

### J2 — Personal Morning Delivery Hub

- Import the structured workout plan.
- Deliver and acknowledge the correct workout.
- Add curated Immich motivation and guitar selections.
- Add approved briefing modules and wake-up stages.
- Keep an independent backup alarm.

### J3 — trusted knowledge and Gospel Library

- Import an approved initial official Church collection.
- Add full-text search, citations, study history, and morning selections.
- Add optional local audio playback.
- Verify offline operation and update previews.

### J4 — local LLM assistance

- Select a model/runtime based on measured hardware.
- Add natural-language interpretation, retrieval-grounded answers, summarization, and plan generation.
- Keep typed execution and policy outside the model.
- Evaluate latency, hallucinations, source faithfulness, and fallback behavior.

### J5 — proactive AI

- Add event rules, quiet hours, cooldowns, deduplication, and acknowledgement.
- Start with morning delivery and important health/backup alerts.
- Add suggestions only after observing low false-positive and annoyance rates.
- Provide per-rule pause, snooze, and disable controls.

### J6 — music, media, and personal context

- Add Navidrome/Spotify-like discovery and playlist workflows.
- Add Jellyfin, Audiobookshelf, Immich, and playback-target control.
- Add explicit feedback and bounded preference/history learning.

### J7 — homelab assistance

- Add read-only infrastructure status and explanations.
- Add approval-gated bounded recovery actions.
- Later connect approved Ansible and Proxmox workflows with previews and audit logs.

### J8 — voice and distributed panels

- Select wake-word, speech-to-text, and text-to-speech components after hardware tests.
- Add room/device-aware voice routing.
- Deploy old-iPad panels and approved speaker endpoints.
- Make mute/privacy state obvious and locally controllable.

### J9 — Ecosystem migration readiness

- Freeze stable capability, context, event, and client contracts.
- Export preferences, history, indexes, and policies cleanly.
- Map homelab Jarvis capabilities into Ecosystem's permission model.
- Keep standalone Jarvis until Ecosystem reaches verified feature parity.

## Decisions still needed

- The first three Jarvis use cases to implement after the core.
- Local model runtime and model size after measuring available resources.
- Wake word, speech-to-text, and text-to-speech stack.
- Primary dashboard and notification destinations.
- Exact proactive quiet hours, priorities, escalation, and cooldown behavior.
- Memory retention periods and what Jarvis may learn automatically versus only after explicit approval.
- Initial Gospel Library publications, conference year range, languages, and audio/video scope.
- Whether updates to trusted Church text may ingest automatically after preview or always require approval.
- Which Home Assistant actions are safe enough for Level 1.
- How Jarvis authenticates Trevor across phone, PC, panels, and voice endpoints.
