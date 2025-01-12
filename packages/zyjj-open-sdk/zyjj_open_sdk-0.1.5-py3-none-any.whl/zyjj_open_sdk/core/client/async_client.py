from typing import Any
from httpx import AsyncClient, Response

from zyjj_open_sdk.core.client.base import BaseClient, Request
from zyjj_open_sdk.core.exception import SDKError

class OpenAsyncClient(BaseClient):
    def __init__(self, sk: str, host: str):
        super().__init__(sk, host)
        self.__sk = sk
        self.__client = AsyncClient(
            base_url=self.get_base_url(),
            headers=self.get_header(),
            timeout=self.timeout
        )

        self.__report_event()

    async def __request(self, request: Request) -> Any:
        res: Response
        if request.method == 'get':
            res = await self.__client.get(request.url)
        elif request.method == 'post':
            res = await self.__client.post(request.url, json=request.data)
        else:
            raise SDKError("method error")
        return self.res_parse(res)

    async def __report_event(self):
        await self.__request(super()._report_event())

    async def get_point(self) -> int:
        return await self.__request(super()._get_point())

    async def execute(self, task_type: int, _input: dict) -> dict:
        return await self.__request(super()._execute(task_type, _input))

    async def execute_async(self, task_type: int, _input: dict) -> str:
        return await self.__request(super()._execute_async(task_type, _input))

    async def get_task_status(self, task_id: str) -> dict:
        return await self.__request(super()._get_task_status(task_id))

    async def get_file_token(self, file_name: str, file_size: int, source: int = 1) -> dict:
        return await self.__request(super()._get_file_token(file_name, file_size, source))

    async def file_multipart_init(self, file_name: str, file_size: int, source: int = 1) -> str:
        return await self.__request(super()._file_multipart_init(file_name, file_size, source))

    async def file_multipart_part(self, upload_id: str, part_num: int) -> dict:
        return await self.__request(super()._file_multipart_part(upload_id, part_num))

    async def file_multipart_complete(self, upload_id: str, part_list: list) -> dict:
        return await self.__request(super()._file_multipart_complete(upload_id, part_list))

    async def get_mqtt_task(self) -> dict:
        return await self.__request(super()._get_mqtt_task())
