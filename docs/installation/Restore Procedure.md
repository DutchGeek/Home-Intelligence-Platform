# Restore Procedure

## Scope
Restore a previously backed up Home Assistant config into the development environment.

## Procedure
1. Stop the container.
2. Replace the current `/config` contents with the selected backup.
3. Verify `configuration.yaml` exists.
4. Verify `homeassistant/packages` exists.
5. Start Home Assistant.
6. Confirm the restored configuration loads without YAML errors.

## Validation
- Packages load
- Expected helpers and scripts are present
- No unexpected entity renames occurred

## Outcome
The environment returns to a previously known-good state.
