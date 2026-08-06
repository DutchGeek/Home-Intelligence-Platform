from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
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
)


class HipOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_DOCUMENTATION_URL,
                    default=self.config_entry.options.get(CONF_DOCUMENTATION_URL, DEFAULT_DOCUMENTATION_URL),
                ): str,
                vol.Optional(
                    CONF_GITHUB_REPO,
                    default=self.config_entry.options.get(CONF_GITHUB_REPO, DEFAULT_GITHUB_REPO),
                ): str,
                vol.Optional(
                    CONF_DEPLOYMENT_TARGET,
                    default=self.config_entry.options.get(CONF_DEPLOYMENT_TARGET, DEFAULT_DEPLOYMENT_TARGET),
                ): vol.In(["development", "production"]),
                vol.Optional(
                    CONF_CUSTOM_COMPONENTS_PATH,
                    default=self.config_entry.options.get(CONF_CUSTOM_COMPONENTS_PATH, DEFAULT_CUSTOM_COMPONENTS_PATH),
                ): str,
                vol.Optional(
                    CONF_PACKAGES_PATH,
                    default=self.config_entry.options.get(CONF_PACKAGES_PATH, DEFAULT_PACKAGES_PATH),
                ): str,
                vol.Optional(
                    CONF_HIP_PATH,
                    default=self.config_entry.options.get(CONF_HIP_PATH, DEFAULT_HIP_PATH),
                ): str,
                vol.Optional(
                    CONF_DASHBOARD_PATH,
                    default=self.config_entry.options.get(CONF_DASHBOARD_PATH, DEFAULT_DASHBOARD_PATH),
                ): str,
                vol.Optional(
                    CONF_RELEASE_NOTES_PATH,
                    default=self.config_entry.options.get(CONF_RELEASE_NOTES_PATH, DEFAULT_RELEASE_NOTES_PATH),
                ): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
