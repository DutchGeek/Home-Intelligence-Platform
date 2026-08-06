# Security Package

The Security package is the source of truth for doorbell event detection.

## Components
- automation.hip_front_door_event

## Event Publisher
- Invokes script.hip_event_manager
- Supplies the normalized trigger input for contract version hip.event.v1

## Responsibility
- Detect security-domain triggers
- Hand one event trigger to the centralized event runtime
