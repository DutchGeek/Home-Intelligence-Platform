# HIP 1.0.0 RC2 Deployment Report

## Release Bundle
The release bundle is produced as `HIP-1.0.0-RC2.zip`.

## Bundle Layout
- `custom_components/hip/`
- `packages/`
- `hip/`
- `docs/`

## Home Assistant Config Placement

### custom_components
Copy `custom_components/hip/` to:
- `/config/custom_components/hip/`

### packages
Copy the contents of `packages/` to:
- `/config/packages/`

Included packages:
- `ai/`
- `cameras/`
- `device_registry/`
- `hip_core/`
- `media/`
- `notifications/`
- `security/`
- `visitor_intelligence/`

### hip
Copy the contents of `hip/` to:
- `/config/hip/`

Included files and directories:
- `HIP-Dashboard.yaml` -> `/config/hip/HIP-Dashboard.yaml`
- `deploy.yaml` -> `/config/hip/deploy.yaml`
- `www/snapshots/.gitkeep` -> `/config/hip/www/snapshots/.gitkeep`
- `www/snapshots/history/.gitkeep` -> `/config/hip/www/snapshots/history/.gitkeep`

### docs
Copy the contents of `docs/` to:
- `/config/docs/hip/` if you want the operational docs available inside the Home Assistant config tree

## Manual Action Required
- Enable Home Assistant packages in `configuration.yaml` if they are not already enabled.

## Post-Extraction Validation
Run:
- `hip.validate`
- `hip.health_check`
- `hip.run_smoke_tests`
- `hip.module_status`
- `hip.kernel_status`

## Verification Coverage
`hip/deploy.yaml` is included to verify:
- HIP integration exists
- Packages are loaded
- Services are registered
- Kernel is running
- Modules are healthy
