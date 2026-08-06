from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue, async_delete_issue
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    ATTR_CONTRACT_VERSION,
    ATTR_DEPLOYMENT_TARGET,
    ATTR_DAILY_HOMEPOD_COUNT,
    ATTR_DAILY_NOTIFICATION_COUNT,
    ATTR_DAILY_SNAPSHOT_COUNT,
    ATTR_DAILY_VISITOR_COUNT,
    ATTR_EVENT_TOTAL,
    ATTR_LAST_DEPLOYMENT,
    ATTR_LAST_DEPLOYMENT_VERSION,
    ATTR_LAST_EVENT_AT,
    ATTR_LAST_EVENT_TYPE,
    ATTR_LAST_REPORT_PATH,
    ATTR_LAST_VALIDATION,
    ATTR_LATEST_RELEASE,
    ATTR_RELEASE_NOTES_URL,
    ATTR_UPDATE_STATUS,
    COORDINATOR_NAME,
    CONF_CUSTOM_COMPONENTS_PATH,
    CONF_DEPLOYMENT_TARGET,
    CONF_DASHBOARD_PATH,
    CONF_DOCUMENTATION_URL,
    CONF_GITHUB_REPO,
    CONF_HIP_PATH,
    CONF_PACKAGES_PATH,
    CONF_RELEASE_NOTES_PATH,
    DEFAULT_CUSTOM_COMPONENTS_PATH,
    DEFAULT_DEPLOYMENT_TARGET,
    DEFAULT_DASHBOARD_PATH,
    DEFAULT_DOCUMENTATION_URL,
    DEFAULT_GITHUB_REPO,
    DEFAULT_HIP_PATH,
    DEFAULT_PACKAGES_PATH,
    DEFAULT_RELEASE_NOTES_PATH,
    DOMAIN,
    INTEGRATION_VERSION,
    MODULE_DEFINITIONS,
    SCAN_INTERVAL,
    SUPPORT_BUNDLE_PREFIX,
)
from .models import HipStatus, ModuleStatus, first_existing_path, is_upgrade_available, release_notes_path
from .update_manager import HipUpdateManager
from .validation import (
    runtime_status,
    smoke_test_matrix,
    validate_configuration_text,
    validate_installation_paths,
    validate_runtime_health,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class ValidationResult:
    installation_valid: bool
    configuration_valid: bool
    runtime_healthy: bool
    installation_issues: list[str]
    configuration_issues: list[str]
    runtime_issues: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "installation_valid": self.installation_valid,
            "configuration_valid": self.configuration_valid,
            "runtime_healthy": self.runtime_healthy,
            "installation_issues": self.installation_issues,
            "configuration_issues": self.configuration_issues,
            "runtime_issues": self.runtime_issues,
        }


class HipDataUpdateCoordinator(DataUpdateCoordinator[HipStatus]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.update_manager = HipUpdateManager(
            base_path=Path(self.hass.config.path()),
            github_repo=self.github_repo,
        )
        super().__init__(hass, _LOGGER, name=COORDINATOR_NAME, update_interval=SCAN_INTERVAL)

    @property
    def base_path(self) -> Path:
        return Path(self.hass.config.path())

    @property
    def packages_path(self) -> str:
        if CONF_PACKAGES_PATH in self.entry.options:
            return self.entry.options[CONF_PACKAGES_PATH]
        if self.deployment_target == "development":
            return "homeassistant/packages"
        return DEFAULT_PACKAGES_PATH

    @property
    def custom_components_path(self) -> str:
        return self.entry.options.get(CONF_CUSTOM_COMPONENTS_PATH, DEFAULT_CUSTOM_COMPONENTS_PATH)

    @property
    def hip_path(self) -> str:
        return self.entry.options.get(CONF_HIP_PATH, DEFAULT_HIP_PATH)

    @property
    def dashboard_path(self) -> str:
        if CONF_DASHBOARD_PATH in self.entry.options:
            return self.entry.options[CONF_DASHBOARD_PATH]
        if self.deployment_target == "development":
            return "homeassistant/dashboards/HIP-Dashboard.yaml"
        return DEFAULT_DASHBOARD_PATH

    @property
    def release_notes_root(self) -> str:
        return self.entry.options.get(CONF_RELEASE_NOTES_PATH, DEFAULT_RELEASE_NOTES_PATH)

    @property
    def documentation_url(self) -> str:
        return self.entry.options.get(CONF_DOCUMENTATION_URL, DEFAULT_DOCUMENTATION_URL)

    @property
    def github_repo(self) -> str:
        return self.entry.options.get(CONF_GITHUB_REPO, DEFAULT_GITHUB_REPO)

    @property
    def deployment_target(self) -> str:
        return self.entry.options.get(CONF_DEPLOYMENT_TARGET, DEFAULT_DEPLOYMENT_TARGET)

    async def _async_update_data(self) -> HipStatus:
        installed_version = self._read_installed_version() or INTEGRATION_VERSION
        latest_release = await self._latest_release()
        repository_version = latest_release.version if latest_release else self._read_repository_version()
        kernel_version = repository_version or installed_version
        contract_version = self._state("input_text.hip_last_event_contract_version") or "hip.event.v1"
        modules = self._discover_modules(repository_version or installed_version)
        validation = self._build_validation(modules)
        runtime_status = self._runtime_status(validation)
        event_statistics = self._event_statistics()
        notes_path = release_notes_path(self.base_path, self.release_notes_root, repository_version)
        rollback_ready = self.update_manager.rollback_available
        deployment_state = self.update_manager.state
        status = HipStatus(
            installed_version=installed_version,
            repository_version=repository_version or installed_version,
            kernel_version=kernel_version,
            contract_version=contract_version,
            runtime_status=runtime_status,
            upgrade_available=is_upgrade_available(installed_version, repository_version),
            migration_notes=notes_path or (latest_release.notes[:500] if latest_release and latest_release.notes else None),
            rollback_available=rollback_ready,
            deployment_target=self.deployment_target,
            update_status=deployment_state.update_status,
            release_notes_url=self.update_manager.release_notes_url(),
            last_deployment=deployment_state.last_deployment,
            last_deployment_version=deployment_state.last_deployment_version,
            last_validation=deployment_state.last_validation,
            last_report_path=deployment_state.last_report_path,
            modules=modules,
            validation=validation.to_dict(),
            event_statistics=event_statistics,
        )
        self._sync_repairs(status)
        return status

    async def _latest_release(self):
        try:
            return await self.update_manager.check_updates(self.hass)
        except Exception as err:  # pragma: no cover - network variability
            _LOGGER.warning("Unable to refresh HIP release metadata: %s", err)
            return self.update_manager.cached_release

    def _read_repository_version(self) -> str | None:
        version_file = self.base_path / "VERSION"
        if not version_file.exists():
            return None
        return version_file.read_text(encoding="utf-8").strip() or None

    def _read_installed_version(self) -> str | None:
        manifest_file = self.base_path / self.custom_components_path / "hip" / "manifest.json"
        if not manifest_file.exists():
            return None
        try:
            payload = json.loads(manifest_file.read_text(encoding="utf-8"))
        except ValueError:
            return None
        version = payload.get("version")
        if isinstance(version, str) and version.strip():
            return version.strip()
        return None

    def _state(self, entity_id: str) -> str | None:
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        return state.state

    def _entity_exists(self, entity_id: str) -> bool:
        return self.hass.states.get(entity_id) is not None

    def _discover_modules(self, version: str) -> dict[str, ModuleStatus]:
        modules: dict[str, ModuleStatus] = {}
        for key, definition in MODULE_DEFINITIONS.items():
            paths = list(definition["paths"])
            if key == "dashboard":
                paths = [self.dashboard_path]
            installed = first_existing_path(self.base_path, paths) is not None
            issues: list[str] = []
            required_entities = list(definition["entities"])
            enabled = installed and all(self._entity_exists(entity_id) for entity_id in required_entities) if required_entities else installed
            healthy = enabled
            if installed and required_entities:
                missing = [entity_id for entity_id in required_entities if not self._entity_exists(entity_id)]
                if missing:
                    healthy = False
                    issues.extend(f"missing entity: {entity_id}" for entity_id in missing)
            if not installed:
                issues.append("module files not found")
            modules[key] = ModuleStatus(
                key=key,
                title=str(definition["title"]),
                installed=installed,
                enabled=enabled,
                healthy=healthy,
                version=version if installed else None,
                issues=issues,
            )
        return modules

    def _build_validation(self, modules: dict[str, ModuleStatus]) -> ValidationResult:
        installation_issues = validate_installation_paths(self.base_path, self.packages_path, self.dashboard_path)
        runtime_issues: list[str] = []

        configuration_file = self.base_path / "configuration.yaml"
        configuration_issues = validate_configuration_text(
            configuration_file.read_text(encoding="utf-8") if configuration_file.exists() else None
        )

        kernel = modules.get("kernel")
        if kernel and not kernel.healthy:
            runtime_issues.extend(kernel.issues or ["kernel unhealthy"])
        for module in modules.values():
            if module.installed and not module.healthy:
                runtime_issues.extend(f"{module.title}: {issue}" for issue in module.issues)

        runtime_issues.extend(
            validate_runtime_health(
                registered_services={
                    f"{DOMAIN}.{service_name}"
                    for service_name in self.hass.services.async_services().get(DOMAIN, {})
                },
                module_health={key: module.healthy for key, module in modules.items()},
                registry_state_count=sum(
                    1
                    for state in self.hass.states.async_all("input_text")
                    if state.entity_id.startswith("input_text.hip_registry_")
                ),
                event_runtime_ok=bool(self._entity_exists("script.hip_event_manager") and self._entity_exists("script.hip_event_dispatch")),
                dashboard_exists=(self.base_path / self.dashboard_path).exists(),
                automation_states={
                    "automation.hip_front_door_event": self._state("automation.hip_front_door_event"),
                    "automation.hip_test_validation_dispatch": self._state("automation.hip_test_validation_dispatch"),
                },
            )
        )

        return ValidationResult(
            installation_valid=not installation_issues,
            configuration_valid=not configuration_issues,
            runtime_healthy=not runtime_issues,
            installation_issues=installation_issues,
            configuration_issues=configuration_issues,
            runtime_issues=runtime_issues,
        )

    def _runtime_status(self, validation: ValidationResult) -> str:
        return runtime_status(
            validation.installation_issues,
            validation.configuration_issues,
            validation.runtime_issues,
        )

    def _event_statistics(self) -> dict[str, Any]:
        return {
            ATTR_EVENT_TOTAL: self._state("input_number.hip_event_total") or "0",
            ATTR_DAILY_VISITOR_COUNT: self._state("input_number.hip_daily_visitor_count") or "0",
            ATTR_DAILY_NOTIFICATION_COUNT: self._state("input_number.hip_daily_notification_count") or "0",
            ATTR_DAILY_HOMEPOD_COUNT: self._state("input_number.hip_daily_homepod_count") or "0",
            ATTR_DAILY_SNAPSHOT_COUNT: self._state("input_number.hip_daily_snapshot_count") or "0",
            ATTR_LAST_EVENT_AT: self._state("input_datetime.hip_last_event_at"),
            ATTR_LAST_EVENT_TYPE: self._state("input_text.hip_last_event_type"),
            ATTR_CONTRACT_VERSION: self._state("input_text.hip_last_event_contract_version") or "hip.event.v1",
        }

    async def validate(self) -> dict[str, Any]:
        self.update_manager.mark_validation()
        await self.async_request_refresh()
        return self.data.validation

    async def health_check(self) -> dict[str, Any]:
        await self.async_request_refresh()
        return {
            "runtime_status": self.data.runtime_status,
            "kernel": self.data.modules["kernel"].to_dict(),
            "issues": self.data.validation["runtime_issues"],
        }

    async def reload(self) -> dict[str, Any]:
        await self.hass.services.async_call("homeassistant", "reload_core_config", blocking=True)
        await self.async_request_refresh()
        return {"runtime_status": self.data.runtime_status}

    async def version_info(self) -> dict[str, Any]:
        await self.async_request_refresh()
        return {
            "installed_version": self.data.installed_version,
            "repository_version": self.data.repository_version,
            "kernel_version": self.data.kernel_version,
            "contract_version": self.data.contract_version,
            "upgrade_available": self.data.upgrade_available,
            "migration_notes": self.data.migration_notes,
            "rollback_available": self.data.rollback_available,
            ATTR_DEPLOYMENT_TARGET: self.data.deployment_target,
            ATTR_UPDATE_STATUS: self.data.update_status,
            ATTR_RELEASE_NOTES_URL: self.data.release_notes_url,
        }

    async def kernel_status(self) -> dict[str, Any]:
        await self.async_request_refresh()
        return self.data.modules["kernel"].to_dict()

    async def module_status(self) -> dict[str, Any]:
        await self.async_request_refresh()
        return {key: module.to_dict() for key, module in self.data.modules.items()}

    async def event_statistics(self) -> dict[str, Any]:
        await self.async_request_refresh()
        return dict(self.data.event_statistics)

    async def run_smoke_tests(self) -> dict[str, Any]:
        await self.async_request_refresh()
        smoke_tests = smoke_test_matrix(
            {
                "kernel": self.data.modules["kernel"].healthy,
                "security": self.data.modules["security"].healthy,
                "media": self.data.modules["media"].healthy,
                "notifications": self.data.modules["notifications"].healthy,
                "snapshots": self.data.modules["snapshots"].healthy,
                "dashboard": self.data.modules["dashboard"].installed,
                "visitor_intelligence": self.data.modules["visitor_intelligence"].healthy,
            },
            self.data.contract_version,
        )
        return {"passed": all(smoke_tests.values()), "checks": smoke_tests}

    async def check_updates(self) -> dict[str, Any]:
        release = await self.update_manager.check_updates(self.hass, force=True)
        await self.async_request_refresh()
        return {
            ATTR_LATEST_RELEASE: release.version if release else None,
            ATTR_RELEASE_NOTES_URL: release.html_url if release else None,
            ATTR_UPDATE_STATUS: self.data.update_status,
            "upgrade_available": self.data.upgrade_available,
        }

    async def open_release_notes(self) -> dict[str, Any]:
        await self.async_request_refresh()
        release_notes_url = self.data.release_notes_url or self.documentation_url
        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "HIP Release Notes",
                "message": release_notes_url,
            },
            blocking=True,
        )
        return {ATTR_RELEASE_NOTES_URL: release_notes_url}

    async def deployment_status(self) -> dict[str, Any]:
        await self.async_request_refresh()
        return {
            ATTR_DEPLOYMENT_TARGET: self.data.deployment_target,
            ATTR_UPDATE_STATUS: self.data.update_status,
            ATTR_LAST_DEPLOYMENT: self.data.last_deployment,
            ATTR_LAST_DEPLOYMENT_VERSION: self.data.last_deployment_version,
            ATTR_LAST_VALIDATION: self.data.last_validation,
            ATTR_LAST_REPORT_PATH: self.data.last_report_path,
            ATTR_RELEASE_NOTES_URL: self.data.release_notes_url,
        }

    async def export_support_bundle(self) -> dict[str, Any]:
        await self.async_request_refresh()
        payload = self._support_bundle_payload()
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        bundle_path = self.base_path / f"{SUPPORT_BUNDLE_PREFIX}_{timestamp}.json"
        bundle_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return {"support_bundle_path": str(bundle_path), "payload": payload}

    def diagnostics_payload(self) -> dict[str, Any]:
        if self.data is None:
            return {}
        return self._support_bundle_payload()

    def _support_bundle_payload(self) -> dict[str, Any]:
        registry = {
            state.entity_id: state.state
            for state in self.hass.states.async_all("input_text")
            if state.entity_id.startswith("input_text.hip_registry_")
        }
        runtime_metrics = {
            "event_total": self._state("input_number.hip_event_total"),
            "daily_visitor_count": self._state("input_number.hip_daily_visitor_count"),
            "daily_notification_count": self._state("input_number.hip_daily_notification_count"),
            "daily_homepod_count": self._state("input_number.hip_daily_homepod_count"),
            "daily_snapshot_count": self._state("input_number.hip_daily_snapshot_count"),
            "last_event_at": self._state("input_datetime.hip_last_event_at"),
            "last_event_type": self._state("input_text.hip_last_event_type"),
        }
        recent_errors = list(self.data.validation["runtime_issues"]) if self.data else []
        return {
            "installed_version": self.data.installed_version if self.data else INTEGRATION_VERSION,
            "repository_version": self.data.repository_version if self.data else INTEGRATION_VERSION,
            "kernel_version": self.data.kernel_version if self.data else INTEGRATION_VERSION,
            "module_versions": {key: module.version for key, module in self.data.modules.items()} if self.data else {},
            "configuration": {
                "packages_path": self.packages_path,
                "dashboard_path": self.dashboard_path,
                "documentation_url": self.documentation_url,
                "release_notes_path": self.release_notes_root,
            },
            "device_registry": registry,
            "event_statistics": self.data.event_statistics if self.data else {},
            "recent_errors": recent_errors,
            "runtime_metrics": runtime_metrics,
            "deployment": {
                "deployment_target": self.data.deployment_target if self.data else self.deployment_target,
                "update_status": self.data.update_status if self.data else "unknown",
                "last_deployment": self.data.last_deployment if self.data else None,
                "last_deployment_version": self.data.last_deployment_version if self.data else None,
                "last_validation": self.data.last_validation if self.data else None,
                "last_report_path": self.data.last_report_path if self.data else None,
                "release_notes_url": self.data.release_notes_url if self.data else None,
            },
        }

    def _sync_repairs(self, status: HipStatus) -> None:
        issue_id = "runtime_health"
        if status.runtime_status == "healthy":
            async_delete_issue(self.hass, DOMAIN, issue_id)
            return
        issue_kwargs: dict[str, Any] = {
            "is_fixable": False,
            "severity": IssueSeverity.WARNING,
            "translation_key": "runtime_health",
            "issue_domain": DOMAIN,
            "learn_more_url": self.documentation_url,
        }
        try:
            async_create_issue(
                self.hass,
                DOMAIN,
                issue_id,
                translation_placeholders={"runtime_status": status.runtime_status},
                **issue_kwargs,
            )
        except TypeError:
            # Compatibility fallback for HA builds that do not support issue translation placeholders.
            async_create_issue(self.hass, DOMAIN, issue_id, **issue_kwargs)
