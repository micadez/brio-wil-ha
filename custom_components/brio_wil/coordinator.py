"""DataUpdateCoordinator for CCEI BRiO WiL."""

from __future__ import annotations

import json
import logging
import socket
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    BRIO_PORT,
    DOMAIN,
    MODES,
    POS_BRIGHTNESS,
    POS_MODE,
    POS_SPEED,
    POS_STATE,
    SPEED_OFFSET,
)

_LOGGER = logging.getLogger(__name__)


class BrioWilCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls the BRiO WiL device over TCP with exponential backoff on failure."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        poll_interval: int,
        retry_interval: int,
        max_retry_interval: int,
    ) -> None:
        self.host = host
        self.poll_interval = poll_interval
        self.retry_interval = retry_interval
        self.max_retry_interval = max_retry_interval
        self._current_backoff = retry_interval
        self._consecutive_failures = 0

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_interval),
        )

    # ── TCP transport ───────────────────────────────────────────────

    def _tcp(self, data: str) -> str | None:
        """Send data over TCP and return the response (blocking)."""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((self.host, BRIO_PORT))
            sock.sendall(data.encode("utf-8"))
            resp = sock.recv(512)
            return resp.decode("ascii", errors="replace")
        except (OSError, socket.timeout):
            return None
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:  # noqa: BLE001
                    pass

    def _get_status(self) -> dict[str, Any] | None:
        """Query the device for its current state."""
        raw = self._tcp("")
        if raw is None or len(raw) < 72:
            return None
        try:
            state_val = int(raw[POS_STATE[0] : POS_STATE[1]])
            mode_val = int(raw[POS_MODE[0] : POS_MODE[1]], 16)
            speed_val = int(raw[POS_SPEED], 16) - SPEED_OFFSET
            bright_val = int(raw[POS_BRIGHTNESS], 16) // 4
            return {
                "is_on": state_val != 0,
                "mode": mode_val,
                "mode_name": MODES.get(mode_val, f"Unknown ({mode_val})"),
                "brightness": max(0, min(3, bright_val)),
                "speed": max(0, min(2, speed_val)),
            }
        except (ValueError, IndexError):
            return None

    def _send_cmd(self, cmd: dict) -> bool:
        return self._tcp(json.dumps(cmd, separators=(",", ":"))) is not None

    # ── Async command helpers (called from entities) ────────────────

    async def async_set_power(self, on: bool) -> bool:
        """Turn the light on or off."""

        def _do() -> bool:
            status = self._get_status()
            if status is None:
                return False
            if status["is_on"] == on:
                return True
            return self._send_cmd({"sprj": 1 if on else 0})

        return await self.hass.async_add_executor_job(_do)

    async def async_set_mode(self, mode_id: int) -> bool:
        return await self.hass.async_add_executor_job(
            self._send_cmd, {"prcn": mode_id}
        )

    async def async_set_brightness(self, level: int) -> bool:
        return await self.hass.async_add_executor_job(
            self._send_cmd, {"plum": max(0, min(3, level))}
        )

    async def async_set_speed(self, speed: int) -> bool:
        return await self.hass.async_add_executor_job(
            self._send_cmd, {"pspd": max(0, min(2, speed))}
        )

    # ── Coordinator update ──────────────────────────────────────────

    async def _async_update_data(self) -> dict[str, Any]:
        status = await self.hass.async_add_executor_job(self._get_status)
        if status is None:
            self._consecutive_failures += 1
            self.update_interval = timedelta(seconds=self._current_backoff)
            self._current_backoff = min(
                self._current_backoff * 2, self.max_retry_interval
            )
            raise UpdateFailed(
                f"Failed to reach BRiO WiL at {self.host} "
                f"(attempt #{self._consecutive_failures}, "
                f"next retry in {self.update_interval.total_seconds():.0f}s)"
            )

        if self._consecutive_failures > 0:
            _LOGGER.info(
                "BRiO WiL back online after %d failures",
                self._consecutive_failures,
            )
        self._consecutive_failures = 0
        self._current_backoff = self.retry_interval
        self.update_interval = timedelta(seconds=self.poll_interval)
        return status
