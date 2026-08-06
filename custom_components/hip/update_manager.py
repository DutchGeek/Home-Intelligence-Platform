from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
import logging
from pathlib import Path
from typing import Any

from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class ReleaseInfo:
    version: str
    tag_name: str
    notes: str
    html_url: str
    published_at: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DeploymentState:
    update_status: str = "idle"
    in_progress: bool = False
    last_deployment: str | None = None
    last_deployment_version: str | None = None
    last_validation: str | None = None
    last_report_path: str | None = None
    previous_backup_path: str | None = None
    latest_release_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HipUpdateManager:
    """Read-only release metadata and external deployment status tracking."""

    _STATE_FILE = ".storage/hip/manager_state.json"

    def __init__(self, *, base_path: Path, github_repo: str) -> None:
        self._base_path = base_path
        self._github_repo = github_repo
        self._cached_release: ReleaseInfo | None = None
        self._state = self._load_state()

    @property
    def state(self) -> DeploymentState:
        # Always reload to reflect script-driven deployment updates.
        self._state = self._load_state()
        return self._state

    @property
    def cached_release(self) -> ReleaseInfo | None:
        return self._cached_release

    @property
    def rollback_available(self) -> bool:
        state = self.state
        path = state.previous_backup_path
        if not path:
            return False
        return Path(path).exists()

    async def check_updates(self, hass, *, force: bool = False) -> ReleaseInfo | None:
        if self._cached_release and not force:
            return self._cached_release

        session = async_get_clientsession(hass)
        url = f"https://api.github.com/repos/{self._github_repo}/releases/latest"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "hip-release-checker",
        }
        async with session.get(url, headers=headers, timeout=30) as response:
            response.raise_for_status()
            payload = await response.json()

        release = ReleaseInfo(
            version=str(payload.get("tag_name", "")).lstrip("vV"),
            tag_name=str(payload.get("tag_name", "")),
            notes=str(payload.get("body") or ""),
            html_url=str(payload.get("html_url", "")),
            published_at=payload.get("published_at"),
        )
        self._cached_release = release

        state = self.state
        state.latest_release_url = release.html_url
        self._state = state
        self._persist_state()
        return release

    def mark_validation(self) -> None:
        state = self.state
        state.last_validation = datetime.now(UTC).isoformat()
        self._state = state
        self._persist_state()

    def release_notes_url(self) -> str | None:
        if self._cached_release:
            return self._cached_release.html_url
        return self.state.latest_release_url

    def _load_state(self) -> DeploymentState:
        state_path = self._base_path / self._STATE_FILE
        if not state_path.exists():
            return DeploymentState()
        try:
            payload = json.loads(state_path.read_text(encoding="utf-8"))
            return DeploymentState(**payload)
        except Exception:
            _LOGGER.warning("Failed to load HIP deployment state, resetting state", exc_info=True)
            return DeploymentState()

    def _persist_state(self) -> None:
        state_path = self._base_path / self._STATE_FILE
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(self._state.to_dict(), indent=2), encoding="utf-8")
