# HIP Core Package

The HIP Core package owns the event runtime.

## Components
- Global enable switch: input_boolean.hip_enabled
- Latest event persistence helpers:
	- input_text.hip_last_event
	- input_text.hip_last_event_id
	- input_text.hip_last_event_type
	- input_text.hip_last_event_source
	- input_text.hip_last_event_contract_version
	- input_text.hip_last_event_lifecycle
	- input_text.hip_last_event_artifact
	- input_text.hip_last_event_artifact_public
	- input_datetime.hip_last_event_at
- Artifact helpers:
	- input_text.hip_snapshot_artifact_path
	- input_text.hip_snapshot_public_path
	- input_text.hip_artifact_retention_policy
- Runtime scripts:
	- script.hip_event_manager
	- script.hip_event_persist
	- script.hip_artifact_manager
	- script.hip_retention_policy
	- script.hip_event_dispatch
	- script.hip_event_log
	- script.hip_log_event

## Responsibility
- Own the versioned event contract lifecycle
- Persist the latest event state
- Manage artifact path ownership and retention policy
- Dispatch subscribers without direct subscriber-to-subscriber communication
