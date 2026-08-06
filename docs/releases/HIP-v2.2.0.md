# HIP v2.2.0

## Summary
HIP v2.2.0 is the first homeowner-facing production release of HIP. It adds operational visibility on top of the existing event runtime without introducing AI, breaking changes, or new event types.

## Delivered
- Event History
- HIP Inspector
- Snapshot Viewer
- Runtime Metrics
- Operational Dashboard

## Compatibility
- Uses the existing `hip.event.v1` contract
- Introduces no new event types
- Preserves existing doorbell runtime behavior
- Builds on the existing event runtime and does not replace it

## Migration Path
1. Deploy the updated dashboard, helper, and documentation files.
2. Ensure Home Assistant still loads the existing package tree.
3. Restart Home Assistant.
4. Verify the HIP dashboard loads and displays current runtime state.
5. Trigger the doorbell and confirm the history and metrics update.

## Rollback Instructions
1. Revert the dashboard and helper changes if the homeowner experience is degraded.
2. Restore the prior README, changelog, and version metadata if needed.
3. Keep the event runtime intact if rollback is limited to the first production dashboard.
4. Restart Home Assistant and confirm the prior release behavior returns.

## Validation Focus
- Event history updates when the existing event runtime completes an event
- HIP Inspector shows the current event contract state
- Snapshot Viewer displays the latest front-door snapshot
- Runtime Metrics reflect event totals and last event time
- Operational Dashboard loads without errors
