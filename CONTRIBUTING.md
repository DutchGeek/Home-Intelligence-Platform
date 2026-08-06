# Contributing

## Principles
- Reliability is more important than features.
- Do not rewrite working code without a clear production need.
- Prefer extending existing implementations over replacing them.
- Minimize change scope.

## Required For Every Change
- Validation steps
- Migration path
- Rollback instructions
- Documentation updates when behavior, structure, or process changes

## Pull Requests
Use the pull request template and complete every section.

## Package Rules
- One responsibility per package
- One event per trigger
- Avoid duplicate automations
- Avoid duplicate entity IDs

## Review Expectations
Changes that increase risk without a clear reliability gain should not merge.
