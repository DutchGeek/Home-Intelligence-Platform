# Visitor Intelligence MVP Checklist

## Preconditions
- [ ] HIP clean deployment completed with compiled packages in `/config/packages`
- [ ] HIP integration loaded and healthy (`sensor.hip_runtime_status == healthy`)
- [ ] Eufy doorbell sensor mapped to `input_text.hip_registry_doorbell_sensor_entity`
- [ ] Camera mapped to `input_text.hip_registry_front_door_camera_entity`

## Expected Services
- [ ] `hip.visitor_create`
- [ ] `hip.visitor_update`
- [ ] `hip.visitor_delete`
- [ ] `hip.visitor_get`
- [ ] `hip.visitor_list`

## Expected Entities
- [ ] `input_text.hip_visitor_card_1_event_id`
- [ ] `input_text.hip_visitor_card_1_snapshot`
- [ ] `input_text.hip_visitor_card_1_status`
- [ ] `input_text.hip_visitor_active_event_id`
- [ ] `input_text.hip_visitor_active_timeline`
- [ ] `input_number.hip_daily_visitor_count`
- [ ] `input_number.hip_daily_notification_count`
- [ ] `input_number.hip_daily_homepod_count`
- [ ] `input_number.hip_daily_snapshot_count`

## End-to-End Flow (Live Test)
- [ ] Press the Eufy doorbell once
- [ ] Event created (`hip.visitor_list` returns new event with `type=visitor`, `status=completed`)
- [ ] Snapshot attached (`snapshot` contains `/local/snapshots/history/<event_id>.jpg`)
- [ ] Dashboard card updates (`homeassistant/dashboards/Visitor-Dashboard.yaml` view)
- [ ] HomePod announcement plays
- [ ] Push notification arrives with snapshot image
- [ ] Event appears in `input_text.hip_event_history`
- [ ] Event timeline includes:
	- [ ] Doorbell pressed
	- [ ] Snapshot captured
	- [ ] Notification sent
	- [ ] HomePod announced

## Dashboard Actions
- [ ] Open Camera shows configured camera entity
- [ ] Open Snapshot shows snapshot URL
- [ ] Open Timeline shows timeline entries
- [ ] Mark Known updates event status to `known`
- [ ] Ignore updates event status to `ignored`
- [ ] Delete removes event from list and dashboard

## Expected Storage Contents
- [ ] File exists: `/config/.storage/hip_visitor_events.json`
- [ ] JSON root contains `version` and `events`
- [ ] Each event includes:
	- [ ] `event_id`
	- [ ] `type`
	- [ ] `status`
	- [ ] `camera`
	- [ ] `timestamp`
	- [ ] `person`
	- [ ] `snapshot`
	- [ ] `confidence`
	- [ ] `notification_sent`
	- [ ] `announcement_sent`
	- [ ] `timeline`

## Expected Dashboard Screenshots
- [ ] `visitor-dashboard-initial.png` (empty/new state)
- [ ] `visitor-dashboard-event-created.png` (new card with snapshot)
- [ ] `visitor-dashboard-event-known.png` (after Mark Known)
- [ ] `visitor-dashboard-timeline-modal.png` (Open Timeline output)
