# Troubleshooting Guide

## Installation Problems
- Run `hip.validate` to check package path, dashboard path, and configuration.
- Confirm `configuration.yaml` enables packages.
- Confirm `custom_components/hip` is present.

## Runtime Problems
- Run `hip.health_check`.
- Check module status with `hip.module_status`.
- Export a support bundle and review runtime metrics and recent errors.

## Version Problems
- Run `hip.version`.
- Compare installed version and repository version.
- Review migration notes from the update entity.

## Recovery
- If health remains degraded, follow the Rollback Guide.
