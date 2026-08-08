# Visitor Dashboard Expected Screens

## 1) visitor-dashboard-initial.png
- View loads without errors.
- Visitor cards show `Unknown` placeholders.
- Daily counters are visible.

## 2) visitor-dashboard-event-created.png
- Card 1 shows a snapshot image.
- Card 1 fields include camera, timestamp, status `completed`, confidence `n/a`.
- Action buttons are visible for Card 1.

## 3) visitor-dashboard-event-known.png
- After `Mark Known`, Card 1 status updates to `known`.
- Name changes from `Unknown` to configured known label.
- Timeline includes `Marked known` entry.

## 4) visitor-dashboard-timeline-modal.png
- `Open Timeline` renders a notification containing ordered entries:
  - Doorbell pressed
  - Snapshot captured
  - Notification sent
  - HomePod announced
