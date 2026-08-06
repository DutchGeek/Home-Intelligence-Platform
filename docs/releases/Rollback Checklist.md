# Rollback Checklist

## Trigger
Use this checklist when validation fails, production behavior regresses, or operational confidence is lost.

## Steps
- Stop rollout and freeze additional changes.
- Identify the last known good commit or release.
- Restore affected files from the previous release.
- Restart or reload dependent systems as required.
- Re-run the previous release validation path.
- Confirm the original production behavior is restored.
- Document the failure cause and rollback outcome.

## Exit Criteria
- Service restored
- Validation passed on previous release
- Incident notes captured
