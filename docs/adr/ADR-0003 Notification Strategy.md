# ADR-0003 Notification Strategy

Status: Accepted
Date: 2026-08-06

## Context
Doorbell events require reliable user notification. Mobile notifications are a production-critical path and should not be coupled to unrelated media or logging actions.

## Decision
HIP uses a dedicated notification package that subscribes to HIP events and sends mobile notifications through the configured Home Assistant notify service.

## Consequences
- Notification logic stays isolated from event production and audio output.
- Mobile delivery can be validated independently.
- Notification payload changes must preserve current working paths or provide a migration path.
- Notification timing should be reviewed when snapshot capture is part of the payload.

## Alternatives Considered
- Inline notification calls in the producer automation
- A single shared script that also handles logging and audio

## Rationale
Isolation keeps failures localized and reduces the risk of rewriting a working notification path when unrelated package behavior changes.
