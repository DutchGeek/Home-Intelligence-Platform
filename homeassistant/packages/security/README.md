# Security Package

The Security package is the source of truth for doorbell event detection.

## Components
- automation.hip_front_door_event

## Event Publisher
- Publishes custom event type: hip_doorbell_pressed
- Event payload fields:
	- source
	- message

## Responsibility
- Detect security-domain triggers
- Publish normalized HIP events for downstream packages
