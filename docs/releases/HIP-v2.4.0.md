# HIP v2.4.0

## Summary
HIP v2.4.0 turns HIP into a native Home Assistant integration while preserving Home Assistant Packages as the execution model.

## Delivered
- Native `custom_components/hip` management layer
- Installation validation
- Configuration validation
- Runtime health validation
- Module discovery and status
- Support bundle export and diagnostics
- Smoke tests and version reporting
- Installation, upgrade, rollback, administration, and troubleshooting guides

## Compatibility
- Event Contract unchanged
- Kernel architecture unchanged
- Existing automations preserved
- Existing entities preserved
- All new functionality is optional

## Migration Path
1. Deploy `custom_components/hip`.
2. Restart Home Assistant.
3. Add HIP in Devices & Services.
4. Run integration validation and smoke tests.
5. Review module and runtime status.

## Rollback Instructions
1. Remove or revert `custom_components/hip`.
2. Restore the prior configuration backup if needed.
3. Restart Home Assistant.
4. Verify prior package-only behavior still works.

## Validation Focus
- Clean install path
- Clean upgrade path
- Rollback availability
- Version detection
- Installation validation
- Configuration validation
- Runtime health validation
- Diagnostics and support bundle export
