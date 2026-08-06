# Smoke Test Checklist

## Core Checks
- [ ] Home Assistant starts successfully
- [ ] Packages load from `homeassistant/packages`
- [ ] `input_boolean.hip_enabled` exists
- [ ] `script.hip_event_manager` exists
- [ ] `script.hip_event_persist` exists
- [ ] `script.hip_artifact_manager` exists
- [ ] `script.hip_retention_policy` exists

## Doorbell Flow Checks
- [ ] `binary_sensor.doorbell_ringing` triggers the event manager
- [ ] Notification is delivered
- [ ] HomePod announcement runs
- [ ] Snapshot file is created
- [ ] `input_text.hip_last_event` updates
- [ ] `input_text.hip_last_event_contract_version` is `hip.event.v1`

## Pass Criteria
All checks should pass before the deployment is considered ready for promotion.
