# ADR-0004 HomePod TTS Strategy

Status: Accepted
Date: 2026-08-06

## Context
HIP requires in-home announcements using an implementation already proven in production. Reliability is preferred over feature experimentation.

## Decision
HIP uses the existing Piper-backed Home Assistant TTS path for HomePod announcements, isolated in the media package.

## Consequences
- Media behavior remains independent from notification and logging concerns.
- Existing TTS entity and media player references should be preserved when practical.
- Any future voice enhancements must extend the existing pipeline rather than replace it without a production migration path.

## Alternatives Considered
- Replacing Piper with a new speech provider
- Embedding TTS calls in the producer or notification package

## Rationale
The current Piper path is already proven. Preserving it minimizes operational risk while keeping a clean architectural boundary.
