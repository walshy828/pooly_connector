"""Async HTTP client for the Pooly backend."""
from __future__ import annotations

import aiohttp

from .const import (
    API_COMPLETE_TASK,
    API_DISMISS_TASK,
    API_MAINTENANCE,
    API_MAINTENANCE_TASK,
    API_SENSOR_PUSH,
    API_STATUS,
)


class PoolyApiError(Exception):
    pass


class PoolyApiClient:
    def __init__(self, host: str, port: int, session: aiohttp.ClientSession) -> None:
        self._base = f"http://{host}:{port}"
        self._session = session

    def _url(self, path: str) -> str:
        return f"{self._base}{path}"

    async def _get(self, path: str) -> dict | list:
        try:
            async with self._session.get(self._url(path), timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    raise PoolyApiError(f"GET {path} returned {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise PoolyApiError(f"Connection error: {err}") from err

    async def _post(self, path: str, payload: dict | None = None) -> dict:
        try:
            async with self._session.post(
                self._url(path),
                json=payload or {},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status not in (200, 201):
                    raise PoolyApiError(f"POST {path} returned {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise PoolyApiError(f"Connection error: {err}") from err

    async def get_status(self) -> dict:
        return await self._get(API_STATUS)

    async def get_maintenance(self) -> list:
        return await self._get(API_MAINTENANCE)

    async def get_maintenance_task(self, task_type: str) -> dict:
        path = API_MAINTENANCE_TASK.format(task_type=task_type)
        return await self._get(path)

    async def complete_task(self, task_type: str, notes: str | None = None) -> dict:
        path = API_COMPLETE_TASK.format(task_type=task_type)
        payload = {"notes": notes} if notes else {}
        return await self._post(path, payload)

    async def dismiss_task(self, task_type: str) -> dict:
        path = API_DISMISS_TASK.format(task_type=task_type)
        return await self._post(path)

    async def push_sensor(self, sensor_type: str, value: float, unit: str | None = None, entity_id: str | None = None) -> dict:
        payload: dict = {"sensor_type": sensor_type, "value": value}
        if unit:
            payload["unit"] = unit
        if entity_id:
            payload["entity_id"] = entity_id
        return await self._post(API_SENSOR_PUSH, payload)
