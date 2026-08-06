from __future__ import annotations

from collections.abc import Awaitable, Callable

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HipDataUpdateCoordinator

Action = Callable[[], Awaitable[dict]]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: HipDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            HipActionButton(coordinator, entry.entry_id, "validate_installation", "Validate Installation", coordinator.validate),
            HipActionButton(coordinator, entry.entry_id, "reload_hip", "Reload HIP", coordinator.reload),
            HipActionButton(coordinator, entry.entry_id, "run_smoke_tests", "Run Smoke Tests", coordinator.run_smoke_tests),
            HipActionButton(coordinator, entry.entry_id, "export_support_bundle", "Export Support Bundle", coordinator.export_support_bundle),
            HipDocumentationButton(coordinator, entry.entry_id),
        ]
    )


class HipActionButton(CoordinatorEntity[HipDataUpdateCoordinator], ButtonEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: HipDataUpdateCoordinator, entry_id: str, key: str, name: str, action: Action) -> None:
        super().__init__(coordinator)
        self._action = action
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{key}"

    async def async_press(self) -> None:
        await self._action()


class HipDocumentationButton(CoordinatorEntity[HipDataUpdateCoordinator], ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Open Documentation"

    def __init__(self, coordinator: HipDataUpdateCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_open_documentation"

    async def async_press(self) -> None:
        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "HIP Documentation",
                "message": self.coordinator.documentation_url,
            },
            blocking=True,
        )
