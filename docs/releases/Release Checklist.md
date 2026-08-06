# Release Checklist

## Pre-Release
- Confirm scope matches the milestone goal.
- Confirm no working Home Assistant behavior was rewritten without documented justification.
- Confirm documentation is updated.
- Confirm migration path is documented.
- Confirm rollback instructions are documented.
- Confirm race-condition review is complete for event fan-out changes.

## Validation
- Run repository validation workflow successfully.
- Validate changed YAML locally or in CI.
- Validate changed Markdown links locally or in CI.
- Validate repository structure rules locally or in CI.
- Execute package-specific acceptance checks.

## Release Approval
- Confirm code owner review.
- Confirm production impact is understood.
- Confirm deployment checklist is attached.
- Confirm rollback checklist is attached.
