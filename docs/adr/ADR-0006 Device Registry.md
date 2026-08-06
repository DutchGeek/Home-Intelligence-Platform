# ADR-0006 Kernel Responsibilities

Status: Accepted
Date: 2026-08-06

## Context
HIP needs a strict separation between operational package logic and platform-specific device resolution. Direct use of entity identifiers couples packages to implementation details, weakens portability, and bypasses the event-runtime boundary.

## Decision
HIP defines a Kernel as the only component allowed to resolve devices.

The Kernel owns:
- the Event Runtime
- the private Device Registry
- the mapping from logical devices to concrete entity and service identifiers

All non-kernel packages must:
- consume logical devices only
- avoid direct access to entity IDs
- communicate only through the Event Runtime

The Event Contract must expose logical devices only. Concrete entity and service identifiers remain private implementation details behind the Kernel boundary.

## Consequences
- The Kernel is the sole device-resolution boundary.
- Packages depend on logical devices and event payloads, not direct entity identifiers.
- The Device Registry is private to the Kernel and must not be treated as a public package API.
- Registry changes remain deployment-impacting and must include migration and rollback guidance.
- Event design must remain stable because packages can only coordinate through the Event Runtime.

## Alternatives Considered
- Hardcoding entity IDs in each package
- Using ad hoc helper entities inside each package
- Allowing packages to query registry values directly as a public interface

## Rationale
Kernel-only device resolution enforces a clean architectural boundary. It keeps packages focused on domain behavior, prevents identifier sprawl, and makes future device replacement, validation, and rollback materially easier.
