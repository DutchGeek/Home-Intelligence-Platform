from __future__ import annotations

from pathlib import Path
from typing import Any


def validate_installation_paths(base_path: Path, packages_path: str, dashboard_path: str) -> list[str]:
    issues: list[str] = []
    if not (base_path / packages_path).exists():
        issues.append(f"packages path missing: {packages_path}")
    if not (base_path / dashboard_path).exists():
        issues.append(f"dashboard path missing: {dashboard_path}")
    return issues


def validate_configuration_text(configuration_text: str | None) -> list[str]:
    if configuration_text is None:
        return ["configuration.yaml not found"]
    if "packages:" not in configuration_text:
        return ["Home Assistant packages are not enabled in configuration.yaml"]
    return []


def smoke_test_matrix(modules: dict[str, bool], contract_version: str) -> dict[str, bool]:
    return {
        "doorbell_event": modules.get("security", False),
        "snapshot": modules.get("snapshots", False),
        "notification": modules.get("notifications", False),
        "homepod_announcement": modules.get("media", False),
        "visitor_timeline": modules.get("visitor_intelligence", False),
        "kernel_event": modules.get("kernel", False),
        "support_bundle": modules.get("kernel", False),
        "dashboard_present": modules.get("dashboard", False),
        "contract_available": contract_version == "hip.event.v1",
    }


def rollback_available(base_path: Path, release_notes_root: str) -> bool:
    return (base_path / release_notes_root / "Rollback Checklist.md").exists()


def runtime_status(installation_issues: list[str], configuration_issues: list[str], runtime_issues: list[str]) -> str:
    if installation_issues:
        return "installation_error"
    if configuration_issues:
        return "configuration_error"
    if runtime_issues:
        return "degraded"
    return "healthy"


def validate_runtime_health(
    *,
    registered_services: set[str],
    module_health: dict[str, bool],
    registry_state_count: int,
    event_runtime_ok: bool,
    dashboard_exists: bool,
    automation_states: dict[str, str | None],
) -> list[str]:
    issues: list[str] = []

    required_services = {
        "hip.validate",
        "hip.check_updates",
        "hip.open_release_notes",
        "hip.deployment_status",
        "hip.run_smoke_tests",
        "hip.export_support_bundle",
    }
    if registered_services:
        missing_services = sorted(required_services - registered_services)
        if missing_services:
            issues.append(f"services not registered: {', '.join(missing_services)}")

    unhealthy_modules = [name for name, healthy in module_health.items() if not healthy]
    if unhealthy_modules:
        issues.append(f"unhealthy modules: {', '.join(sorted(unhealthy_modules))}")

    if registry_state_count == 0:
        issues.append("registry healthy check failed: no hip_registry pointers found")

    if not event_runtime_ok:
        issues.append("event runtime healthy check failed")

    if not dashboard_exists:
        issues.append("dashboard availability check failed")

    failed_automations = [entity_id for entity_id, state in automation_states.items() if state in {None, "unavailable", "unknown"}]
    if failed_automations:
        issues.append(f"automation validation failures detected: {', '.join(sorted(failed_automations))}")

    return issues
