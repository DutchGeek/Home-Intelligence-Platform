# Home Intelligence Platform (HIP)

Version: 2.1.0

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
