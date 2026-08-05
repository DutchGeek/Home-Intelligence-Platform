# HIP Core Package

The HIP Core package provides shared controls and event logging.

## Components
- Global enable switch: input_boolean.hip_enabled
- Last event register: input_text.hip_last_event
- Event logging scripts:
	- script.hip_event_log
	- script.hip_log_event (compatibility alias)
- Event listener:
	- automation.hip_doorbell_event_logger

## Responsibility
- Keep platform-wide runtime state
- Persist and log normalized HIP events
