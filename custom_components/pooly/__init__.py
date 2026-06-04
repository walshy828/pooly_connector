"""Pooly Home Assistant Integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .api import PoolyApiClient, PoolyApiError
from .const import DOMAIN
from .coordinator import PoolyCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON]

SERVICE_PUSH_SENSOR = "push_sensor"
SERVICE_PUSH_SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required("sensor_type"): vol.In(["pool_temp", "pump_state", "pump_energy"]),
        vol.Required("value"): vol.Coerce(float),
        vol.Optional("unit"): cv.string,
        vol.Optional("entity_id"): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    client = PoolyApiClient(entry.data[CONF_HOST], entry.data[CONF_PORT], session)

    coordinator = PoolyCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_push_sensor(call: ServiceCall) -> None:
        for coordinator in hass.data[DOMAIN].values():
            try:
                await coordinator.client.push_sensor(
                    sensor_type=call.data["sensor_type"],
                    value=call.data["value"],
                    unit=call.data.get("unit"),
                    entity_id=call.data.get("entity_id"),
                )
            except PoolyApiError as err:
                _LOGGER.error("push_sensor failed: %s", err)

    if not hass.services.has_service(DOMAIN, SERVICE_PUSH_SENSOR):
        hass.services.async_register(
            DOMAIN,
            SERVICE_PUSH_SENSOR,
            handle_push_sensor,
            schema=SERVICE_PUSH_SENSOR_SCHEMA,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_PUSH_SENSOR)
    return unloaded
