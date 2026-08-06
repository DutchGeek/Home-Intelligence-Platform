# HIP Architecture

Home Assistant packages are the primary modular boundary in HIP v2.0.0.

## Event-Driven Flow

binary_sensor.doorbell_ringing
-> Security publisher (automation.hip_front_door_event)
-> custom event hip_doorbell_pressed
-> package subscribers:
- HIP Core logger
- Notification handler
- Media handler
- Camera snapshot handler

## Package Responsibilities
- HIP Core: global enable state and event logging
- Security: event detection and publishing
- Notifications: iPhone notifications
- Media: Piper HomePod announcements
- Cameras: snapshot capture

## Change Guardrails
- Prefer extending existing package behavior over replacing working flows.
- Keep one primary responsibility per package.
- Emit one normalized HIP event per trigger.
- Avoid multiple automations that react to the same trigger unless each automation owns a distinct responsibility.
- Preserve existing entity IDs to reduce operational migration risk.
- Treat race-condition analysis as a release requirement for any fan-out event flow.

## Compatibility
- Existing entity IDs are preserved where practical
- Legacy script call path script.hip_log_event remains available

