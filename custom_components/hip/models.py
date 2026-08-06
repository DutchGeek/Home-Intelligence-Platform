from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ModuleStatus:
    key: str
    title: str
    installed: bool
    enabled: bool
    healthy: bool
    version: str | None
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class HipStatus:
    installed_version: str
    repository_version: str
    kernel_version: str
    contract_version: str
    runtime_status: str
    upgrade_available: bool
    migration_notes: str | None
    rollback_available: bool
    deployment_target: str
    update_status: str
    release_notes_url: str | None
    last_deployment: str | None
    last_deployment_version: str | None
    last_validation: str | None
    last_report_path: str | None
    modules: dict[str, ModuleStatus]
    validation: dict[str, Any]
    event_statistics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "installed_version": self.installed_version,
            "repository_version": self.repository_version,
            "kernel_version": self.kernel_version,
            "contract_version": self.contract_version,
            "runtime_status": self.runtime_status,
            "upgrade_available": self.upgrade_available,
            "migration_notes": self.migration_notes,
            "rollback_available": self.rollback_available,
            "deployment_target": self.deployment_target,
            "update_status": self.update_status,
            "release_notes_url": self.release_notes_url,
            "last_deployment": self.last_deployment,
            "last_deployment_version": self.last_deployment_version,
            "last_validation": self.last_validation,
            "last_report_path": self.last_report_path,
            "modules": {key: status.to_dict() for key, status in self.modules.items()},
            "validation": self.validation,
            "event_statistics": self.event_statistics,
        }


def normalize_version(version: str | None) -> tuple[int, int, int]:
    if not version:
        return (0, 0, 0)
    cleaned = version.strip().lstrip("vV").split("-", 1)[0]
    parts = cleaned.split(".")
    padded = (parts + ["0", "0", "0"])[:3]
    values: list[int] = []
    for part in padded:
        digits = "".join(char for char in part if char.isdigit())
        values.append(int(digits or "0"))
    return tuple(values)  # type: ignore[return-value]


def is_upgrade_available(installed_version: str | None, repository_version: str | None) -> bool:
    return normalize_version(repository_version) > normalize_version(installed_version)


def first_existing_path(base_path: Path, candidates: list[str]) -> Path | None:
    for candidate in candidates:
        path = base_path / candidate
        if path.exists():
            return path
    return None


def release_notes_path(base_path: Path, release_notes_root: str, version: str | None) -> str | None:
    if not version:
        return None
    candidate = base_path / release_notes_root / f"HIP-v{version}.md"
    return str(candidate) if candidate.exists() else None
