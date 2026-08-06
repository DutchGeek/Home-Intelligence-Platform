from __future__ import annotations

from homeassistant.components.update import UpdateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HipDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: HipDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HipUpdateEntity(coordinator, entry.entry_id)])


class HipUpdateEntity(CoordinatorEntity[HipDataUpdateCoordinator], UpdateEntity):
    _attr_has_entity_name = True
    _attr_name = "Repository Update"

    def __init__(self, coordinator: HipDataUpdateCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_update"

    @property
    def installed_version(self) -> str | None:
        return self.coordinator.data.installed_version

    @property
    def latest_version(self) -> str | None:
        return self.coordinator.data.repository_version

    @property
    def release_summary(self) -> str | None:
        return self.coordinator.data.migration_notes

    @property
    def in_progress(self) -> bool:
        return self.coordinator.data.update_status in {"deploying", "rolling_back"}

    @property
    def release_url(self) -> str | None:
        return self.coordinator.data.release_notes_url

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "deployment_target": self.coordinator.data.deployment_target,
            "update_status": self.coordinator.data.update_status,
            "last_deployment": self.coordinator.data.last_deployment,
            "last_deployment_version": self.coordinator.data.last_deployment_version,
            "last_report_path": self.coordinator.data.last_report_path,
        }

