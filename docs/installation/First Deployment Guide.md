# First Deployment Guide

## Goal
Deploy HIP into a fresh Home Assistant environment with the development environment as the rehearsal target.

## Steps
1. Prepare the backup and restore path before deployment.
2. Start the development environment once and confirm the repo mounts correctly.
3. Copy the production package tree into the target Home Assistant config.
4. Create the required snapshot directory.
5. Deploy the configuration.
6. Run the smoke test checklist.
7. Record the deployment outcome and any follow-up actions.

## Success Criteria
- Configuration loads
- Doorbell automation works
- Notification, media, and snapshot paths work
- Rollback can be executed from the documented backup
