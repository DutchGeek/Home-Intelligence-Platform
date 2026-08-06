# Test Harness

## Purpose
The HIP Test package provides infrastructure-only validation for runtime behavior without changing production packages.

## Package Location
- homeassistant/packages/test

## Capabilities
- Test event generation
- Test event replay
- Doorbell pressed simulation
- Motion detected simulation
- Camera unavailable simulation
- Piper unavailable simulation
- Notification unavailable simulation
- Logging of validation runs

## Runtime Contract
The test harness publishes `hip_test_run` events into the test package dispatcher. The dispatcher records the event, replays the last event when requested, and exercises the production runtime through existing package entrypoints.

## Usage Notes
- Use the test harness before promoting a release.
- Use the failure simulations to validate fallback behavior and error visibility.
- Keep the harness isolated from production package changes.
