# Installation Validation Checklist

## Integration Files
- [ ] `manifest.json` present and valid
- [ ] `services.yaml` present and valid
- [ ] translations present
- [ ] diagnostics module present
- [ ] config flow present
- [ ] options flow present
- [ ] update entity present
- [ ] repairs integration path present

## Home Assistant Behavior
- [ ] HIP appears in Devices & Services
- [ ] Config flow creates a single HIP entry
- [ ] Options flow updates paths and documentation URL
- [ ] Buttons are created for validation, reload, smoke tests, support bundle, and documentation
- [ ] Sensors are created for installed version, kernel version, runtime status, and installed modules
- [ ] Update entity shows installed and repository versions

## Service Validation
- [ ] `hip.validate`
- [ ] `hip.reload`
- [ ] `hip.health_check`
- [ ] `hip.export_support_bundle`
- [ ] `hip.run_smoke_tests`
- [ ] `hip.version`
- [ ] `hip.kernel_status`
- [ ] `hip.module_status`
- [ ] `hip.event_statistics`

## Package Validation
- [ ] All package YAML files load
- [ ] Package discovery reports expected modules
- [ ] Existing runtime entities still exist

## Diagnostics
- [ ] Diagnostics payload downloads
- [ ] Support bundle file is created
- [ ] Support bundle includes module versions, configuration, registry, event statistics, recent errors, and runtime metrics

## Rollback Readiness
- [ ] Backup exists
- [ ] Rollback guide reviewed
- [ ] Prior package-only behavior can be restored
