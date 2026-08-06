from __future__ import annotations

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_TITLE, DOMAIN
from .options_flow import HipOptionsFlowHandler


class HipConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            return self.async_create_entry(title=DEFAULT_TITLE, data={})
        return self.async_show_form(step_id="user", data_schema=None, description_placeholders={"title": DEFAULT_TITLE})

    @staticmethod
    def async_get_options_flow(config_entry):
        return HipOptionsFlowHandler(config_entry)
