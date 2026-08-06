# HIP Test Package

The HIP Test package provides infrastructure-only validation helpers for HIP runtime testing.

## Responsibilities
- Generate test events
- Replay the last recorded test event
- Simulate unavailable dependencies for validation
- Log validation activity without changing production packages

## Scenarios
- Doorbell pressed
- Motion detected
- Camera unavailable
- Piper unavailable
- Notification unavailable

## Contract
- Test events are published on the local test event bus and dispatched by the test automation in this package.
- Production packages are exercised through existing scripts and services only.
