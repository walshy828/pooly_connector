"""DataUpdateCoordinator for Pooly."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PoolyApiClient, PoolyApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class PoolyCoordinator(DataUpdateCoordinator):
    """Polls /api/ha/status and /api/ha/maintenance every scan interval."""

    def __init__(self, hass: HomeAssistant, client: PoolyApiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        try:
            status = await self.client.get_status()
            maintenance = await self.client.get_maintenance()
        except PoolyApiError as err:
            raise UpdateFailed(f"Error communicating with Pooly: {err}") from err

        maintenance_by_task = {task["task_type"]: task for task in maintenance}

        return {
            "status": status,
            "maintenance": maintenance_by_task,
        }
