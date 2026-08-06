# Entity Naming

## Goals
- Stable entity IDs
- Predictable ownership
- Low migration cost

## Rules
- Preserve existing entity IDs wherever practical.
- Prefix HIP-managed helpers and scripts with hip_.
- Name entities by responsibility, not implementation detail.
- Avoid creating near-duplicate entity IDs that differ only by suffix or wording.
- Document all externally referenced entities that HIP does not create.

## Examples
- input_boolean.hip_enabled
- input_text.hip_last_event
- script.hip_notify_doorbell
- automation.hip_front_door_event
