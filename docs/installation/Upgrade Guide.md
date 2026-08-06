# Upgrade Guide

## Goal
Upgrade HIP while preserving packages, entities, Kernel architecture, and Event Contract compatibility.

## Steps
1. Review the target release notes and migration notes.
2. Back up the full Home Assistant configuration.
3. Update the repository contents, including `custom_components/hip` and package files.
4. Restart Home Assistant.
5. Use the HIP integration to run validation, health checks, and smoke tests.
6. Verify installed version, repository version, module status, and runtime status in the HIP integration.

## Acceptance Criteria
- Installed modules remain healthy.
- Runtime status is healthy.
- Smoke tests pass.
- Existing automations and entities continue to function.
