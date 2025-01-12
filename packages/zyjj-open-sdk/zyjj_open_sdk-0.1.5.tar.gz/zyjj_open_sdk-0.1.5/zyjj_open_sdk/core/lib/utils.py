import logging

from zyjj_open_sdk.core.entity.type import FileObject
from zyjj_open_sdk.core.client import OpenClient, OpenAsyncClient
from zyjj_open_sdk.core.lib.file import FileUtils

def get_init(init: dict, data: dict) -> dict:
    for k, v in data.items():
        if v is None:
            continue
        # 如果k包含.那么就需要拆分
        if '.' in k:
            k = k.split('.')
            # 目前只支持两级
            k0, k1 = k
            if k0 not in init:
                init[k0] = {}
            init[k0][k1] = v
        else:
            init[k] = v
    return init

def get_input(client: OpenClient, init: dict, data: dict, source: int = 1) -> dict:
    init = get_init(init, data)
    for k, v in init.items():
        # 如果v是文件类型就需要上传获取上传地址
        if isinstance(v, FileObject):
            init[k] = FileUtils(client).file_upload(v, source)
    logging.info(f"input is {init}")
    return init

async def async_get_input(client: OpenAsyncClient, init: dict, data: dict, source: int = 1) -> dict:
    init = get_init(init, data)
    for k, v in init.items():
        # 如果v是文件类型就需要上传获取上传地址
        if isinstance(v, FileObject):
            init[k] = await FileUtils(async_client=client).async_file_upload(v, source)
    logging.info(f"input is {init}")
    return init
