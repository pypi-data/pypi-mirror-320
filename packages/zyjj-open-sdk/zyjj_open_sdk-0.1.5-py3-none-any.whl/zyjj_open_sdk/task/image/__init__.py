from zyjj_open_sdk.core import OpenClient, OpenAsyncClient, MqttAsyncClient, FileObject, TaskExecute, TaskExecuteAsync, get_input, async_get_input, MqttClient
from typing import Literal, Type
from zyjj_open_sdk.task.image.entity import *

class Image:
    def __init__(self, client: OpenClient, mqtt: MqttClient):
        self.__client = client
        self.__mqtt = mqtt

    def image_enhance(self, img: FileObject) -> TaskExecute[Type[ImageEnhanceResp]]:
        """
        图像增强
        :param img: 原始图片,清晰度低的照片
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1005,
            {},
            {'img': img},
            ImageEnhanceResp
        )

    def text_to_img(self, prompt: str, style: Literal['000', '201', '202', '203', '204', '301', '401', '101', '102', '103', '118', '104', '105', '106', '107', '108', '109', '119', '110', '111', '112', '113', '114', '115', '116', '117'], size: Literal['768:768', '768:1024', '1024:768', '1024:1024', '720:1280', '1280:720', '768:1280', '1280:768', '1080:1920', '1920:1080'], negative: str = None) -> TaskExecute[Type[TextToImgResp]]:
        """
        AI绘画
        :param prompt: 图片描述,建议使用中文输入，详细描述画面主体、细节、场景等，文本描述越丰富，生成效果越精美
        :param style: 绘画风格,000：不限定风格、201：日系动漫、202：怪兽风格、203：唯美古风、204：复古动漫、301：游戏卡通手绘、401：通用写实风格、101：水墨画、102：概念艺术、103：油画1、118：油画2（梵高）、104：水彩画、105：像素画、106：厚涂风格、107：插图、108：剪纸风格、109：印象派1（莫奈）、119：印象派2、110：2.5D、111：古典肖像画、112：黑白素描画、113：赛博朋克、114：科幻风格、115：暗黑风格、116：3D、117：蒸汽波
        :param size: 图片大小,768:768（1:1）、768:1024（3:4）、1024:768（4:3）、1024:1024（1:1）、720:1280（9:16）、1280:720（16:9）、768:1280（3:5）、1280:768（5:3）、1080:1920（9:16）、1920:1080（16:9)
        :param negative: 反向描述,使用中文输入不希望出现的内容
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1006,
            {},
            {'prompt': prompt, 'style': style, 'size': size, 'negative': negative},
            TextToImgResp
        )

    def img_to_img(self, img: FileObject, style: Literal['104', '107', '116', '201', '203'], size: Literal['origin', '768:768', '768:1024', '1024:768'], prompt: str = None, negative: str = None, strength: float = None) -> TaskExecute[Type[ImgToImgResp]]:
        """
        图生图
        :param img: 原始图片,参考图片
        :param style: 绘画风格,104：水彩画、107：卡通插画、116：3D、201：日系动漫、203：唯美古风
        :param size: 图片尺寸,origin（原图大小）、768:768（1：1）、768:1024（3：4）、1024:768（4：3）
        :param prompt: 辅助文本描述,建议使用中文输入希望出现的内容
        :param negative: 反向描述,使用中文输入不希望出现的内容
        :param strength: 图片自由度,取值范围0~1，生成自由度越小，生成图和原图越接近
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1007,
            {},
            {'img': img, 'style': style, 'size': size, 'prompt': prompt, 'negative': negative, 'strength': strength},
            ImgToImgResp
        )

    def face_age_change(self, img: FileObject, age: int) -> TaskExecute[Type[FaceAgeChangeResp]]:
        """
        人脸年龄变化
        :param img: 人脸图片,需要上传带人脸的图片
        :param age: 年龄,要变化的年龄，范围 10-80
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1008,
            {},
            {'img': img, 'age': age},
            FaceAgeChangeResp
        )

    def face_sex_change(self, img: FileObject, gender: int) -> TaskExecute[Type[FaceSexChangeResp]]:
        """
        人脸性别变化
        :param img: 人脸图片,需要上传带人脸的图片
        :param gender: 性别,性别：0（男变女）、1（女变男）
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1009,
            {},
            {'img': img, 'gender': gender},
            FaceSexChangeResp
        )

    def face_animation(self, img: FileObject) -> TaskExecute[Type[FaceAnimationResp]]:
        """
        人脸动漫化
        :param img: 人脸图片,需要上传带人脸的图片
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1010,
            {},
            {'img': img},
            FaceAnimationResp
        )

    def people_segment(self, img: FileObject) -> TaskExecute[Type[PeopleSegmentResp]]:
        """
        人像抠图
        :param img: 人脸图片,需要上传带人脸的图片
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1011,
            {},
            {'img': img},
            PeopleSegmentResp
        )

    def img_inpainting(self, img: FileObject, mask: FileObject) -> TaskExecute[Type[ImgInpaintingResp]]:
        """
        图像消除(图像修复)
        :param img: 原始图片,[示例图片](https://img.zyjj.cc/help/202412180903525.png)
        :param mask: 掩码图片,和原始图片大小一致，需要把透明区域设置为白色，要擦除区域设置为黑色 <br /> [示例图片](https://img.zyjj.cc/help/202412180904221.png)
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1032,
            {},
            {'img': img, 'mask': mask},
            ImgInpaintingResp
        )

    def id_photo_generate(self, img: FileObject, background: Literal['#d74532', '#628bce', '#FFFFFF', '#000000', '#4b6190', '#f2f0f0'], size: Literal['531x709', '600x600', '390x567', '358x441', '413x531', '260x378', '295x413', '1050x1499', '144x192', '413x626']) -> TaskExecute[Type[IdPhotoGenerateResp]]:
        """
        证件照生成
        :param img: 人脸图片,上传带人脸的图片
        :param background: 背景颜色,#d74532（红色）、#628bce（蓝色）、#FFFFFF（白色）、#000000（黑色）、#4b6190（深蓝色）、#f2f0f0（深灰色）
        :param size: 图片尺寸,295x413（一寸）、413x626（二寸）、260x378（小一寸）、413x531（小二寸）、390x567（大一寸）、413x626（大二寸）、1050x1499（五寸）、295x413（教师资格证）、295x413（国家公务员考试）、295x413 （初级会计考试）、144x192（英语四六级）、390x567（计算机等级考试）、531x709（研究生考试）、358x441（社保卡）、260x378（电子驾驶证）、600x600（美国签证）、295x413（日本签证）、413x531（韩国签证）
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1033,
            {},
            {'img': img, 'background': background, 'size': size},
            IdPhotoGenerateResp
        )

    def comic_translate(self, img: FileObject) -> TaskExecute[Type[ComicTranslateResp]]:
        """
        漫画翻译
        :param img: 漫画图片,任意语言的漫画图片
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1038,
            {},
            {'img': img},
            ComicTranslateResp
        )

    def img_colorful(self, img: FileObject) -> TaskExecute[Type[ImgColorfulResp]]:
        """
        照片上色
        :param img: 黑白图片,支持常见图片格式
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1039,
            {},
            {'img': img},
            ImgColorfulResp
        )


class AsyncImage:
    def __init__(self, client: OpenAsyncClient, mqtt: MqttAsyncClient):
        self.__client = client
        self.__mqtt = mqtt

    def image_enhance(self, img: FileObject) -> TaskExecuteAsync[Type[ImageEnhanceResp]]:
        """
        图像增强
        :param img: 原始图片,清晰度低的照片
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1005,
            {},
            {'img': img},
            ImageEnhanceResp
        )

    def text_to_img(self, prompt: str, style: Literal['000', '201', '202', '203', '204', '301', '401', '101', '102', '103', '118', '104', '105', '106', '107', '108', '109', '119', '110', '111', '112', '113', '114', '115', '116', '117'], size: Literal['768:768', '768:1024', '1024:768', '1024:1024', '720:1280', '1280:720', '768:1280', '1280:768', '1080:1920', '1920:1080'], negative: str = None) -> TaskExecuteAsync[Type[TextToImgResp]]:
        """
        AI绘画
        :param prompt: 图片描述,建议使用中文输入，详细描述画面主体、细节、场景等，文本描述越丰富，生成效果越精美
        :param style: 绘画风格,000：不限定风格、201：日系动漫、202：怪兽风格、203：唯美古风、204：复古动漫、301：游戏卡通手绘、401：通用写实风格、101：水墨画、102：概念艺术、103：油画1、118：油画2（梵高）、104：水彩画、105：像素画、106：厚涂风格、107：插图、108：剪纸风格、109：印象派1（莫奈）、119：印象派2、110：2.5D、111：古典肖像画、112：黑白素描画、113：赛博朋克、114：科幻风格、115：暗黑风格、116：3D、117：蒸汽波
        :param size: 图片大小,768:768（1:1）、768:1024（3:4）、1024:768（4:3）、1024:1024（1:1）、720:1280（9:16）、1280:720（16:9）、768:1280（3:5）、1280:768（5:3）、1080:1920（9:16）、1920:1080（16:9)
        :param negative: 反向描述,使用中文输入不希望出现的内容
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1006,
            {},
            {'prompt': prompt, 'style': style, 'size': size, 'negative': negative},
            TextToImgResp
        )

    def img_to_img(self, img: FileObject, style: Literal['104', '107', '116', '201', '203'], size: Literal['origin', '768:768', '768:1024', '1024:768'], prompt: str = None, negative: str = None, strength: float = None) -> TaskExecuteAsync[Type[ImgToImgResp]]:
        """
        图生图
        :param img: 原始图片,参考图片
        :param style: 绘画风格,104：水彩画、107：卡通插画、116：3D、201：日系动漫、203：唯美古风
        :param size: 图片尺寸,origin（原图大小）、768:768（1：1）、768:1024（3：4）、1024:768（4：3）
        :param prompt: 辅助文本描述,建议使用中文输入希望出现的内容
        :param negative: 反向描述,使用中文输入不希望出现的内容
        :param strength: 图片自由度,取值范围0~1，生成自由度越小，生成图和原图越接近
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1007,
            {},
            {'img': img, 'style': style, 'size': size, 'prompt': prompt, 'negative': negative, 'strength': strength},
            ImgToImgResp
        )

    def face_age_change(self, img: FileObject, age: int) -> TaskExecuteAsync[Type[FaceAgeChangeResp]]:
        """
        人脸年龄变化
        :param img: 人脸图片,需要上传带人脸的图片
        :param age: 年龄,要变化的年龄，范围 10-80
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1008,
            {},
            {'img': img, 'age': age},
            FaceAgeChangeResp
        )

    def face_sex_change(self, img: FileObject, gender: int) -> TaskExecuteAsync[Type[FaceSexChangeResp]]:
        """
        人脸性别变化
        :param img: 人脸图片,需要上传带人脸的图片
        :param gender: 性别,性别：0（男变女）、1（女变男）
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1009,
            {},
            {'img': img, 'gender': gender},
            FaceSexChangeResp
        )

    def face_animation(self, img: FileObject) -> TaskExecuteAsync[Type[FaceAnimationResp]]:
        """
        人脸动漫化
        :param img: 人脸图片,需要上传带人脸的图片
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1010,
            {},
            {'img': img},
            FaceAnimationResp
        )

    def people_segment(self, img: FileObject) -> TaskExecuteAsync[Type[PeopleSegmentResp]]:
        """
        人像抠图
        :param img: 人脸图片,需要上传带人脸的图片
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1011,
            {},
            {'img': img},
            PeopleSegmentResp
        )

    def img_inpainting(self, img: FileObject, mask: FileObject) -> TaskExecuteAsync[Type[ImgInpaintingResp]]:
        """
        图像消除(图像修复)
        :param img: 原始图片,[示例图片](https://img.zyjj.cc/help/202412180903525.png)
        :param mask: 掩码图片,和原始图片大小一致，需要把透明区域设置为白色，要擦除区域设置为黑色 <br /> [示例图片](https://img.zyjj.cc/help/202412180904221.png)
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1032,
            {},
            {'img': img, 'mask': mask},
            ImgInpaintingResp
        )

    def id_photo_generate(self, img: FileObject, background: Literal['#d74532', '#628bce', '#FFFFFF', '#000000', '#4b6190', '#f2f0f0'], size: Literal['531x709', '600x600', '390x567', '358x441', '413x531', '260x378', '295x413', '1050x1499', '144x192', '413x626']) -> TaskExecuteAsync[Type[IdPhotoGenerateResp]]:
        """
        证件照生成
        :param img: 人脸图片,上传带人脸的图片
        :param background: 背景颜色,#d74532（红色）、#628bce（蓝色）、#FFFFFF（白色）、#000000（黑色）、#4b6190（深蓝色）、#f2f0f0（深灰色）
        :param size: 图片尺寸,295x413（一寸）、413x626（二寸）、260x378（小一寸）、413x531（小二寸）、390x567（大一寸）、413x626（大二寸）、1050x1499（五寸）、295x413（教师资格证）、295x413（国家公务员考试）、295x413 （初级会计考试）、144x192（英语四六级）、390x567（计算机等级考试）、531x709（研究生考试）、358x441（社保卡）、260x378（电子驾驶证）、600x600（美国签证）、295x413（日本签证）、413x531（韩国签证）
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1033,
            {},
            {'img': img, 'background': background, 'size': size},
            IdPhotoGenerateResp
        )

    def comic_translate(self, img: FileObject) -> TaskExecuteAsync[Type[ComicTranslateResp]]:
        """
        漫画翻译
        :param img: 漫画图片,任意语言的漫画图片
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1038,
            {},
            {'img': img},
            ComicTranslateResp
        )

    def img_colorful(self, img: FileObject) -> TaskExecuteAsync[Type[ImgColorfulResp]]:
        """
        照片上色
        :param img: 黑白图片,支持常见图片格式
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1039,
            {},
            {'img': img},
            ImgColorfulResp
        )
