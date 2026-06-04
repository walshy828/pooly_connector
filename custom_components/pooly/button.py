"""Button platform for Pooly — mark complete and dismiss maintenance tasks."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import PoolyApiError
from .const import DOMAIN
from .coordinator import PoolyCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PoolyCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[ButtonEntity] = []
    for task_type, task_data in coordinator.data["maintenance"].items():
        display_name = task_data.get("display_name", task_type.replace("_", " ").title())
        entities.append(PoolyCompleteButton(coordinator, entry, task_type, display_name))
        entities.append(PoolyDismissButton(coordinator, entry, task_type, display_name))

    async_add_entities(entities)


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer="Pooly",
        model="Pool Manager",
    )


class PoolyTaskButton(CoordinatorEntity[PoolyCoordinator], ButtonEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PoolyCoordinator,
        entry: ConfigEntry,
        task_type: str,
        display_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._task_type = task_type
        self._display_name = display_name
        self._attr_device_info = _device_info(entry)


class PoolyCompleteButton(PoolyTaskButton):
    _attr_icon = "mdi:check-circle-outline"

    def __init__(self, coordinator, entry, task_type, display_name) -> None:
        super().__init__(coordinator, entry, task_type, display_name)
        self._attr_unique_id = f"{entry.entry_id}_complete_{task_type}"
        self._attr_name = f"{display_name} — Mark Complete"

    async def async_press(self) -> None:
        try:
            await self.coordinator.client.complete_task(self._task_type)
        except PoolyApiError as err:
            _LOGGER.error("Failed to complete task %s: %s", self._task_type, err)
            return
        await self.coordinator.async_request_refresh()


class PoolyDismissButton(PoolyTaskButton):
    _attr_icon = "mdi:bell-off-outline"

    def __init__(self, coordinator, entry, task_type, display_name) -> None:
        super().__init__(coordinator, entry, task_type, display_name)
        self._attr_unique_id = f"{entry.entry_id}_dismiss_{task_type}"
        self._attr_name = f"{display_name} — Dismiss"

    async def async_press(self) -> None:
        try:
            await self.coordinator.client.dismiss_task(self._task_type)
        except PoolyApiError as err:
            _LOGGER.error("Failed to dismiss task %s: %s", self._task_type, err)
            return
        await self.coordinator.async_request_refresh()
