# Rollback Procedure

## Scope
Return the environment to the last known good release if a deployment or upgrade fails.

## Procedure
1. Stop the container.
2. Restore the last known good backup.
3. Revert to the previous release artifact or repository revision.
4. Start Home Assistant.
5. Re-run the smoke test checklist for the previous release.

## Release Safety
- Do not proceed with a second change until rollback has been verified.
- Prefer rollback over ad hoc hotfixes in the development environment.

## Outcome
The environment is restored to a known-good state with documented validation.
