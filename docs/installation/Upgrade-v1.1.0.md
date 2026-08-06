# Upgrade From HIP v1.1.0 To HIP v2.0.0

## Goal
Upgrade the existing production installation to the v2.0.0 event-driven package layout without changing working entity IDs.

## Migration Path
1. Back up the full Home Assistant configuration directory.
2. Back up the currently deployed HIP package files.
3. Copy the updated HIP repository contents into the deployment source.
4. Confirm that Home Assistant packages are enabled with:
	homeassistant:
	  packages: !include_dir_named ../packages
5. Create or verify the directory /config/www/snapshots.
6. Deploy the updated package files to Home Assistant without renaming entities.
7. Restart Home Assistant.
8. Validate that these automations load:
	- hip_front_door_event
	- hip_doorbell_event_logger
	- hip_doorbell_notification_handler
	- hip_doorbell_homepod_handler
	- hip_doorbell_snapshot_handler
9. Trigger the doorbell once and confirm notification, audio, snapshot, and event logging behavior.

## Rollback Instructions
1. If validation fails, stop the rollout immediately.
2. Restore the previous v1.1.0 HIP package files from backup.
3. Remove any newly copied v2.0.0 release files if they are part of the failure scope.
4. Restart Home Assistant.
5. Re-run the v1.1.0 doorbell validation path before declaring rollback complete.

## Notes
- v2.0.0 preserves existing helper and script entity IDs where practical.
- The rollout introduces event fan-out but keeps one event publication per trigger.
- Reliability takes precedence over enabling additional features during upgrade.
