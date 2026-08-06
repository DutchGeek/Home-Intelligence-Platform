# Visitor Intelligence Package

The Visitor Intelligence package provides homeowner-facing event retention, snapshot history, and daily statistics on top of the existing HIP Event Runtime.

## Responsibility
- Record visitor timeline entries
- Maintain event detail state for the dashboard
- Maintain snapshot history references
- Maintain daily homeowner-visible statistics

## Runtime Model
- Consumes the existing Event Contract through Kernel dispatch
- Does not publish new event types
- Does not modify the Kernel architecture

## Retention Model
- Timeline retention is helper-backed and stores the latest five completed events.
- Snapshot history retention stores the latest five retained per-event snapshot references.
- Daily statistics reset when the event date changes.

## Homeowner Questions Answered
- Who came?
- When?
- What happened?
- Was I notified?
- Did the HomePod announce?
- Was a snapshot captured?
