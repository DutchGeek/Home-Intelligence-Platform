# HIP v2.0.0

## Summary
HIP v2.0.0 establishes a production package-first, event-driven architecture for the doorbell domain while preserving existing working integrations.

## Delivered
- Security package publishes hip_doorbell_pressed
- HIP Core package logs normalized events
- Notification package subscribes and sends rich iPhone notifications
- Media package subscribes and announces on HomePod through Piper
- Camera package subscribes and captures snapshots to /config/www/snapshots/front_door_latest.jpg

## Compatibility
- Existing entity IDs are preserved where practical
- Existing script path script.hip_log_event remains available for compatibility

## Validation Focus
- Verify all five doorbell automations are loaded
- Trigger binary_sensor.doorbell_ringing and confirm:
  - notification delivery
  - Piper announcement
  - snapshot creation
  - logbook entry and input_text.hip_last_event update

## Next Roadmap
- Frigate event ingestion
- CompreFace identity enrichment
- Whisper transcription pipeline
- Ollama local reasoning flows
