import asyncio
import logging

from zyjj_open_sdk.core.client import OpenClient, OpenAsyncClient
from zyjj_open_sdk.core.entity.type import FileObject
from zyjj_open_sdk.core.exception import SDKError, RequestError
from httpx import Client, AsyncClient
from pathlib import Path


class FileUtils:
    def __init__(self, client: OpenClient = None, async_client: OpenAsyncClient = None):
        self.__client = client
        self.__async_client = async_client
        self.__http = Client()
        self.__async_http = AsyncClient()
        self.__timout = 600
        self.__max_size = 1024 * 1024 * 20  # 单次最大上传大小
        self.__chunk_size = 1024 * 1024 * 5  # 分片上传大小
        self.__semaphore = asyncio.Semaphore(5)  # 限制同步并发上传数

    # 全量上传
    def __full_upload(self, file_name: str, data: bytes, source: int):
        token = self.__client.get_file_token(file_name, len(data), source)
        auth, file = token["auth"], token["file"]
        # 上传文件
        res = self.__http.put(auth["url"], content=data, headers=auth["header"], timeout=self.__timout)
        if res.status_code != 200:
            raise RequestError(res.status_code, res.text)
        return file

    # 全量上传
    async def __async_full_upload(self, file_name: str, data: bytes, source: int):
        async with self.__semaphore:
            token = await self.__async_client.get_file_token(file_name, len(data), source)
            auth, file = token["auth"], token["file"]
            # 上传文件
            res = await self.__async_http.put(auth["url"], content=data, headers=auth["header"], timeout=self.__timout)
            if res.status_code != 200:
                raise RequestError(res.status_code, res.text)
            return file

    def __multipart_upload(self, file_name: str, file_size: int, path: str, source: int) -> dict:
        upload_id = self.__client.file_multipart_init(file_name, file_size, source)
        part_list = []
        # 分片读取文件信息
        with open(path, "rb") as f:
            # part_num 需要从1开始
            part_num = 1
            while True:
                part_data = f.read(self.__chunk_size)  # 读取指定大小的块
                if not part_data:  # 如果没有更多数据，退出循环
                    break
                # 获取鉴权信息
                data = self.__client.file_multipart_part(upload_id, part_num)
                # 上传文件
                res = self.__http.put(data["url"], content=part_data, headers=data["header"], timeout=self.__timout)
                if res.status_code != 200:
                    raise RequestError(res.status_code, res.text)
                # 从返回的header中获取etag信息
                part_list.append({"part_num": part_num, "etag": res.headers.get("etag")})
                part_num += 1
        logging.info(f"part list {part_list}")
        # 最后我们完成上传
        return self.__client.file_multipart_complete(upload_id, part_list)

    async def __async_multipart_part(self, upload_id: str, part_num: int, part_data: bytes) -> dict:
        # 获取鉴权信息
        data = await self.__async_client.file_multipart_part(upload_id, part_num)
        # 上传文件
        res = await self.__async_http.put(data["url"], content=part_data, headers=data["header"], timeout=self.__timout)
        if res.status_code != 200:
            raise RequestError(res.status_code, res.text)
        return {"part_num": part_num, "etag": res.headers.get("etag")}

    async def __async_multipart_upload(self, file_name: str, file_size: int, path: str, source: int) -> dict:
        async with self.__semaphore:
            upload_id = await self.__async_client.file_multipart_init(file_name, file_size, source)
            task_list = []
            # 分片读取文件信息
            with open(path, "rb") as f:
                # part_num 需要从1开始
                part_num = 1
                while True:
                    part_data = f.read(self.__chunk_size)  # 读取指定大小的块
                    if not part_data:  # 如果没有更多数据，退出循环
                        break
                    # 上传任务推送到线程池中执行
                    task_list.append(asyncio.create_task(self.__async_multipart_part(upload_id, part_num, part_data)))
            part_list = await asyncio.gather(*task_list)
            logging.info(f"part list {part_list}")
            # 最后我们完成上传
            return await self.__async_client.file_multipart_complete(upload_id, part_list)

    def __get_bytes_or_path(self, file: FileObject) -> (bytes | str, int):
        if file.file_content is not None and len(file.file_content):
            # 如果字节流有数据就直接从字节流中加载
            return file.file_content, len(file.file_content)
        elif file.path is not None:
            path = Path(file.path)
            # 判断一下文件是否存在
            if not path.is_file():
                raise SDKError("文件不存在")
            # 判断一下文件大小
            file_size = path.stat().st_size
            if file_size > self.__max_size:  # 超过最大单次上传大小就使用分片上传
                return file.path, file_size
            else:
                return path.read_bytes(), file_size

    def __download_url(self, file: FileObject) -> (bytes, int):
        logging.info(f"[file] start download {file.url}")
        res = self.__http.get(file.url, headers=file.headers)
        res.raise_for_status()
        data = res.content
        return data, len(data)

    async def __async_download_url(self, file: FileObject) -> (bytes, int):
        logging.info(f"[file] start async download {file.url}")
        res = await self.__async_http.get(file.url, headers=file.headers)
        res.raise_for_status()
        data = res.content
        return data, len(data)

    # 文件上传
    def file_upload(self, file: FileObject, source: int = 1) -> dict:
        if file.url is not None:
            data, file_size = self.__download_url(file)
        else:
            data, file_size = self.__get_bytes_or_path(file)
        if isinstance(data, bytes):
            return self.__full_upload(file.file_name, data, source)
        elif isinstance(data, str):
            return self.__multipart_upload(file.file_name, file_size, data, source)

    # 异步文件上传
    async def async_file_upload(self, file: FileObject, source: int = 1) -> dict:
        if file.url is not None:
            data, file_size = await self.__async_download_url(file)
        else:
            data, file_size = self.__get_bytes_or_path(file)
        if isinstance(data, bytes):
            return await self.__async_full_upload(file.file_name, data, source)
        elif isinstance(data, str):
            return await self.__async_multipart_upload(file.file_name, file_size, file.path, source)
