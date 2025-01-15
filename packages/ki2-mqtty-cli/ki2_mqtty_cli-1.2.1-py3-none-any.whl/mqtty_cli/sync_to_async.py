from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict
import asyncio

from aiomqtt import Client as AioMqttClient

if TYPE_CHECKING:
    pass


class QueueItem(TypedDict):
    topic: str
    payload: str


serial_error_queue: asyncio.Queue[QueueItem] = asyncio.Queue()

mqtt_connexion_status: bool = False


def ask_publish_sync(topic: str, payload: str) -> None:
    global serial_error_queue
    serial_error_queue.put_nowait({"topic": topic, "payload": payload})


async def handle_queue(client: AioMqttClient):
    global mqtt_connexion_status
    while not mqtt_connexion_status:
        await asyncio.sleep(0.1)
    while True:
        item = await serial_error_queue.get()
        topic = item["topic"]
        payload = item["payload"]
        await client.publish(topic, payload)


def change_mqtt_connexion_status(status: bool):
    global mqtt_connexion_status
    mqtt_connexion_status = status
