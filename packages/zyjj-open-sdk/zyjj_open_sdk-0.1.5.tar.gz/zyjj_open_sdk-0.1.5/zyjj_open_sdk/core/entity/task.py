import time
from abc import ABC, abstractmethod


from zyjj_open_sdk.core.client import OpenClient, MqttClient, MqttResponse
from zyjj_open_sdk.core.client.base import BaseMqttClient
from zyjj_open_sdk.core.exception import ServerError
from zyjj_open_sdk.core.entity.type import T, data_class_init, ProgressCallback, SuccessCallback, ErrorCallback, DetailCallback
from zyjj_open_sdk.core.lib import get_input
from dataclasses import dataclass
from typing import Generic, Type, Optional


# 任务异步执行结果(同步)
class TaskExecuteBase(ABC):
    def __init__(self, task_id: str, mqtt: BaseMqttClient, output: dataclass):
        self.__task_id = task_id
        self.__mqtt = mqtt
        # 任务输出结果
        self._output = output
        # 任务执行进度
        self.__progress: float = 0
        # 任务执行状态
        self._status = 1  # 1 开始 2 进度 3 成功 4 失败 5 追加 6 设置
        # 任务详情信息
        self._detail = {}
        # 异常信息
        self._exception = None
        # 监听mqtt状态回调
        self.__mqtt.add_listener(self.__task_id, self.__on_mqtt_message)
        # 各种监听器
        self._progress_callbacks: list[ProgressCallback] = []
        self._success_callbacks: list[SuccessCallback] = []
        self._error_callbacks: list[ErrorCallback] = []
        self._detail_callbacks: list[DetailCallback] = []

    def __on_mqtt_message(self, msg: Type[MqttResponse]):
        self._status = msg.event_type
        if self._status == 2:  # 进度
            self.__progress = float(msg.data)
            for callback in self._progress_callbacks:
                callback(self.__progress)
        elif self._status == 3:  # 成功
            self._output = data_class_init(msg.data, self._output)
            for callback in self._success_callbacks:
                callback(self._output)
        elif self._status == 4:  # 失败
            self._exception = ServerError(msg.code, msg.data)
            for callback in self._error_callbacks:
                callback(self._exception)
        elif self._status == 5:  # 详情追加
            for callback in self._detail_callbacks:
                if isinstance(msg.data, dict):
                    for k, v in msg.data.items():
                        if k not in self._detail:
                            self._detail[k] = v
                        else:
                            self._detail[k] += v
                callback(self._detail)

    @property
    def err(self) -> Optional[ServerError]:
        """
        获取任务的错误信息
        :return: 错误信息
        """
        return self._exception

    @property
    def output(self) -> Optional[T]:
        """
        获取任务的错误信息
        :return: 任务结果（任务未成功或进行中为None）
        """
        if self._status != 2:
            return None
        return self._output

    @property
    def progress(self) -> float:
        """
        获取任务执行进度
        :return: 进度信息
        """
        return self.__progress

    @property
    def status(self) -> int:
        """
        获取任务状态
        :return: 任务状态信息 1 创建 2 执行中 3 成功 4 失败
        """
        if self._status in [3, 4, 1]:
            return self._status
        else:
            return 2

    @abstractmethod
    def wait(self, progress_callback: ProgressCallback = None) -> T:
        """
        一直阻塞直到任务完成
        :param progress_callback: 进度回调
        :return:
        """
        pass

    def listener(
            self,
            on_progress: ProgressCallback = None,
            on_success: SuccessCallback = None,
            on_error: ErrorCallback = None,
            on_detail: DetailCallback = None
    ):
        """
        监听任务进度
        :param on_progress: 进度回调
        :param on_success: 成功回调
        :param on_error: 失败回调
        :param on_detail: 详情回调
        :return:
        """
        if on_progress is not None:
            self._progress_callbacks.append(on_progress)
        if on_success is not None:
            self._success_callbacks.append(on_success)
        if on_error is not None:
            self._error_callbacks.append(on_error)
        if on_detail is not None:
            self._detail_callbacks.append(on_detail)


# 任务异步执行结果(同步)
class TaskExecuteResult(Generic[T], TaskExecuteBase):
    def __init__(self, task_id: str, mqtt: MqttClient, output: dataclass):
        super().__init__(task_id, mqtt, output)

    def wait(self, progress_callback: ProgressCallback = None, detail_callback: DetailCallback = None) -> T:
        if progress_callback is not None:
            self._progress_callbacks.append(progress_callback)
        if detail_callback is not None:
            self._detail_callbacks.append(detail_callback)
        while True:
            time.sleep(0.1)
            if self._status == 3:
                return self._output
            elif self._status == 4:
                raise self._exception


# 任务执行器
class TaskExecute(Generic[T]):
    def __init__(self, client: OpenClient, mqtt: MqttClient, task_type: int, init: dict, _input: dict, output: T, source: int = 1):
        self.__client = client
        self.__mqtt = mqtt
        self.__task_type = task_type
        self.__init = init
        self.__init_input = _input
        self.__source = source
        self.__input = None
        self.__output = output

    def __get_input(self):
        if self.__input is not None:
            return self.__input
        self.__input = get_input(self.__client, self.__init, self.__init_input, self.__source)
        return self.__input

    def execute(self) -> T:
        """同步执行"""
        return data_class_init(self.__client.execute(self.__task_type, self.__get_input()), self.__output)

    def execute_async(self) -> TaskExecuteResult[T]:
        """异步执行"""
        self.__mqtt.start()
        task_id = self.__client.execute_async(self.__task_type, self.__get_input())
        return TaskExecuteResult[T](task_id, self.__mqtt, self.__output)

    def execute_async_wait(
            self,
            progress_callback: ProgressCallback = None,
            detail_callback: DetailCallback = None
    ) -> T:
        """
        异步执行并等待任务完成
        :param progress_callback: 进度回调
        :param detail_callback: 详情回调
        :return:
        """
        return self.execute_async().wait(progress_callback, detail_callback)

    @staticmethod
    def _get_input(init: dict, **kwargs) -> dict:
        data = init.copy()
        for k, v in kwargs.items():
            if v is not None:
                data[k] = v
        return data
