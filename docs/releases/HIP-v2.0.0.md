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

## Migration Path
1. Back up the active Home Assistant configuration before copying HIP v2.0.0 files.
2. Ensure packages are still enabled through homeassistant: packages: !include_dir_named ../packages.
3. Create or verify the directory /config/www/snapshots.
4. Deploy the updated package files without renaming existing entities.
5. Restart Home Assistant and verify the five doorbell automations load.
6. Trigger binary_sensor.doorbell_ringing once and confirm logbook, notification, audio, and snapshot behavior.

## Rollback Instructions
1. Stop after validation failure and do not continue layering additional changes.
2. Restore the previous package files from the v1.1.0 backup or repository checkout.
3. Remove the v2.0.0 snapshot package changes if snapshot handling caused the regression.
4. Restart Home Assistant.
5. Re-run the previous v1.1.0 validation flow before returning the system to service.

## Reliability Notes
- The event publisher remains singular: one trigger, one event.
- Doorbell responsibilities are split by package to avoid duplicated logic inside a single automation.
- Existing entity IDs and script call paths are preserved to reduce migration risk.

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

