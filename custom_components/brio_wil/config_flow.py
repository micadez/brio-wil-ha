"""Config flow for CCEI BRiO WiL."""

from __future__ import annotations

import socket
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    BRIO_PORT,
    CONF_MAX_RETRY_INTERVAL,
    CONF_POLL_INTERVAL,
    CONF_RETRY_INTERVAL,
    DEFAULT_MAX_RETRY_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_RETRY_INTERVAL,
    DOMAIN,
)


def _test_connection(host: str) -> bool:
    """Try a TCP connection to the BRiO WiL device."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        result = sock.connect_ex((host, BRIO_PORT))
        sock.close()
        return result == 0
    except OSError:
        return False


class BrioWilConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BRiO WiL."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            can_connect = await self.hass.async_add_executor_job(
                _test_connection, host
            )
            if can_connect:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"BRiO WiL ({host})", data=user_input
                )
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> BrioWilOptionsFlow:
        return BrioWilOptionsFlow(config_entry)


class BrioWilOptionsFlow(OptionsFlow):
    """Handle options for BRiO WiL."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_POLL_INTERVAL,
                        default=options.get(
                            CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=86400)),
                    vol.Optional(
                        CONF_RETRY_INTERVAL,
                        default=options.get(
                            CONF_RETRY_INTERVAL, DEFAULT_RETRY_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
                    vol.Optional(
                        CONF_MAX_RETRY_INTERVAL,
                        default=options.get(
                            CONF_MAX_RETRY_INTERVAL, DEFAULT_MAX_RETRY_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=60, max=86400)),
                }
            ),
        )
