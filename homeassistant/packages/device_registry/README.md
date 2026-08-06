# Device Registry

The Device Registry is the canonical source of truth for entity and device identifiers used by HIP.

## Responsibility
- Store canonical entity IDs and service targets
- Keep implementation files free of hardcoded device identifiers
- Provide the lookup values used by runtime packages, dashboards, and test harnesses
- Own the authoritative mapping for device resolution across the repository

## Canonical Entries
- hip_registry_doorbell_sensor_entity
- hip_registry_hip_enabled_entity
- hip_registry_last_event_entity
- hip_registry_last_event_id_entity
- hip_registry_last_event_type_entity
- hip_registry_last_event_source_entity
- hip_registry_last_event_contract_version_entity
- hip_registry_last_event_lifecycle_entity
- hip_registry_last_event_artifact_entity
- hip_registry_last_event_artifact_public_entity
- hip_registry_last_event_at_entity
- hip_registry_event_history_entity
- hip_registry_event_total_entity
- hip_registry_snapshot_artifact_path_entity
- hip_registry_snapshot_public_path_entity
- hip_registry_artifact_retention_policy_entity
- hip_registry_mobile_notify_service
- hip_registry_piper_tts_entity
- hip_registry_homepod_player_entity
- hip_registry_front_door_camera_entity
- hip_registry_test_enabled_entity
- hip_registry_test_scenario_entity
- hip_registry_test_last_event_id_entity
- hip_registry_test_last_event_type_entity
- hip_registry_test_last_event_source_entity
- hip_registry_test_last_event_message_entity
- hip_registry_test_last_result_entity
- hip_registry_test_last_run_at_entity
