# ADR-0005 Event Contract

Status: Accepted
Date: 2026-08-06

## Context
HIP needs a stable runtime contract so event producers, persistence, artifact handling, and subscribers can evolve without direct coupling. The production requirement is one event, one contract, one lifecycle, one persistence model, and one artifact manager.

## Decision
HIP uses a single versioned event contract for the doorbell runtime: `hip.event.v1`.

Required fields:
- event_id
- contract_version
- event_type
- source
- message
- occurred_at
- lifecycle
- artifact_path
- artifact_public_path

The Event Manager is the only orchestrator allowed to manage lifecycle progression and subscriber dispatch. Subscribers do not communicate with each other directly.

## Consequences
- Existing user-facing scripts can remain stable while receiving the shared contract.
- Lifecycle and persistence are centralized in HIP Core.
- Artifact path ownership is centralized and documented.
- Contract evolution must be versioned and backwards compatible.

## Alternatives Considered
- Unversioned ad hoc event payloads
- Direct subscriber-to-subscriber communication
- Separate contracts per package

## Rationale
A single contract and manager reduce coupling, simplify rollback, and make runtime behavior testable and auditable.