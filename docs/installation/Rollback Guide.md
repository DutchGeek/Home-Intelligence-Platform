# Rollback Guide

## Goal
Roll back HIP safely if an installation or upgrade fails.

## Steps
1. Stop after the first failed validation.
2. Restore the last known good Home Assistant configuration backup.
3. Restore the previous `custom_components/hip` contents if they changed.
4. Restore the previous package files if they changed.
5. Restart Home Assistant.
6. Run `hip.health_check` and the prior release smoke tests.

## Success Criteria
- Runtime status returns to healthy.
- Existing automations resume working.
- Previous release behavior is restored without manual entity renames.
