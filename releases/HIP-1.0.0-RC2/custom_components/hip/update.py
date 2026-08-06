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
        return False
