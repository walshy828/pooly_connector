"""Sensor platform for Pooly."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MAINTENANCE_STATES, STATE_ICONS
from .coordinator import PoolyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PoolyCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        PoolyHealthScoreSensor(coordinator, entry),
        PoolyTemperatureSensor(coordinator, entry),
        PoolyUrgentCountSensor(coordinator, entry),
    ]

    for task_type, task_data in coordinator.data["maintenance"].items():
        entities.append(PoolyMaintenanceSensor(coordinator, entry, task_type, task_data))

    async_add_entities(entities)


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


class PoolyHealthScoreSensor(PoolyCoordinatorEntity, SensorEntity):
    _attr_name = "Health Score"
    _attr_icon = "mdi:pool"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = None

    def __init__(self, coordinator: PoolyCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_health_score"

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data["status"].get("health_score")

    @property
    def extra_state_attributes(self) -> dict:
        status = self.coordinator.data["status"]
        return {
            "health_label": status.get("health_label"),
            "pool_name": status.get("pool_name"),
            "last_updated": status.get("last_updated"),
        }


class PoolyTemperatureSensor(PoolyCoordinatorEntity, SensorEntity):
    _attr_name = "Pool Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT

    def __init__(self, coordinator: PoolyCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_pool_temp"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data["status"].get("pool_temp_f")


class PoolyUrgentCountSensor(PoolyCoordinatorEntity, SensorEntity):
    _attr_name = "Urgent Maintenance Count"
    _attr_icon = "mdi:alert-circle"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: PoolyCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_urgent_count"

    @property
    def native_value(self) -> int:
        summary = self.coordinator.data["status"].get("maintenance_summary", {})
        return summary.get("urgent_count", 0)

    @property
    def extra_state_attributes(self) -> dict:
        summary = self.coordinator.data["status"].get("maintenance_summary", {})
        return {
            "overdue_count": summary.get("overdue_count", 0),
            "due_soon_count": summary.get("due_soon_count", 0),
            "good_count": summary.get("good_count", 0),
            "total_enabled": summary.get("total_enabled", 0),
        }


class PoolyMaintenanceSensor(PoolyCoordinatorEntity, SensorEntity):
    _attr_device_class = None

    def __init__(
        self,
        coordinator: PoolyCoordinator,
        entry: ConfigEntry,
        task_type: str,
        task_data: dict,
    ) -> None:
        super().__init__(coordinator, entry)
        self._task_type = task_type
        self._attr_unique_id = f"{entry.entry_id}_maintenance_{task_type}"
        self._attr_name = task_data.get("display_name", task_type.replace("_", " ").title())

    @property
    def _task(self) -> dict:
        return self.coordinator.data["maintenance"].get(self._task_type, {})

    @property
    def native_value(self) -> str | None:
        return self._task.get("state")

    @property
    def icon(self) -> str:
        state = self._task.get("state", "good")
        return STATE_ICONS.get(state, "mdi:check-circle")

    @property
    def extra_state_attributes(self) -> dict:
        task = self._task
        return {
            "priority": task.get("priority"),
            "interval_days": task.get("interval_days"),
            "last_completed": task.get("last_completed"),
            "next_due": task.get("next_due"),
            "days_since": task.get("days_since"),
            "days_until_due": task.get("days_until_due"),
            "recommendation": task.get("recommendation"),
            "enabled": task.get("enabled"),
        }
