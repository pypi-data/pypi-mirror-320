import os
import logging
import pytest
from dotenv import load_dotenv
from zyjj_open_sdk import AsyncClient, FileObject

# 加载 .env 文件
load_dotenv()
client = AsyncClient(os.getenv('sk'))


@pytest.mark.asyncio
async def test_subtitle_generate():
    res = await client.subtitle.subtitle_generate(audio=FileObject.from_path("test.mp3")).execute_async_wait(lambda i: logging.info(f"progres: {i}"))
    print(res.subtitle)

@pytest.mark.asyncio
async def test_subtitle_generate_multilingual():
    res = await client.subtitle.subtitle_generate_multilingual(audio=FileObject.from_path("test.mp3"), language="zh").execute_async_wait(lambda i: logging.info(f"progres: {i}"))
    print(res.subtitle)

@pytest.mark.asyncio
async def test_subtitle_translate():
    res = await client.subtitle.subtitle_translate(subtitle=FileObject.from_path("test.srt"), language="英语", mode=0).execute_async_wait(lambda i: logging.info(f"progres: {i}"))
    print(res.translated)





