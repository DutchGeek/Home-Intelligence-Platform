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
        "kernel_loaded": modules.get("kernel", False),
        "security_loaded": modules.get("security", False),
        "media_loaded": modules.get("media", False),
        "notifications_loaded": modules.get("notifications", False),
        "snapshots_loaded": modules.get("snapshots", False),
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
