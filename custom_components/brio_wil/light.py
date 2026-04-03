"""Light platform for CCEI BRiO WiL."""

from __future__ import annotations

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODES, MODE_BY_NAME
from .coordinator import BrioWilCoordinator

# Map between the device's 4 brightness levels and HA's 1-255 scale.
WIL_TO_HA_BRIGHTNESS = {0: 64, 1: 128, 2: 192, 3: 255}
_HA_BRIGHTNESS_THRESHOLDS = [(96, 0), (160, 1), (224, 2), (255, 3)]

REFRESH_DELAY = 1.5


def _ha_brightness_to_wil(value: int) -> int:
    for threshold, level in _HA_BRIGHTNESS_THRESHOLDS:
        if value <= threshold:
            return level
    return 3


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: BrioWilCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BrioWilLight(coordinator, entry)])


class BrioWilLight(CoordinatorEntity[BrioWilCoordinator], LightEntity):
    """Representation of a BRiO WiL pool light."""

    _attr_has_entity_name = True
    _attr_name = "Pool Light"
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = list(MODES.values())

    def __init__(self, coordinator: BrioWilCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_light"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "CCEI BRiO WiL",
            "manufacturer": "CCEI",
            "model": "BRiO WiL",
        }

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data["is_on"]

    @property
    def brightness(self) -> int | None:
        if self.coordinator.data is None:
            return None
        return WIL_TO_HA_BRIGHTNESS.get(self.coordinator.data["brightness"], 255)

    @property
    def effect(self) -> str | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data["mode_name"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_power(True)

        wil_brightness = None
        if ATTR_BRIGHTNESS in kwargs:
            wil_brightness = _ha_brightness_to_wil(int(kwargs[ATTR_BRIGHTNESS]))
            await self.coordinator.async_set_brightness(wil_brightness)

        mode_name = None
        if ATTR_EFFECT in kwargs:
            mode_name = kwargs[ATTR_EFFECT]
            mode_id = MODE_BY_NAME.get(mode_name)
            if mode_id is not None:
                await self.coordinator.async_set_mode(mode_id)

        # Optimistic update — reflect expected state immediately in UI
        if self.coordinator.data is not None:
            self.coordinator.data["is_on"] = True
            if wil_brightness is not None:
                self.coordinator.data["brightness"] = wil_brightness
            if mode_name is not None:
                self.coordinator.data["mode_name"] = mode_name
            self.async_write_ha_state()

        # Deferred refresh to verify actual device state
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_power(False)

        if self.coordinator.data is not None:
            self.coordinator.data["is_on"] = False
            self.async_write_ha_state()

        await self.coordinator.async_request_refresh()
