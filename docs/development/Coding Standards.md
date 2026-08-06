# Coding Standards

## Principles
- Reliability is more important than feature growth.
- Do not rewrite working code unless there is a clear production defect or operational need.
- Prefer extending existing implementations over replacing them.
- Minimize scope and blast radius.
- Every change must be production ready.

## Home Assistant YAML
- Keep package files narrowly scoped.
- Preserve existing entity IDs where practical.
- Avoid duplicated automations and duplicated helper definitions.
- Use one published HIP event per trigger.
- Document every service call introduced by a change.

## Change Requirements
- Include validation steps.
- Include migration path.
- Include rollback instructions.
- Include race-condition review for event fan-out or queued behavior.

## Review Standard
A change is incomplete if it lacks documentation, validation, migration guidance, or rollback guidance.
