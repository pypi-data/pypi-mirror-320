from __future__ import annotations

from contextlib import asynccontextmanager
from enum import Enum
from typing import AsyncIterator

from aiohttp import ClientSession, ClientWebSocketResponse, TCPConnector, ClientWSTimeout
from pydantic import BaseModel


class WebsocketClient:
    def __init__(self, hostname, access_token):
        self.base_url = f"https://{hostname}:12445/api/v1/developer/"
        self.headers = {"Authorization": f"Bearer {access_token}"}

    @asynccontextmanager
    async def _connection(self, url) -> AsyncIterator[ClientWebSocketResponse]:
        async with ClientSession(
                base_url=self.base_url,
                headers=self.headers
        ) as session, session.ws_connect(
            url,
            verify_ssl=False,
            # UniFi doesn't properly close server side, so this is needed to avoid infinite loop
            timeout=ClientWSTimeout(ws_close=0)
        ) as socket:
            yield socket

    @asynccontextmanager
    async def device_notifications(self) -> AsyncIterator[AsyncIterator[Notification]]:
        async with self._connection("devices/notifications") as socket:
            async def wrapper():
                async for message in socket:
                    json = message.json()
                    if type(json) is dict:
                        yield Notification.model_validate(json)

            yield wrapper()


class Notification(BaseModel):
    event: NotificationEvent


class NotificationEvent(str, Enum):
    DeviceUpdateV2 = "access.data.v2.device.update"
    Missing = ""

    @classmethod
    def _missing_(cls, value: str) -> NotificationEvent:
        return NotificationEvent.Missing
