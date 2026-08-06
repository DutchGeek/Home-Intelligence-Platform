from __future__ import annotations

from typing import Any, Awaitable, Callable

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse

from .const import (
    DOMAIN,
    SERVICE_CHECK_UPDATES,
    SERVICE_DEPLOYMENT_STATUS,
    SERVICE_EVENT_STATISTICS,
    SERVICE_EXPORT_SUPPORT_BUNDLE,
    SERVICE_HEALTH_CHECK,
    SERVICE_KERNEL_STATUS,
    SERVICE_MODULE_STATUS,
    SERVICE_OPEN_RELEASE_NOTES,
    SERVICE_RELOAD,
    SERVICE_RUN_SMOKE_TESTS,
    SERVICE_VALIDATE,
    SERVICE_VERSION,
)
from .coordinator import HipDataUpdateCoordinator

ServiceHandler = Callable[[ServiceCall], Awaitable[dict[str, Any]]]


async def async_setup_services(hass: HomeAssistant, coordinator: HipDataUpdateCoordinator) -> None:
    async def _register(service: str, handler: ServiceHandler, schema: vol.Schema | None = None) -> None:
        async def _wrapped(call: ServiceCall) -> dict[str, Any]:
            return await handler(call)

        hass.services.async_register(
            DOMAIN,
            service,
            _wrapped,
            schema=schema or vol.Schema({}),
            supports_response=SupportsResponse.ONLY,
        )

    await _register(SERVICE_VALIDATE, lambda _: coordinator.validate())
    await _register(SERVICE_RELOAD, lambda _: coordinator.reload())
    await _register(SERVICE_HEALTH_CHECK, lambda _: coordinator.health_check())
    await _register(SERVICE_EXPORT_SUPPORT_BUNDLE, lambda _: coordinator.export_support_bundle())
    await _register(SERVICE_RUN_SMOKE_TESTS, lambda _: coordinator.run_smoke_tests())
    await _register(SERVICE_VERSION, lambda _: coordinator.version_info())
    await _register(SERVICE_KERNEL_STATUS, lambda _: coordinator.kernel_status())
    await _register(SERVICE_MODULE_STATUS, lambda _: coordinator.module_status())
    await _register(SERVICE_EVENT_STATISTICS, lambda _: coordinator.event_statistics())
    await _register(SERVICE_CHECK_UPDATES, lambda _: coordinator.check_updates())
    await _register(SERVICE_OPEN_RELEASE_NOTES, lambda _: coordinator.open_release_notes())
    await _register(SERVICE_DEPLOYMENT_STATUS, lambda _: coordinator.deployment_status())


async def async_unload_services(hass: HomeAssistant) -> None:
    for service in (
        SERVICE_VALIDATE,
        SERVICE_RELOAD,
        SERVICE_HEALTH_CHECK,
        SERVICE_EXPORT_SUPPORT_BUNDLE,
        SERVICE_RUN_SMOKE_TESTS,
        SERVICE_VERSION,
        SERVICE_KERNEL_STATUS,
        SERVICE_MODULE_STATUS,
        SERVICE_EVENT_STATISTICS,
        SERVICE_CHECK_UPDATES,
        SERVICE_OPEN_RELEASE_NOTES,
        SERVICE_DEPLOYMENT_STATUS,
    ):
        if hass.services.has_service(DOMAIN, service):
            hass.services.async_remove(DOMAIN, service)
