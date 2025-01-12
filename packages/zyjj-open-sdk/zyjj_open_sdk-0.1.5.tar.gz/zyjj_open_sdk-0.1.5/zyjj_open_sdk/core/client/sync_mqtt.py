from zyjj_open_sdk.core.client import OpenClient
from zyjj_open_sdk.core.client.base import BaseMqttClient, Callback

class MqttClient(BaseMqttClient):
    def __init__(self, client: OpenClient):
        super().__init__()
        self.__client = client

    def start(self):
        if not self.is_connect:
            super()._start(self.__client.get_mqtt_task())

    def add_listener(self, task_id: str, callback: Callback):
        super().add_listener(task_id, callback)

    def close(self):
        super().close()
