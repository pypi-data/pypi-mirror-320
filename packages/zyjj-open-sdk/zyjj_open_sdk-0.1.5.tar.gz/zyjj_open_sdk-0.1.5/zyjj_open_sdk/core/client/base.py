import json
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Literal, Any, Callable, Type

from httpx import Response
import paho.mqtt.client as mqtt

from zyjj_open_sdk.core.entity.type import data_class_init
from zyjj_open_sdk.core.exception import ServerError, RequestError


@dataclass
class Request:
    method: Literal['get', 'post', 'put']
    url: str
    data: dict = None


@dataclass
class MqttResponse:
    task_id: str
    event_type: int  # 1 开始 2 执行中 3 成功 4 失败 5 详情追加 6 详情设置
    data: Any
    code: int


Callback = Callable[[Type[MqttResponse]], None]


class BaseClient(ABC):
    version = "0.1.0"

    def __init__(self, sk: str, host: str):
        self.__sk = sk
        self.__host = host
        self.timeout = 60

    def get_base_url(self) -> str:
        """获取基础url"""
        return f"{self.__host}/api/v1/"

    def get_header(self) -> dict:
        """获取请求header"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.__sk}"
        }

    @staticmethod
    def res_parse(res: Response) -> Any:
        if res.status_code != 200:
            raise RequestError(res.status_code, res.content)
        data = res.json()
        code = data.get('code', -1)
        if code != 0:
            raise ServerError(code, data.get('message', ''))
        return data.get('data', None)

    def _report_event(self) -> Request:
        return Request('get', f'common/app/info?os=sdk-python&version={self.version}')

    @staticmethod
    def _get_point() -> Request:
        return Request('get', 'open/account/point')

    @staticmethod
    def _execute(task_type: int, _input: dict) -> Request:
        return Request('post', 'open/task/sync', {
            "task_type": task_type,
            "input": _input
        })

    @staticmethod
    def _execute_async(task_type: int, _input: dict) -> Request:
        return Request('post', 'open/task', {
            "task_type": task_type,
            "input": _input
        })

    @staticmethod
    def _get_task_status(task_id: str) -> Request:
        return Request('get', f'open/task/{task_id}')

    @staticmethod
    def _get_file_token(file_name: str, file_size: int, source: int = 1) -> Request:
        return Request('post', 'open/file', {
            "file_name": file_name,
            "file_size": file_size,
            "source": source

        })

    @staticmethod
    def _file_multipart_init(file_name: str, file_size: int, source: int) -> Request:
        return Request('post', 'open/file/multipart/init', {
            "file_name": file_name,
            "file_size": file_size,
            "source": source
        })

    @staticmethod
    def _file_multipart_part(upload_id: str, part_num: int) -> Request:
        return Request('post', 'open/file/multipart/part', {
            "upload_id": upload_id,
            "part_num": part_num
        })

    @staticmethod
    def _file_multipart_complete(upload_id: str, part_list: list) -> Request:
        return Request('post', f'open/file/multipart/complete', {
            "upload_id": upload_id,
            "part_list": part_list
        })

    @staticmethod
    def _get_mqtt_task() -> Request:
        return Request('get', f'open/mqtt/task')

    @abstractmethod
    def get_point(self) -> int:
        """
        获取当前账户剩余积分
        :return:
        """
        pass

    @abstractmethod
    def execute(self, task_type: int, _input: dict) -> dict:
        """
        同步执行执行任务
        :param task_type: 任务类型
        :param _input: 任务输入
        :return: 任务执行结果
        """
        pass

    @abstractmethod
    def execute_async(self, task_type: int, _input: dict) -> str:
        """
        异步执行任务
        :param task_type: 任务类型
        :param _input: 任务输入
        :return 任务id
        """
        pass

    @abstractmethod
    def get_task_status(self, task_id: str) -> dict:
        """
        获取任务状态
        :param task_id: 任务id
        :return: 任务状态
        """

    @abstractmethod
    def get_file_token(self, file_name: str, file_size: int, source: int = 1) -> dict:
        """
        获取文件上传token
        :param file_name: 文件名称
        :param file_size: 文件大小
        :param source: 文件来源
        :return:
        """

    @abstractmethod
    def file_multipart_init(self, file_name: str, file_size: int, source: int = 1) -> dict:
        """
        初始化分片上传
        :param file_name: 文件名称
        :param file_size: 文件大小
        :param source: 文件来源
        :return:
        """

    @abstractmethod
    def file_multipart_part(self, upload_id: str, part_num: int) -> dict:
        """
        开始分片上传
        :param upload_id: 上传id
        :param part_num: 第几个分片
        :return:
        """

    @abstractmethod
    def file_multipart_complete(self, upload_id: str, part_list: list) -> dict:
        """
        完成分片上传
        :param upload_id: 上传id
        :param part_list: 分片列表
        :return:
        """

    @abstractmethod
    def get_mqtt_task(self) -> dict:
        """
        获取mqtt task客户端链接
        :return:
        """


class BaseMqttClient(ABC):
    def __init__(self):
        # 链接是否成功
        self.is_connect = False
        self.__client: mqtt.Client | None = None
        # 监听列表
        self.__listen_map: dict[str, Callback] = {}
        logging.info(f'[mqtt] connect start')

    def __on_connect(self, code: int):
        if code != 0:
            logging.info(f'[mqtt] connect error {code}')
            return
        self.is_connect = True
        logging.info(f'[mqtt] connect success')
        # 启动后自动订阅topic
        self.__client.subscribe(self.__mqtt_data["topic"], qos=2)

    def _start(self, data):
        # 初始化mqtt信息
        self.__mqtt_data = data
        logging.info(f"start connect info {self.__mqtt_data}")
        self.__client = mqtt.Client(client_id=self.__mqtt_data["client_id"], protocol=mqtt.MQTTv311)
        self.__client.username_pw_set(self.__mqtt_data["username"], self.__mqtt_data["password"])
        self.__client.on_connect = lambda client, userdata, flags, rc: self.__on_connect(rc)
        self.__client.on_message = lambda client, userdata, msg: self.__on_message(msg)
        self.__client.connect(self.__mqtt_data["host"], 1883, 30)
        self.__client.loop_start()
        while not self.is_connect:
            pass

    def __on_message(self, msg: mqtt.MQTTMessage):
        logging.info(f'[mqtt] from {msg.topic} get message {msg.payload}')
        event = data_class_init(json.loads(msg.payload), MqttResponse)
        if event.task_id in self.__listen_map:
            # logging.info(f"[mqtt] task id {event.task_id} in listen map")
            self.__listen_map[event.task_id](event)
        # 任务完成状态把监听器移除
        if event.event_type in [3, 4]:
            self.__listen_map.pop(event.task_id, None)

    def add_listener(self, task_id: str, callback: Callback):
        """
        添加一个监听器
        :param task_id: 任务id
        :param callback: 任务回调
        :return:
        """
        self.__listen_map[task_id] = callback

    def close(self):
        """
        关闭mqtt连接
        :return:
        """
        if self.__client is not None:
            self.__client.loop_stop()
            self.__client.disconnect()
        self.is_connect = False

    @abstractmethod
    def start(self):
        """
        启动mqtt客户端
        :return:
        """
        pass
