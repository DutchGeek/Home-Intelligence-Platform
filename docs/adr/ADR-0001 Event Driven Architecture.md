# ADR-0001 Event Driven Architecture

Status: Accepted
Date: 2026-08-06

## Context
HIP coordinates multiple Home Assistant responsibilities from common triggers such as a doorbell ring. Directly embedding every action in one automation increases coupling and makes validation, rollback, and ownership harder.

## Decision
HIP uses an event-driven architecture where one trigger produces one normalized HIP event, and downstream packages subscribe based on responsibility.

## Consequences
- Packages remain narrowly scoped.
- Consumers can evolve independently without replacing the producer.
- Fan-out introduces ordering and race-condition considerations that must be reviewed per release.
- Migration and rollback must account for both publisher and subscribers.

## Alternatives Considered
- Single monolithic automation per use case
- Direct script chaining without event publication

## Rationale
A single published event from a single producer gives a stable handoff boundary while preserving modularity and minimizing duplicate logic.
