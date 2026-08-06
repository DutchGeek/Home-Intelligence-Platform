# Testing

## Validation Priorities
1. Validate the narrowest changed surface first.
2. Validate behavior before broad repository checks when possible.
3. Treat production rollback readiness as part of testing.

## Required Checks Per Change
- YAML syntax remains valid.
- Documentation links remain valid.
- Repository structure remains valid.
- Package-specific acceptance criteria are exercised.

## Home Assistant Validation
- Confirm changed automations load.
- Confirm referenced entities exist or are documented external dependencies.
- Confirm no duplicate entity IDs or duplicate automation responsibilities are introduced.
- Confirm migration steps work in order.
- Confirm rollback steps return the system to the prior working state.

## Evidence
Every change should leave behind explicit validation notes in the PR or release documentation.
