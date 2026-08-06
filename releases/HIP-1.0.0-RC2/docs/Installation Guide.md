# Installation Guide

## Goal
Install HIP as a native Home Assistant integration while continuing to use Home Assistant Packages as the execution modules.

## Steps
1. Copy the HIP repository contents into your Home Assistant configuration directory.
2. Ensure `homeassistant/packages` is present under the configuration directory.
3. Ensure Home Assistant packages are enabled in `configuration.yaml`.
4. Copy `custom_components/hip` into the Home Assistant `custom_components` directory.
5. Ensure `/config/www/snapshots` exists.
6. Restart Home Assistant.
7. Add HIP from Settings -> Devices & Services.
8. Verify the HIP integration loads and exposes version, runtime status, installed modules, and actions.

## Validation
- Run `hip.validate`
- Run `hip.health_check`
- Run `hip.run_smoke_tests`

## Outcome
HIP is installed as a managed integration without replacing the package execution model.
