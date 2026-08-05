# Camera Package

The Camera package handles front-door snapshot capture.

## Components
- input_text.hip_front_door_camera
- script.hip_capture_snapshot
- automation.hip_doorbell_snapshot_handler

## Responsibility
- Subscribe to hip_doorbell_pressed events
- Capture snapshot to /config/www/snapshots/front_door_latest.jpg
