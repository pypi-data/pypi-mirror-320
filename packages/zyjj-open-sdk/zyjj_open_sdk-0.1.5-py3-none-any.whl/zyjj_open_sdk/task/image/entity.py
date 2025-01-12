from dataclasses import dataclass

@dataclass
class ImageEnhanceResp:
    """图像增强结果"""
    img_url: str  # 增强后的图片

@dataclass
class TextToImgResp:
    """AI绘画结果"""
    img_url: str  # 生成的图片地址

@dataclass
class ImgToImgResp:
    """图生图结果"""
    img_url: str  # 生成的图片地址

@dataclass
class FaceAgeChangeResp:
    """人脸年龄变化结果"""
    img_url: str  # 处理后的图片地址

@dataclass
class FaceSexChangeResp:
    """人脸性别变化结果"""
    img_url: str  # 处理后的图片地址

@dataclass
class FaceAnimationResp:
    """人脸动漫化结果"""
    img_url: str  # 处理后的图片地址

@dataclass
class PeopleSegmentResp:
    """人像抠图结果"""
    img_url: str  # 处理后的图片地址

@dataclass
class ImgInpaintingResp:
    """图像消除(图像修复)结果"""
    img_url: str  # 处理后的图片地址

@dataclass
class IdPhotoGenerateResp:
    """证件照生成结果"""
    img_url: str  # 证件照地址

@dataclass
class ComicTranslateResp:
    """漫画翻译结果"""
    img_url: str  # 翻译好的图片地址

@dataclass
class ImgColorfulResp:
    """照片上色结果"""
    img_url: str  # 彩色图片地址
