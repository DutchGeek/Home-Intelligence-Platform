# Package Standards

## Package Model
Each package must own one primary responsibility.

## Allowed Package Roles
- Producer package: detects a trigger and publishes one normalized event.
- Consumer package: subscribes to one or more normalized events and performs one responsibility.
- Core package: owns shared control state and platform-wide logging.

## Rules
- Do not mix unrelated responsibilities in one package.
- Do not duplicate the same responsibility across multiple packages.
- Shared helpers belong in the narrowest stable package that can own them.
- Cross-package dependencies must be documented.
- Reserved packages without implementation should be documented as reserved, not presented as complete.

## Acceptance Criteria
- Inputs are documented.
- Outputs are documented.
- Services called are documented.
- Migration and rollback are documented.
