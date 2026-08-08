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
    SERVICE_VISITOR_CREATE,
    SERVICE_VISITOR_DELETE,
    SERVICE_VISITOR_GET,
    SERVICE_VISITOR_LIST,
    SERVICE_VISITOR_UPDATE,
)
from .coordinator import HipDataUpdateCoordinator

ServiceHandler = Callable[[ServiceCall], Awaitable[dict[str, Any]]]

VISITOR_CREATE_SCHEMA = vol.Schema(
    {
        vol.Optional("event_id"): str,
        vol.Optional("type", default="visitor"): str,
        vol.Optional("status", default="new"): str,
        vol.Optional("camera", default="Front Door"): str,
        vol.Optional("timestamp"): str,
        vol.Optional("person"): vol.Any(str, None),
        vol.Optional("snapshot"): vol.Any(str, None),
        vol.Optional("confidence"): vol.Any(vol.Coerce(float), None),
        vol.Optional("notification_sent", default=False): bool,
        vol.Optional("announcement_sent", default=False): bool,
        vol.Optional("timeline_append"): str,
    },
    extra=vol.ALLOW_EXTRA,
)

VISITOR_UPDATE_SCHEMA = vol.Schema(
    {
        vol.Required("event_id"): str,
        vol.Optional("type"): str,
        vol.Optional("status"): str,
        vol.Optional("camera"): str,
        vol.Optional("timestamp"): str,
        vol.Optional("person"): vol.Any(str, None),
        vol.Optional("snapshot"): vol.Any(str, None),
        vol.Optional("confidence"): vol.Any(vol.Coerce(float), None),
        vol.Optional("notification_sent"): bool,
        vol.Optional("announcement_sent"): bool,
        vol.Optional("timeline_append"): str,
    },
    extra=vol.ALLOW_EXTRA,
)

VISITOR_EVENT_ID_SCHEMA = vol.Schema({vol.Required("event_id"): str})
VISITOR_LIST_SCHEMA = vol.Schema(
    {
        vol.Optional("limit"): vol.All(vol.Coerce(int), vol.Range(min=1, max=250)),
        vol.Optional("status"): str,
        vol.Optional("camera"): str,
    }
)


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

    async def _visitor_create(call: ServiceCall) -> dict[str, Any]:
        return await coordinator.visitor_create(dict(call.data))

    async def _visitor_update(call: ServiceCall) -> dict[str, Any]:
        payload = dict(call.data)
        event_id = str(payload.pop("event_id"))
        return await coordinator.visitor_update(event_id, payload)

    async def _visitor_delete(call: ServiceCall) -> dict[str, Any]:
        return await coordinator.visitor_delete(str(call.data["event_id"]))

    async def _visitor_get(call: ServiceCall) -> dict[str, Any]:
        return await coordinator.visitor_get(str(call.data["event_id"]))

    async def _visitor_list(call: ServiceCall) -> dict[str, Any]:
        return await coordinator.visitor_list(
            limit=call.data.get("limit"),
            status=call.data.get("status"),
            camera=call.data.get("camera"),
        )

    await _register(SERVICE_VISITOR_CREATE, _visitor_create, schema=VISITOR_CREATE_SCHEMA)
    await _register(SERVICE_VISITOR_UPDATE, _visitor_update, schema=VISITOR_UPDATE_SCHEMA)
    await _register(SERVICE_VISITOR_DELETE, _visitor_delete, schema=VISITOR_EVENT_ID_SCHEMA)
    await _register(SERVICE_VISITOR_GET, _visitor_get, schema=VISITOR_EVENT_ID_SCHEMA)
    await _register(SERVICE_VISITOR_LIST, _visitor_list, schema=VISITOR_LIST_SCHEMA)


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
        SERVICE_VISITOR_CREATE,
        SERVICE_VISITOR_UPDATE,
        SERVICE_VISITOR_DELETE,
        SERVICE_VISITOR_GET,
        SERVICE_VISITOR_LIST,
    ):
        if hass.services.has_service(DOMAIN, service):
            hass.services.async_remove(DOMAIN, service)
