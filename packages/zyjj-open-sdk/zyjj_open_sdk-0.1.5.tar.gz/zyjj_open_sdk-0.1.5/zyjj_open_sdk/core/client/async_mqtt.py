from zyjj_open_sdk.core.client.async_client import OpenAsyncClient
from zyjj_open_sdk.core.client.base import BaseMqttClient, Callback

class MqttAsyncClient(BaseMqttClient):
    def __init__(self, client: OpenAsyncClient):
        super().__init__()
        self.__client = client

    async def start(self):
        if not self.is_connect:
            super()._start(await self.__client.get_mqtt_task())

    def add_listener(self, task_id: str, callback: Callback):
        super().add_listener(task_id, callback)

    def close(self):
        super().close()
