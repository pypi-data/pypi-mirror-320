import os
import logging
from dotenv import load_dotenv
from zyjj_open_sdk import Client, FileObject

# 加载 .env 文件
load_dotenv()
client = Client(os.getenv('sk'))


def test_image_enhance():
    res = client.image.image_enhance(img=FileObject.from_path("people.png")).execute()
    print(res.img_url)

def test_text_to_img():
    res = client.image.text_to_img(prompt="长发女孩、头戴花环、精致脸蛋、强烈的光影对比", style="201", size="1920:1080").execute()
    print(res.img_url)

def test_img_to_img():
    res = client.image.img_to_img(img=FileObject.from_path("people.png"), style="104", size="origin").execute()
    print(res.img_url)

def test_face_age_change():
    res = client.image.face_age_change(img=FileObject.from_path("people.png"), age=10).execute()
    print(res.img_url)

def test_face_sex_change():
    res = client.image.face_sex_change(img=FileObject.from_path("people.png"), gender=1).execute()
    print(res.img_url)

def test_face_animation():
    res = client.image.face_animation(img=FileObject.from_path("people.png")).execute()
    print(res.img_url)

def test_people_segment():
    res = client.image.people_segment(img=FileObject.from_path("people.png")).execute()
    print(res.img_url)

def test_img_inpainting():
    res = client.image.img_inpainting(img=FileObject.from_path("test.png"), mask=FileObject.from_path("mask.png")).execute_async().wait(lambda i: logging.info(f"progres: {i}"))
    print(res.img_url)

def test_id_photo_generate():
    res = client.image.id_photo_generate(img=FileObject.from_path("people.png"), background="#d74532", size="295x413").execute_async().wait(lambda i: logging.info(f"progres: {i}"))
    print(res.img_url)

def test_comic_translate():
    res = client.image.comic_translate(img=FileObject.from_path("日文.jpg")).execute_async().wait(lambda i: logging.info(f"progres: {i}"))
    print(res.img_url)

def test_img_colorful():
    res = client.image.img_colorful(img=FileObject.from_path("black.png")).execute_async().wait(lambda i: logging.info(f"progres: {i}"))
    print(res.img_url)





