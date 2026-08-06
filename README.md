# Home Intelligence Platform (HIP)

Version: 2.5.5

A modular, event-driven Home Assistant platform.

## Production Status
- HIP Core package active
- Security package active
- Notification package active
- Media package active
- Camera package active

## Architecture
- Package-first Home Assistant implementation
- Event-driven pipeline centered on custom HIP events
- Existing entity IDs preserved from prior releases
- Device Registry is the canonical source of truth for entity and service identifiers
- Operational packages resolve targets through registry values instead of hardcoded device IDs

## Production Principles
- Reliability over feature growth
- Extend working implementations instead of replacing them
- Minimize change scope per release
- One responsibility per package
- One event per trigger
- Avoid race conditions and duplicate automations
- Preserve and reuse existing entity IDs wherever practical
- Every change must ship with migration and rollback guidance

## v2.0.0 Milestone
- Refactored doorbell flow to event-driven architecture
- Replaced snapshot placeholder with production snapshot capture
- Preserved existing iPhone notification and Piper HomePod announcement behavior
- Added package-level event handlers for modular operation

## v2.0.1 Engineering Foundation
- GitHub issue and pull request governance added
- Repository validation workflow added for YAML, Markdown links, and structure
- Architecture decision records added under docs/adr
- Development standards, release checklists, and contributor policies added

## v2.1.0 Event Runtime
- Added a centralized event manager in HIP Core
- Added versioned event contract hip.event.v1
- Added helper-backed event persistence and lifecycle state
- Added artifact manager, snapshot manager flow, and retention policy ownership
- Preserved the existing doorbell behavior without direct subscriber communication

## v2.2.0 First Production Release
- Added event history, HIP Inspector, snapshot viewer, runtime metrics, and an operational dashboard
- Built on the existing event runtime and event contract
- No AI features added
- No breaking changes introduced

## v2.3.0 Visitor Intelligence
- Added a homeowner-facing visitor timeline and snapshot history
- Added event detail answers for who, when, what, notified, announced, and snapshot captured
- Added daily visitor, notification, announcement, and snapshot statistics
- Built entirely on the existing Kernel and Event Runtime

## v2.4.0 Installation & Home Assistant Integration
- Added a native `custom_components/hip` management integration
- Added installation, configuration, runtime health, and smoke-test validation services
- Added diagnostics and support bundle export
- Added integration UI surfaces for version, modules, runtime status, and management actions

## v2.5.1 Deployment Simplification
- HIP integration is deployment-dashboard only (no internal file installation or rollback)
- Repository scripts manage deploy/rollback/validation from outside Home Assistant
- Added script entrypoints under `tools/`:
	- `deploy-dev.sh`
	- `deploy-prod.sh`
	- `rollback-dev.sh`
	- `rollback-prod.sh`
	- `validate.sh`

## v2.5.5 External Configuration Architecture
- Repository is stateless for deployment secrets and machine-specific settings
- Repository keeps only templates:
	- `config/dev.env.example`
	- `config/prod.env.example`
- Real deployment configuration is loaded from:
	- `/mnt/apps/configs/hip/dev.env`
	- `/mnt/apps/configs/hip/prod.env`
- Deployment scripts support legacy migration from repository config files on first run
- Added git safety checks and optional `git pull --ff-only` support
- Added interactive deployment confirmation (configurable)
- Added colored output, progress indicators, and duration reporting
- Added validation and smoke-test summary output

### One-command deployment
- Development: `./deploy-dev.sh`
- Production: `./deploy-prod.sh`
