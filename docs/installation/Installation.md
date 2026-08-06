# Installation

1. Copy the HIP repository contents into your Home Assistant configuration directory.
2. Ensure `/config/packages` is present in the Home Assistant runtime configuration directory.
3. Enable packages in `configuration.yaml`.
4. Copy `custom_components/hip` into `custom_components`.
5. Ensure `/config/www/snapshots` exists.
6. Restart Home Assistant.
7. Add HIP from Settings -> Devices & Services.
8. Run `hip.validate` and `hip.run_smoke_tests`.
