import logging

from zyjj_open_sdk.core import OpenClient, MqttClient, OpenAsyncClient, MqttAsyncClient
from zyjj_open_sdk.task.text import Text, AsyncText
from zyjj_open_sdk.task.image import Image, AsyncImage
from zyjj_open_sdk.task.audio import Audio, AsyncAudio
from zyjj_open_sdk.task.subtitle import Subtitle, AsyncSubtitle
from zyjj_open_sdk.task.tool import Tool, AsyncTool

class Client:
    def __init__(self, sk: str, host: str = 'https://api.zyjj.cc'):
        self.__client = OpenClient(sk, host)
        self.__mqtt = MqttClient(self.__client)
        self.text = Text(self.__client, self.__mqtt)
        self.image = Image(self.__client, self.__mqtt)
        self.audio = Audio(self.__client, self.__mqtt)
        self.subtitle = Subtitle(self.__client, self.__mqtt)
        self.tool = Tool(self.__client, self.__mqtt)

    def __handle_signal(self, signum, frame):
        logging.info(f"handle signal {signum}")
        """处理信号"""
        self.close()

    def close(self):
        """关闭客户端，必须显式调用"""
        self.__mqtt.close()

class AsyncClient:
    def __init__(self, sk: str, host: str = 'https://api.zyjj.cc'):
        self.__client = OpenAsyncClient(sk, host)
        self.__mqtt = MqttAsyncClient(self.__client)
        self.text = AsyncText(self.__client, self.__mqtt)
        self.image = AsyncImage(self.__client, self.__mqtt)
        self.audio = AsyncAudio(self.__client, self.__mqtt)
        self.subtitle = AsyncSubtitle(self.__client, self.__mqtt)
        self.tool = AsyncTool(self.__client, self.__mqtt)

    def close(self):
        """关闭客户端，必须显式调用"""
        self.__mqtt.close()
