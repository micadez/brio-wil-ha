"""Select platform for CCEI BRiO WiL (speed control)."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SPEED_BY_NAME, SPEED_LEVELS
from .coordinator import BrioWilCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: BrioWilCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BrioWilSpeedSelect(coordinator, entry)])


class BrioWilSpeedSelect(CoordinatorEntity[BrioWilCoordinator], SelectEntity):
    """Select entity for animation speed."""

    _attr_has_entity_name = True
    _attr_name = "Speed"
    _attr_icon = "mdi:speedometer"
    _attr_options = list(SPEED_LEVELS.values())

    def __init__(self, coordinator: BrioWilCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_speed"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
        }

    @property
    def current_option(self) -> str | None:
        if self.coordinator.data is None:
            return None
        return SPEED_LEVELS.get(self.coordinator.data["speed"])

    async def async_select_option(self, option: str) -> None:
        speed = SPEED_BY_NAME.get(option)
        if speed is not None:
            await self.coordinator.async_set_speed(speed)

            if self.coordinator.data is not None:
                self.coordinator.data["speed"] = speed
                self.async_write_ha_state()

            await self.coordinator.async_request_refresh()
