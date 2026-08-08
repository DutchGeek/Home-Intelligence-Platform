# Visitor Intelligence Package

Visitor Intelligence is the first complete end-to-end HIP product feature. It is event-first: every doorbell interaction becomes a persistent Visitor Event and all downstream behavior reads from that event.

## Responsibility
- Create and persist Visitor Events through `hip.visitor_*` services
- Keep per-event timeline evidence (`Doorbell pressed`, `Snapshot captured`, `Notification sent`, `HomePod announced`)
- Sync visitor dashboard cards from persisted storage
- Provide dashboard action scripts (`Mark Known`, `Ignore`, `Delete`, `Open Timeline`)
- Maintain homeowner-facing counters and event detail helpers

## Event Model
Each event includes:
- `event_id`
- `type`
- `status`
- `camera`
- `timestamp`
- `person`
- `snapshot`
- `confidence`
- `notification_sent`
- `announcement_sent`
- `timeline`

## Storage
- Persistent file: `/config/.storage/hip_visitor_events.json`
- Survives Home Assistant restarts
- Supports create, update, retrieve, list, and delete through HIP services

## Dashboard
- Dashboard file: `homeassistant/dashboards/Visitor-Dashboard.yaml`
- Renders latest visitor cards from service-backed helper state
- Updates immediately when `script.hip_record_visitor_event` syncs storage to helpers
