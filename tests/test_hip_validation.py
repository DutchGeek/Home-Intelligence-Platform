from __future__ import annotations

from pathlib import Path

from custom_components.hip.models import is_upgrade_available, normalize_version, release_notes_path
from custom_components.hip.validation import (
    rollback_available,
    runtime_status,
    smoke_test_matrix,
    validate_configuration_text,
    validate_installation_paths,
)


def test_installation_validation_detects_missing_paths(tmp_path: Path) -> None:
    issues = validate_installation_paths(tmp_path, "homeassistant/packages", "homeassistant/dashboards/HIP-Dashboard.yaml")
    assert "packages path missing: homeassistant/packages" in issues
    assert "dashboard path missing: homeassistant/dashboards/HIP-Dashboard.yaml" in issues


def test_upgrade_detection_uses_repository_version() -> None:
    assert is_upgrade_available("2.3.0", "2.4.0") is True
    assert is_upgrade_available("2.4.0", "2.4.0") is False


def test_rollback_detection_uses_release_checklist(tmp_path: Path) -> None:
    release_root = tmp_path / "docs" / "releases"
    release_root.mkdir(parents=True)
    assert rollback_available(tmp_path, "docs/releases") is False
    (release_root / "Rollback Checklist.md").write_text("# Rollback", encoding="utf-8")
    assert rollback_available(tmp_path, "docs/releases") is True


def test_health_status_transitions() -> None:
    assert runtime_status([], [], []) == "healthy"
    assert runtime_status(["missing packages"], [], []) == "installation_error"
    assert runtime_status([], ["packages disabled"], []) == "configuration_error"
    assert runtime_status([], [], ["kernel unhealthy"]) == "degraded"


def test_smoke_test_matrix_requires_contract_and_core_modules() -> None:
    matrix = smoke_test_matrix(
        {
            "kernel": True,
            "security": True,
            "media": True,
            "notifications": True,
            "snapshots": True,
            "dashboard": True,
            "visitor_intelligence": True,
        },
        "hip.event.v1",
    )
    assert all(matrix.values()) is True


def test_configuration_validation_requires_packages() -> None:
    assert validate_configuration_text(None) == ["configuration.yaml not found"]
    assert validate_configuration_text("default_config:\n") == [
        "Home Assistant packages are not enabled in configuration.yaml"
    ]
    assert validate_configuration_text("homeassistant:\n  packages: !include_dir_named homeassistant/packages\n") == []


def test_release_notes_path_resolves_existing_release_file(tmp_path: Path) -> None:
    releases = tmp_path / "docs" / "releases"
    releases.mkdir(parents=True)
    expected = releases / "HIP-v2.4.0.md"
    expected.write_text("# HIP v2.4.0", encoding="utf-8")
    assert release_notes_path(tmp_path, "docs/releases", "2.4.0") == str(expected)


def test_normalize_version_handles_suffixes() -> None:
    assert normalize_version("v2.4.0-rc1") == (2, 4, 0)
