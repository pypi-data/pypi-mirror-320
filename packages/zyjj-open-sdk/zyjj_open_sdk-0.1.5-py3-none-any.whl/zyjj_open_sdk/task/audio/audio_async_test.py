import os
import logging
import pytest
from dotenv import load_dotenv
from zyjj_open_sdk import AsyncClient, FileObject

# 加载 .env 文件
load_dotenv()
client = AsyncClient(os.getenv('sk'))


@pytest.mark.asyncio
async def test_voice_recognize():
    res = await client.audio.voice_recognize(audio=FileObject.from_path("speech.wav")).execute()
    print(res.text)

@pytest.mark.asyncio
async def test_voice_generate_azure():
    res = await client.audio.voice_generate_azure(voice_name="zh-CN-YunzeNeural", text="欢迎使用智游剪辑").execute()
    print(res.audio_url)

@pytest.mark.asyncio
async def test_audio_separate():
    res = await client.audio.audio_separate(audio=FileObject.from_path("黑泽明.mp3"), option="no_vocals").execute_async_wait(lambda i: logging.info(f"progres: {i}"))
    print(res.vocals)





