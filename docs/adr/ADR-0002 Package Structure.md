# ADR-0002 Package Structure

Status: Accepted
Date: 2026-08-06

## Context
HIP is built on Home Assistant Packages. Production reliability depends on clear module boundaries, stable entity IDs, and limited blast radius for changes.

## Decision
HIP organizes automation behavior by package responsibility:
- hip_core for shared controls and logging
- security for trigger detection and publishing
- notifications for mobile alerts
- media for HomePod and audio actions
- cameras for snapshot capture
- ai and dashboard reserved for future bounded responsibilities

## Consequences
- Each package owns one primary responsibility.
- Shared helpers must stay in the narrowest stable package that justifies them.
- Cross-package dependencies must be explicit in documentation.
- Duplicate automations reacting to the same trigger for the same responsibility are not allowed.

## Alternatives Considered
- Flat repository-wide YAML without package boundaries
- Broad domain packages containing multiple unrelated responsibilities

## Rationale
Package boundaries are the primary maintainability tool in HIP. They reduce accidental coupling and make rollback and testing more predictable.
