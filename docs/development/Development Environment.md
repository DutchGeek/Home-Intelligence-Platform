# Development Environment

## Purpose
This repository uses a self-contained Home Assistant development environment for infrastructure validation only.

## Files
- `docker-compose.dev.yml`
- `.env.dev`

## Layout
- The Home Assistant runtime uses an isolated named volume for `/config`.
- The repository is mounted read-only at `/workspace`.
- The bootstrap command creates `/config/configuration.yaml` and copies the existing HIP packages into the runtime config volume.

## Usage
1. Copy `.env.dev` into your local environment or export the same values in your shell.
2. Start the development environment with Docker Compose.
3. Open Home Assistant on the configured port.
4. Validate that the package configuration loads from `homeassistant/packages`.

## Notes
- This environment is for infrastructure testing only.
- No Home Assistant implementation files are changed by the environment bootstrap.
- The config volume is disposable and can be removed to reset the environment.

## Validation Targets
- Package loading
- YAML parsing
- Smoke testing for the current release branch
- Backup and restore rehearsal
