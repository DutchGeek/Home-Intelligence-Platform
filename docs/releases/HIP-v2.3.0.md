# HIP v2.3.0

## Summary
HIP v2.3.0 delivers the first complete homeowner capability on top of the existing HIP Kernel and Event Runtime. It adds visitor-facing timeline, detail, retention, and daily statistics without changing the Event Contract or introducing AI.

## Delivered
- Visitor Timeline
- Snapshot History
- Event History UI
- Event Detail / Inspector
- Dashboard improvements
- Event retention
- Snapshot retention references
- Daily statistics

## Compatibility
- Uses the existing Event Runtime
- Uses the existing Event Contract
- Introduces no new event types
- Does not modify Kernel architecture
- Introduces no AI features

## Migration Path
1. Deploy the Visitor Intelligence package and updated dashboard.
2. Restart Home Assistant.
3. Verify the new helpers load.
4. Trigger an existing doorbell event.
5. Confirm the homeowner dashboard surfaces update.

## Rollback Instructions
1. Remove the Visitor Intelligence package and revert the dashboard changes.
2. Restart Home Assistant.
3. Confirm the previous Event Runtime behavior is still intact.

## Validation Focus
- Timeline updates after completed events
- Snapshot history references update after completed events
- Event detail answers who, when, what, notified, announced, and snapshot captured
- Daily counters increment and reset on day change
- Dashboard cards load without errors
