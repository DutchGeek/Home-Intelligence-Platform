# HIP v2.1.0

## Summary
HIP v2.1.0 introduces the production event runtime for the existing doorbell pipeline. This milestone does not add AI features or new user-facing capabilities. It centralizes runtime orchestration, persistence, and artifact ownership while preserving the current doorbell behavior.

## Delivered
- ADR-0005 Event Contract
- Versioned event contract `hip.event.v1`
- Central event manager: `script.hip_event_manager`
- Event persistence model in HIP Core helpers
- Central dispatch lifecycle for subscribers
- Snapshot manager flow through the event manager
- Artifact manager and retention policy ownership in HIP Core

## Compatibility
- Existing doorbell trigger remains `binary_sensor.doorbell_ringing`
- Existing package subscriber scripts remain in place
- Existing logging compatibility script `script.hip_log_event` remains available
- Existing snapshot public path remains `/local/snapshots/front_door_latest.jpg`

## Migration Path
1. Back up the current Home Assistant configuration.
2. Deploy the updated HIP Core, Security, Notification, Media, and Camera package files.
3. Restart Home Assistant.
4. Verify `script.hip_event_manager`, `script.hip_event_persist`, `script.hip_event_dispatch`, `script.hip_artifact_manager`, and `script.hip_retention_policy` are loaded.
5. Trigger the doorbell once and confirm notification, HomePod announcement, snapshot creation, and latest-event helper updates.
6. Confirm `input_text.hip_last_event_contract_version` reports `hip.event.v1`.

## Rollback Instructions
1. Stop rollout on first validation failure.
2. Restore the previous package files from the last known good release.
3. Restart Home Assistant.
4. Re-run the v2.0.x doorbell validation path.
5. Return the system to service only after notification, HomePod, snapshot, and logging behavior are confirmed.

## Validation Focus
- One trigger enters one manager.
- Subscribers do not communicate directly.
- Lifecycle state is persisted from accepted through completed.
- Artifact path ownership remains stable.
- Existing doorbell behavior is unchanged from the operator perspective.