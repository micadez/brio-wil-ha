"""CCEI BRiO WiL pool light integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_MAX_RETRY_INTERVAL,
    CONF_POLL_INTERVAL,
    CONF_RETRY_INTERVAL,
    DEFAULT_MAX_RETRY_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_RETRY_INTERVAL,
    DOMAIN,
)
from .coordinator import BrioWilCoordinator

PLATFORMS = [Platform.LIGHT, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BRiO WiL from a config entry."""
    host = entry.data[CONF_HOST]
    poll = entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
    retry = entry.options.get(CONF_RETRY_INTERVAL, DEFAULT_RETRY_INTERVAL)
    max_retry = entry.options.get(CONF_MAX_RETRY_INTERVAL, DEFAULT_MAX_RETRY_INTERVAL)

    coordinator = BrioWilCoordinator(hass, host, poll, retry, max_retry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload integration when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
