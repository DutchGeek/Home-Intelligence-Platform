# Device Registry

## Purpose
The Device Registry is the Kernel's private source of truth for entity and service identifiers used by HIP.

## Rules
- Only the Kernel may resolve devices through the registry.
- Production packages must consume logical devices only.
- Packages must never access entity IDs directly as part of their operating model.
- Any new device, helper, or service target must be added to the registry first.
- The registry must be updated before downstream kernel behavior is changed.

## Contract
Registry entries are stored as helper entities and referenced privately by the Kernel.

The Event Contract exposes logical devices only. Registry entries are not a public package interface.

## Operational Guidance
- Review registry updates during code review.
- Treat registry changes as part of the deployment and rollback surface.
- Update the validation checklist when registry entries change.
