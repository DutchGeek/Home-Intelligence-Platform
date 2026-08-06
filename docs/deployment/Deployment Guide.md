# HIP Deployment Guide

## Purpose
This guide covers HIP v2.5.5 external configuration architecture.

## Stateless repository model
The repository must not contain machine-specific values or secrets.

Repository files:
1. `config/dev.env.example`
2. `config/prod.env.example`

Local machine files:
1. `/mnt/apps/configs/hip/dev.env`
2. `/mnt/apps/configs/hip/prod.env`

## Configuration source resolution
Deployment scripts resolve configuration in this order:
1. `HIP_CONFIG_DIR` environment variable
2. Default `/mnt/apps/configs/hip`
3. Fail with a clear error when configuration cannot be created or accessed

Scripts never load deployment secrets from repository env files.

## First run behavior
If the target configuration file does not exist:
1. Scripts create `/mnt/apps/configs/hip` (or `HIP_CONFIG_DIR`).
2. Scripts copy from `config/*.env.example`.
3. Scripts print a setup message and exit successfully.

Development first run message:
1. `Development configuration created.`
2. `Please edit: /mnt/apps/configs/hip/dev.env before deploying.`

Production first run message:
1. `Production configuration created.`
2. `Please edit: /mnt/apps/configs/hip/prod.env before deploying.`

## Migration from repository-based configuration
If legacy files still exist in the repository:
1. `config/dev.env`
2. `config/prod.env`

Scripts automatically migrate them to external location when the target external file does not yet exist:
1. Move `config/dev.env` to `/mnt/apps/configs/hip/dev.env`.
2. Move `config/prod.env` to `/mnt/apps/configs/hip/prod.env`.
3. Print a migration warning.

## Creating and editing local configuration
1. Run `./deploy-dev.sh` or `./deploy-prod.sh` once to auto-generate the local file.
2. Edit the generated local env file.
3. Set required values:
   - `HIP_CONTAINER_NAME`
   - `HIP_HA_URL`
   - `HIP_HA_TOKEN`
4. Optionally set:
   - `HIP_GIT_PULL`
   - `HIP_REQUIRE_CLEAN_TREE`
   - `HIP_CONFIRM_DEPLOYMENT`
   - `HIP_REPOSITORY`
   - `HIP_CONFIG_PATH`

## Deployment commands
Development:
1. `./deploy-dev.sh`

Production:
1. `./deploy-prod.sh`

## CLI modes
### Version mode
1. `./deploy-dev.sh --version`
2. `./deploy-prod.sh --version`

Outputs:
1. HIP Version
2. Git Commit
3. Branch
4. Repository
5. Deployment Target
6. Container
7. Home Assistant URL
8. Configuration file

The command exits immediately after printing.

### Doctor mode
1. `./deploy-dev.sh --doctor`
2. `./deploy-prod.sh --doctor`

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

Doctor includes:
1. `Configuration Source` with full external env file path.

Final status:
1. `READY TO DEPLOY`
2. `FAILED` with all detected issues listed

### Dry run
1. `./deploy-dev.sh --dry-run`
2. `./deploy-prod.sh --dry-run`

Dry run:
1. Loads configuration.
2. Runs preflight validation.
3. Prints planned actions.
4. Exits successfully.

Dry run does not:
1. Ask for confirmation.
2. Create backups.
3. Copy files.
4. Restart containers.
5. Call Home Assistant services.

## Rollback and validation commands
1. `tools/rollback-dev.sh`
2. `tools/rollback-prod.sh`
3. `tools/validate.sh`

These scripts use the same external configuration loader.

## Back up deployment configuration
Back up external env files outside git:
1. `/mnt/apps/configs/hip/dev.env`
2. `/mnt/apps/configs/hip/prod.env`

Recommended backup locations:
1. Encrypted NAS share
2. Secret manager export
3. Offline secure backup

## Multiple NAS installations
For multiple hosts, use one config directory per installation and set `HIP_CONFIG_DIR` per shell/session.

Examples:
1. `HIP_CONFIG_DIR=/mnt/apps/configs/hip-site-a ./deploy-prod.sh`
2. `HIP_CONFIG_DIR=/mnt/apps/configs/hip-site-b ./deploy-prod.sh`

## Development vs production recommendations
Development defaults:
1. `HIP_REQUIRE_CLEAN_TREE=false`
2. `HIP_CONFIRM_DEPLOYMENT=true`

Production defaults:
1. `HIP_REQUIRE_CLEAN_TREE=true`
2. `HIP_CONFIRM_DEPLOYMENT=true`

## Security reminders
Never commit:
1. Tokens
2. URLs tied to private infrastructure
3. Container names unique to host environments
4. Local filesystem paths
5. Machine-specific repository locations
