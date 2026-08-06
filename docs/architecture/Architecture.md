# HIP Architecture

Home Assistant packages are the primary modular boundary in HIP v2.1.0.

## Event-Driven Flow

binary_sensor.doorbell_ringing
-> Security trigger (automation.hip_front_door_event)
-> HIP Event Manager (script.hip_event_manager)
-> HIP event contract `hip.event.v1`
-> persistence and lifecycle updates
-> artifact manager and snapshot manager
-> subscriber dispatch scripts:
- Notification subscriber
- Media subscriber
- Logging subscriber

## Package Responsibilities
- HIP Core: Kernel runtime, event manager, persistence, lifecycle, artifact management, and logging
- Security: trigger detection and event manager entrypoint
- Notifications: mobile notification subscriber implementation
- Media: Piper HomePod announcement subscriber implementation
- Cameras: snapshot subscriber implementation used by the event manager
- Visitor Intelligence: homeowner-facing retention, event detail, timeline, and daily statistics

## Event Runtime
- One event: `hip_doorbell_pressed`
- One contract: `hip.event.v1`
- One lifecycle owner: `script.hip_event_manager`
- One persistence model: helper-backed latest-event state in HIP Core
- One artifact manager: `script.hip_artifact_manager`
- Subscribers do not communicate directly

## Device Registry
- The Kernel is the only component allowed to resolve devices.
- The Device Registry is private to the Kernel.
- Packages consume logical devices only and must never treat entity IDs as public inputs.
- The Event Contract exposes logical devices only.

## Kernel Boundary
- Packages communicate only through the Event Runtime.
- Packages must never access entity IDs directly as part of their public behavior model.
- Logical devices are the only supported package-facing abstraction.

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
