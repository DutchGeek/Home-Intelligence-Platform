# HIP Deployment Guide

## Purpose
This guide covers the hardened deployment workflow for HIP v2.5.4.

## Initial setup
1. Ensure Docker, curl, and git are installed on the deployment machine.
2. Ensure the Home Assistant container exists and is running.
3. Ensure this repository is cloned locally.

## Create development configuration
1. Copy `config/dev.env.example` to `config/dev.env`.
2. Edit `config/dev.env` and set:
   - `HIP_CONTAINER_NAME`
   - `HIP_HA_URL`
   - `HIP_HA_TOKEN`
3. Keep `config/dev.env` local. It is ignored by git.

## Create production configuration
1. Copy `config/prod.env.example` to `config/prod.env`.
2. Edit `config/prod.env` and set production values.
3. Keep `config/prod.env` local. It is ignored by git.

## Generate Home Assistant Long-Lived Token
1. Open Home Assistant user profile.
2. In Long-Lived Access Tokens, create a new token.
3. Copy the token into `HIP_HA_TOKEN` in the matching env file.

## Run development deployment
Use one command:

`./deploy-dev.sh`

The script will:
1. Load `config/dev.env`.
2. Validate prerequisites and configuration.
3. Apply git checks and optional pull.
4. Back up current HIP files.
5. Deploy repository runtime files.
6. Restart Home Assistant.
7. Wait for startup.
8. Run `hip.validate` and `hip.run_smoke_tests` when available.
9. Print a colorized deployment summary and report location.

## Run production deployment
Use one command:

`./deploy-prod.sh`

Production-specific behavior:
1. Dirty git tree aborts deployment.
2. Preflight failures abort deployment.

## Dry-run
Use:

`./deploy-dev.sh --dry-run`
`./deploy-prod.sh --dry-run`

Dry-run:
1. Loads configuration.
2. Runs full preflight validation.
3. Prints every planned deployment action.
4. Exits successfully without asking for confirmation.
5. Does not create backups, copy files, restart containers, or call Home Assistant services.

## Version mode
Use:

`./deploy-dev.sh --version`
`./deploy-prod.sh --version`

This loads configuration, prints deployment metadata, and exits immediately:
1. HIP Version
2. Git Commit
3. Branch
4. Repository
5. Deployment Target
6. Container
7. Home Assistant URL
8. Configuration file

## Doctor mode
Use:

`./deploy-dev.sh --doctor`
`./deploy-prod.sh --doctor`

Doctor verifies:
1. Repository
2. Git
3. Docker
4. Container exists
5. Configuration path
6. Token configured
7. Home Assistant reachable
8. Runtime directories
9. Permissions

Doctor output ends with:
1. `READY TO DEPLOY` when all checks pass.
2. `FAILED` plus a full issue list when one or more checks fail.

## Rollback
Development rollback:

`tools/rollback-dev.sh`

Production rollback:

`tools/rollback-prod.sh`

Each rollback:
1. Restores latest backup for the target.
2. Restarts Home Assistant.
3. Runs validation and smoke tests when available.
4. Prints rollback duration and report location.

## Troubleshooting
- If config file is missing:
  - Scripts create it from the example and exit.
  - Edit the generated file and rerun.
- If token is missing:
  - Set `HIP_HA_TOKEN` in the target env file.
- If Home Assistant services are not available yet:
  - Scripts print:
    - `HIP services not available yet.`
    - `Skipping validation.`
  - Deployment continues.
- If production deployment aborts on dirty tree:
  - Commit or stash local changes, then rerun.
