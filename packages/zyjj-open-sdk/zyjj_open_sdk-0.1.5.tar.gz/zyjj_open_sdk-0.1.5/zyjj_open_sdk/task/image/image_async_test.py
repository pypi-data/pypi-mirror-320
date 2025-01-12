import os
import logging
import pytest
from dotenv import load_dotenv
from zyjj_open_sdk import AsyncClient, FileObject

# 加载 .env 文件
load_dotenv()
client = AsyncClient(os.getenv('sk'))


@pytest.mark.asyncio
async def test_image_enhance():
    res = await client.image.image_enhance(img=FileObject.from_path("people.png")).execute()
    print(res.img_url)

@pytest.mark.asyncio
async def test_text_to_img():
    res = await client.image.text_to_img(prompt="长发女孩、头戴花环、精致脸蛋、强烈的光影对比", style="201", size="1920:1080").execute()
    print(res.img_url)

@pytest.mark.asyncio
async def test_img_to_img():
    res = await client.image.img_to_img(img=FileObject.from_path("people.png"), style="104", size="origin").execute()
    print(res.img_url)

@pytest.mark.asyncio
async def test_face_age_change():
    res = await client.image.face_age_change(img=FileObject.from_path("people.png"), age=10).execute()
    print(res.img_url)

@pytest.mark.asyncio
async def test_face_sex_change():
    res = await client.image.face_sex_change(img=FileObject.from_path("people.png"), gender=1).execute()
    print(res.img_url)

@pytest.mark.asyncio
async def test_face_animation():
    res = await client.image.face_animation(img=FileObject.from_path("people.png")).execute()
    print(res.img_url)

@pytest.mark.asyncio
async def test_people_segment():
    res = await client.image.people_segment(img=FileObject.from_path("people.png")).execute()
    print(res.img_url)

@pytest.mark.asyncio
async def test_img_inpainting():
    res = await client.image.img_inpainting(img=FileObject.from_path("test.png"), mask=FileObject.from_path("mask.png")).execute_async_wait(lambda i: logging.info(f"progres: {i}"))
    print(res.img_url)

@pytest.mark.asyncio
async def test_id_photo_generate():
    res = await client.image.id_photo_generate(img=FileObject.from_path("people.png"), background="#d74532", size="295x413").execute_async_wait(lambda i: logging.info(f"progres: {i}"))
    print(res.img_url)

@pytest.mark.asyncio
async def test_comic_translate():
    res = await client.image.comic_translate(img=FileObject.from_path("日文.jpg")).execute_async_wait(lambda i: logging.info(f"progres: {i}"))
    print(res.img_url)

@pytest.mark.asyncio
async def test_img_colorful():
    res = await client.image.img_colorful(img=FileObject.from_path("black.png")).execute_async_wait(lambda i: logging.info(f"progres: {i}"))
    print(res.img_url)





