# Deployment Checklist

## Before Deployment
- Back up the current production configuration.
- Review migration steps in the target release notes.
- Review rollback steps in the target release notes.
- Confirm required directories, helpers, and external dependencies exist.

## Deployment
- Deploy only the approved file set.
- Avoid bundling unrelated changes.
- Restart or reload services in the minimum safe scope.

## After Deployment
- Validate the narrow changed surface first.
- Confirm no duplicate automations or duplicate entity IDs were introduced.
- Confirm logs show expected behavior and no new failures.
- Record deployment result and any follow-up actions.
