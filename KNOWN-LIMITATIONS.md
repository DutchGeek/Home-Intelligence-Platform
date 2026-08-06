# Known Limitations

## Current Scope
- The HIP integration manages HIP but does not replace the package execution model.
- Validation and smoke testing rely on the currently installed module/entity surface.
- The integration reports repository version from the local `VERSION` file, not a remote release feed.
- Support bundle export writes JSON into the Home Assistant configuration directory.

## Environment Limitations
- Full integration behavior still requires verification in a real Home Assistant instance.
- Editor diagnostics in this repository do not include Home Assistant type stubs, so some Python imports report missing stubs even when the integration structure is valid.

## Operational Limitations
- Rollback remains file-based and depends on configuration backups.
- Module health is inferred from installed files and required entity presence.
