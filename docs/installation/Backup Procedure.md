# Backup Procedure

## Scope
Back up the Home Assistant config volume before any deployment, upgrade, or rollback rehearsal.

## Procedure
1. Stop the development or production Home Assistant container.
2. Copy the full `/config` contents to a timestamped backup location.
3. Preserve the package tree and any runtime state.
4. Verify the backup contains `configuration.yaml`, `homeassistant/packages`, and `www`.
5. Record the backup location and timestamp.

## Minimum Backup Set
- configuration.yaml
- homeassistant/packages
- www
- .storage, if present

## Outcome
A known-good configuration snapshot is available for restore or rollback.
