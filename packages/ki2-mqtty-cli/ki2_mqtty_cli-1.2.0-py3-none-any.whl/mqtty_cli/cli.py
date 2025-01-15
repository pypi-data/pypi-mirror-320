from __future__ import annotations
from typing import TYPE_CHECKING
from typing_extensions import Any
import asyncio
import sys
import os
import json
from datetime import datetime
from pathlib import Path

from aiomqtt import Client as AioMqttClient

from ki2_python_utils import run_parallel
from mqtty import serial_device_factory, manager_setup, connect_aio_mqtt, MqttyDevice

from .config import load_config, convert_parity
from .sync_to_async import ask_publish_sync, handle_queue

if TYPE_CHECKING:
    pass


def get_path():
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    env_conf = os.getenv("MQTTY_CONFIG")
    if env_conf is not None:
        return Path(env_conf)
    return Path("settings.toml")


async def _main():
    path = get_path()
    print(f"Path = {path}")
    config = load_config(path)

    if len(config.devices) == 0:
        print("No devices configured")
        return

    mqtt_config: dict[str, Any] = {
        "hostname": config.mqtt.host,
        "port": config.mqtt.port,
    }

    if config.mqtt.auth is not None:
        mqtt_config["username"] = config.mqtt.auth.username
        mqtt_config["password"] = config.mqtt.auth.password

    if config.mqtt.startup_wait_time > 0:
        await asyncio.sleep(config.mqtt.startup_wait_time)

    mqtt_client = AioMqttClient(**mqtt_config)

    if (
        isinstance(config.mqtt.pending_calls_threshold, int)
        and config.mqtt.pending_calls_threshold > 0
    ):
        mqtt_client.pending_calls_threshold = config.mqtt.pending_calls_threshold

    def on_serial_error(device: MqttyDevice, error: Exception):
        print(f"Error occured on device {device.name}: {error}")
        if config.mqtt.notification_topic is not None:
            topic: str = config.mqtt.notification_topic
            payload = {
                "type": "serial-exception",
                "device": device.name,
                "message": str(error),
                "timestamp": datetime.now().isoformat(),
            }

            ask_publish_sync(topic, json.dumps(payload))

    manager = manager_setup("async")
    manager.on_serial_error = on_serial_error

    for device in config.devices:
        topic = device.topic
        optional = device.optional
        serial_config = device.model_dump(exclude={"topic", "optional"})
        if optional:
            if not os.path.exists(device.port):
                print(f"Optional device '{device.port}' not found - skipping")
                continue
        if serial_config["baudrate"] is None:
            serial_config["baudrate"] = config.default.baudrate
        serial_config["parity"] = convert_parity(serial_config["parity"])
        serial_device = serial_device_factory(**serial_config)
        manager.register(topic, serial_device)
        print(f"New device '{device.port}' on topic '{topic}'")

    mqtt_loop = connect_aio_mqtt(mqtt_client, manager=manager)

    async def _handle_queue():
        await handle_queue(mqtt_client)

    await run_parallel(manager.loop, mqtt_loop, _handle_queue)


def main():
    asyncio.run(_main())
