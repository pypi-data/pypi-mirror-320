import os
import logging
from dotenv import load_dotenv
from zyjj_open_sdk import Client, FileObject

# 加载 .env 文件
load_dotenv()
client = Client(os.getenv('sk'))


def test_subtitle_generate():
    res = client.subtitle.subtitle_generate(audio=FileObject.from_path("test.mp3")).execute_async().wait(lambda i: logging.info(f"progres: {i}"))
    print(res.subtitle)

def test_subtitle_generate_multilingual():
    res = client.subtitle.subtitle_generate_multilingual(audio=FileObject.from_path("test.mp3"), language="zh").execute_async().wait(lambda i: logging.info(f"progres: {i}"))
    print(res.subtitle)

def test_subtitle_translate():
    res = client.subtitle.subtitle_translate(subtitle=FileObject.from_path("test.srt"), language="英语", mode=0).execute_async().wait(lambda i: logging.info(f"progres: {i}"))
    print(res.translated)





