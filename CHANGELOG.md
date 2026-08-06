# Changelog

## 2.4.0
- Added the native Home Assistant HIP management integration under `custom_components/hip`
- Added installation, upgrade, rollback, health-check, and smoke-test validation surfaces
- Added diagnostics, support bundle export, update visibility, and module discovery
- Preserved the existing Kernel, Event Runtime, Event Contract, automations, and entities

## 2.3.0
- Added Visitor Intelligence as the first complete homeowner capability
- Added visitor timeline, snapshot history, event detail, and daily statistics
- Added retained per-event snapshot history references without changing the Event Contract
- Preserved Kernel architecture and existing event runtime behavior

## 2.2.0
- Added homeowner-facing operational dashboard surfaces
- Added event history and runtime metrics built on the existing event contract
- Added snapshot viewer and HIP Inspector views
- Preserved production runtime behavior and avoided AI features

## 2.1.0
- Added ADR-0005 for the versioned event contract
- Added HIP Core event manager, persistence model, artifact manager, and retention policy
- Routed doorbell runtime flow through a single event lifecycle manager
- Removed direct package event subscriber automations while preserving existing doorbell behavior

## 2.0.1
- Added GitHub governance templates, CODEOWNERS, and repository validation workflow
- Added architecture decision records for eventing, package structure, notifications, and HomePod TTS
- Added development standards, release checklists, and contributor support policies
- No Home Assistant implementation changes in this milestone

## 2.0.0
- Refactored the front-door doorbell flow to event-driven package orchestration
- Added package handlers for notifications, media, snapshots, and logging
- Implemented production snapshot capture in the camera package
- Preserved existing entity IDs and working integrations

## 1.0.0-alpha
- Initial project structure
- HIP Core scaffolding
