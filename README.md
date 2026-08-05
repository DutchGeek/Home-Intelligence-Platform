# Home Intelligence Platform (HIP)

Version: 2.0.0

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

## v2.0.0 Milestone
- Refactored doorbell flow to event-driven architecture
- Replaced snapshot placeholder with production snapshot capture
- Preserved existing iPhone notification and Piper HomePod announcement behavior
- Added package-level event handlers for modular operation
