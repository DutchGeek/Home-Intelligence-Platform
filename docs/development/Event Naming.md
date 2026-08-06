# Event Naming

## Goals
- One event per trigger
- Clear domain ownership
- Stable consumer contracts

## Rules
- Use normalized HIP events as package boundaries.
- A producer should publish one event for one trigger transition.
- Event names should be specific to domain intent and stable over time.
- Event payloads should be documented and treated as a contract.
- Adding fields is preferred over replacing an event name when evolving behavior.

## Current Event
- hip_doorbell_pressed
  - source
  - message

## Recommendation
Future event families should adopt a documented naming convention before expansion, for example domain-first names with versioned payload contracts.
