import asyncio
import logging

from zyjj_open_sdk.core.client import OpenAsyncClient, MqttAsyncClient
from zyjj_open_sdk.core.entity.type import T, data_class_init, ProgressCallback, DetailCallback
from zyjj_open_sdk.core.entity.task import TaskExecuteBase
from zyjj_open_sdk.core.lib import async_get_input
from dataclasses import dataclass
from typing import Generic


# 任务异步执行结果(同步)
class AsyncTaskExecuteResult(Generic[T], TaskExecuteBase):
    def __init__(self, task_id: str, mqtt: MqttAsyncClient, output: dataclass):
        super().__init__(task_id, mqtt, output)

    async def wait(self, progress_callback: ProgressCallback = None, detail_callback: DetailCallback = None) -> T:
        """
        一直阻塞直到任务完成
        :param progress_callback: 进度回调
        :param detail_callback: 详情回调
        :return:
        """
        if progress_callback is not None:
            self._progress_callbacks.append(progress_callback)
        if detail_callback is not None:
            self._detail_callbacks.append(detail_callback)
        while True:
            await asyncio.sleep(0.1)
            if self._status == 3:
                return self._output
            elif self._status == 4:
                raise self._exception

# 异步任务执行器
class TaskExecuteAsync(Generic[T]):
    def __init__(
        self,
        client: OpenAsyncClient,
        mqtt: MqttAsyncClient,
        task_type: int,
        init: dict,
        _input: dict,
        output: T,
        source: int = 1
    ):
        self.__client = client
        self.__mqtt = mqtt
        self.__task_type = task_type
        self.__init_input = _input
        self.__init = init
        self.__source = source
        # 默认input只初始化一次
        self.__input = None
        self.__output = output

    async def __get_input(self):
        if self.__input is not None:
            return self.__input
        self.__input = await async_get_input(self.__client, self.__init, self.__init_input, self.__source)
        return self.__input

    async def execute(self) -> T:
        """同步执行"""
        return data_class_init(await self.__client.execute(self.__task_type, await self.__get_input()), self.__output)

    async def execute_async(self) -> AsyncTaskExecuteResult[T]:
        """异步执行"""
        await self.__mqtt.start()
        task_id = await self.__client.execute_async(self.__task_type, await self.__get_input())
        return AsyncTaskExecuteResult[T](task_id, self.__mqtt, self.__output)

    async def execute_async_wait(
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
        return await (await self.execute_async()).wait(progress_callback, detail_callback)

    @staticmethod
    def _get_input(init: dict, **kwargs) -> dict:
        data = init.copy()
        for k, v in kwargs.items():
            if v is not None:
                data[k] = v
        return data
