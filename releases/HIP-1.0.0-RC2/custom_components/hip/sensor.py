from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HipDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: HipDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            HipCoordinatorSensor(coordinator, entry.entry_id, "installed_version", "Installed Version"),
            HipCoordinatorSensor(coordinator, entry.entry_id, "kernel_version", "Kernel Version"),
            HipCoordinatorSensor(coordinator, entry.entry_id, "runtime_status", "Runtime Status"),
            HipInstalledModulesSensor(coordinator, entry.entry_id),
        ]
    )


class HipCoordinatorSensor(CoordinatorEntity[HipDataUpdateCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: HipDataUpdateCoordinator, entry_id: str, key: str, name: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{key}"

    @property
    def native_value(self):
        return getattr(self.coordinator.data, self._key)


class HipInstalledModulesSensor(CoordinatorEntity[HipDataUpdateCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Installed Modules"

    def __init__(self, coordinator: HipDataUpdateCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_installed_modules"

    @property
    def native_value(self) -> str:
        return ", ".join(module.title for module in self.coordinator.data.modules.values() if module.installed)

    @property
    def extra_state_attributes(self) -> dict:
        return {key: module.to_dict() for key, module in self.coordinator.data.modules.items()}
