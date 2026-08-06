# Upgrade Procedure

## Scope
Upgrade the development environment or a test deployment to a newer HIP release without changing implementation logic.

## Procedure
1. Review the release notes for migration and rollback instructions.
2. Back up the existing config.
3. Update the repository or deployment artifact.
4. Recreate the container if the image or compose file changed.
5. Start the environment.
6. Run the release smoke test checklist.

## Acceptance Criteria
- Home Assistant boots successfully.
- No YAML errors are reported.
- The release-specific validation passes.
- The backup can still be restored if needed.
