# HIP v2.4.0 RC1 Deployment

## Goal
Prepare HIP for installation into a real Home Assistant development environment using the native HIP integration and package execution model.

## Readiness Summary
- Custom integration present under `custom_components/hip`
- Package execution model preserved
- Kernel architecture unchanged
- Event Contract unchanged
- Installation, health, diagnostics, and smoke-test services defined
- Deployment remains optional and backward compatible

## Deployment Steps
1. Back up the Home Assistant configuration directory.
2. Copy `custom_components/hip` into the Home Assistant `custom_components` directory.
3. Copy the HIP package tree into the Home Assistant configuration directory.
4. Ensure packages are enabled in `configuration.yaml`.
5. Ensure `/config/www/snapshots` exists.
6. Restart Home Assistant.
7. Add HIP from Settings -> Devices & Services.
8. Run validation and smoke tests from the HIP integration.

## Deployment Gates
- Installation validation passes
- Configuration validation passes
- Runtime health is healthy or understood
- Support bundle export works
- Module discovery matches the installed package set

## Rollback Trigger
Rollback is required if installation validation fails, runtime status degrades unexpectedly, or the integration cannot be loaded in Home Assistant.
