from __future__ import annotations

from typing import Any, Awaitable, Callable

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse

from .const import (
    DOMAIN,
    SERVICE_EVENT_STATISTICS,
    SERVICE_EXPORT_SUPPORT_BUNDLE,
    SERVICE_HEALTH_CHECK,
    SERVICE_KERNEL_STATUS,
    SERVICE_MODULE_STATUS,
    SERVICE_RELOAD,
    SERVICE_RUN_SMOKE_TESTS,
    SERVICE_VALIDATE,
    SERVICE_VERSION,
)
from .coordinator import HipDataUpdateCoordinator

ServiceHandler = Callable[[], Awaitable[dict[str, Any]]]


async def async_setup_services(hass: HomeAssistant, coordinator: HipDataUpdateCoordinator) -> None:
    async def _register(service: str, handler: ServiceHandler) -> None:
        async def _wrapped(call: ServiceCall) -> dict[str, Any]:
            del call
            return await handler()

        hass.services.async_register(
            DOMAIN,
            service,
            _wrapped,
            schema=vol.Schema({}),
            supports_response=SupportsResponse.ONLY,
        )

    await _register(SERVICE_VALIDATE, coordinator.validate)
    await _register(SERVICE_RELOAD, coordinator.reload)
    await _register(SERVICE_HEALTH_CHECK, coordinator.health_check)
    await _register(SERVICE_EXPORT_SUPPORT_BUNDLE, coordinator.export_support_bundle)
    await _register(SERVICE_RUN_SMOKE_TESTS, coordinator.run_smoke_tests)
    await _register(SERVICE_VERSION, coordinator.version_info)
    await _register(SERVICE_KERNEL_STATUS, coordinator.kernel_status)
    await _register(SERVICE_MODULE_STATUS, coordinator.module_status)
    await _register(SERVICE_EVENT_STATISTICS, coordinator.event_statistics)


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
    ):
        if hass.services.has_service(DOMAIN, service):
            hass.services.async_remove(DOMAIN, service)
