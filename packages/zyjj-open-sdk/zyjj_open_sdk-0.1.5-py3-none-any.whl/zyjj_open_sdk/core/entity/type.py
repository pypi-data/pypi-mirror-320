import logging
from dataclasses import dataclass, fields
from typing import TypeVar, Callable, Any
from zyjj_open_sdk.core.exception import ServerError, SDKError

import httpx

T = TypeVar('T')  # 定义一个类型变量 T

# 各种回调函数
ProgressCallback = Callable[[float], None]
SuccessCallback = Callable[[T], None]
ErrorCallback = Callable[[ServerError], None]
DetailCallback = Callable[[dict], None]

def data_class_init(data: dict, cls: T) -> T:
    init = {}
    # logging.info(f"data class init {cls} data {data}")
    # 过滤掉不需要的字段
    for field in fields(cls):
        if field.name not in data:
            continue
        # 几种特殊类型不需要转换
        field_type = str(field.type)
        if field_type in ['dict[str, str]', 'list[str]', "<class 'dict'>", 'typing.Any']:
            pass
        # dict和list需要单独转换
        elif isinstance(data[field.name], dict):
            logging.info(f"init dict {field.type}")
            data[field.name] = data_class_init(data[field.name], field.type)
        elif isinstance(data[field.name], list) and hasattr(field.type, '__args__'):
            logging.info(f"init list {field.type}")
            data[field.name] = [data_class_init(item, field.type.__args__[0]) for item in data[field.name]]
        init[field.name] = data[field.name]

    return cls(**init)

@dataclass
class FileObject:
    path: str = None
    file_name: str = None
    file_content: bytes = None
    url: str = None
    headers: dict = None

    @classmethod
    def from_path(cls, path: str):
        """
        从本地路径初始化
        :param path: 文件所在路径
        :return:
        """
        # win系统需要替换路径
        new_path = path.replace('\\', '/')
        return cls(path=path, file_name=new_path.split('/')[-1])

    @classmethod
    def from_bytes(cls, file_name: str, data: bytes):
        """
        从字节流初始化
        :param file_name: 文件名称
        :param data: 文件数据
        :return:
        """
        if file_name == '' or file_name is None:
            raise SDKError('文件名不能为空')
        return cls(file_name=file_name, file_content=data)

    @classmethod
    def from_url(cls, url: str, headers: dict = None):
        """
        从url初始化
        :param url: 资源url
        :param headers: 请求header信息，可为空
        :return:
        """
        # 从资源url中获取文件名称
        name = url.split('/')[-1].split('?')[0]
        return cls(url=url, headers=headers, file_name=name)
