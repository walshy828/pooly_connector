"""Binary sensor platform for Pooly."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PoolyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PoolyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        PoolyPoolStatusSensor(coordinator, entry),
        PoolyPumpStateSensor(coordinator, entry),
    ])


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer="Pooly",
        model="Pool Manager",
    )


class PoolyCoordinatorEntity(CoordinatorEntity[PoolyCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: PoolyCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = _device_info(entry)


class PoolyPoolStatusSensor(PoolyCoordinatorEntity, BinarySensorEntity):
    _attr_name = "Pool Open"
    _attr_device_class = BinarySensorDeviceClass.OPENING
    _attr_icon = "mdi:pool"

    def __init__(self, coordinator: PoolyCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_pool_status"

    @property
    def is_on(self) -> bool:
        return self.coordinator.data["status"].get("pool_status") == "open"

    @property
    def extra_state_attributes(self) -> dict:
        status = self.coordinator.data["status"]
        return {
            "pool_opened_at": status.get("pool_opened_at"),
            "pool_closed_at": status.get("pool_closed_at"),
        }


class PoolyPumpStateSensor(PoolyCoordinatorEntity, BinarySensorEntity):
    _attr_name = "Pump Running"
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_icon = "mdi:pump"

    def __init__(self, coordinator: PoolyCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_pump_state"

    @property
    def is_on(self) -> bool | None:
        state = self.coordinator.data["status"].get("pump_state")
        if state is None:
            return None
        return state == "on"
