from typing import Any

from zyjj_open_sdk.core.client.base import BaseClient, Request
from zyjj_open_sdk.core.exception import SDKError
from httpx import Client, Response

class OpenClient(BaseClient):
    def __init__(self, sk: str, host: str):
        super().__init__(sk, host)
        self.__sk = sk
        self.__client = Client(
            base_url=self.get_base_url(),
            headers=self.get_header(),
            timeout=self.timeout
        )
        self.__report_event()

    def __request(self, request: Request) -> Any:
        res: Response
        if request.method == 'get':
            res = self.__client.get(request.url)
        elif request.method == 'post':
            res = self.__client.post(request.url, json=request.data)
        else:
            raise SDKError("method error")
        return self.res_parse(res)

    def __report_event(self):
        self.__request(super()._report_event())

    def get_point(self) -> int:
        return self.__request(super()._get_point())

    def execute(self, task_type: int, _input: dict) -> dict:
        return self.__request(super()._execute(task_type, _input))

    def execute_async(self, task_type: int, _input: dict) -> str:
        return self.__request(super()._execute_async(task_type, _input))

    def get_task_status(self, task_id: str) -> dict:
        return self.__request(super()._get_task_status(task_id))

    def get_file_token(self, file_name: str, file_size: int, source: int = 1) -> dict:
        return self.__request(super()._get_file_token(file_name, file_size, source))

    def file_multipart_init(self, file_name: str, file_size: int, source: int = 1) -> str:
        return self.__request(super()._file_multipart_init(file_name, file_size, source))

    def file_multipart_part(self, upload_id: str, part_num: int) -> dict:
        return self.__request(super()._file_multipart_part(upload_id, part_num))

    def file_multipart_complete(self, upload_id: str, part_list: list) -> dict:
        return self.__request(super()._file_multipart_complete(upload_id, part_list))

    def get_mqtt_task(self) -> dict:
        return self.__request(super()._get_mqtt_task())
