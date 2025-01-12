from dataclasses import dataclass

@dataclass
class BiliVideoParseVideo:
    """B站视频解析结果-视频文件信息，如果需要最后的视频文件，可以使用`ffmpeg -i xx.m4a -i xx.m4a xx.mp4`来合成"""
    url: str  # 下载链接
    filename: str  # 文件名
    headers: dict[str, str]  # 请求头

@dataclass
class BiliVideoParseAudio:
    """B站视频解析结果-音频文件信息"""
    url: str  # 下载链接
    filename: str  # 文件名
    headers: dict[str, str]  # 请求头

@dataclass
class BiliVideoParseResp:
    """B站视频解析结果"""
    video: BiliVideoParseVideo  # 视频文件信息，如果需要最后的视频文件，可以使用`ffmpeg -i xx.m4a -i xx.m4a xx.mp4`来合成
    audio: BiliVideoParseAudio  # 音频文件信息

@dataclass
class BiliPicParseResp:
    """B站封面解析结果"""
    img_url: str  # 封面地址

@dataclass
class BiliSubtitleDownloadSubtitle:
    """B站字幕下载结果-字幕列表"""
    name: str  # 字幕名称
    url: str  # 字幕下载地址

@dataclass
class BiliSubtitleDownloadResp:
    """B站字幕下载结果"""
    subtitle: list[BiliSubtitleDownloadSubtitle]  # 字幕列表

@dataclass
class BiliDanmuDownloadResp:
    """B站弹幕下载结果"""
    danmu: str  # 弹幕下载地址

@dataclass
class BiliVideoSummaryResp:
    """B站视频总结结果"""
    text: str  # 视频总结信息

@dataclass
class BiliCommentCloudResp:
    """B站评论词云结果"""
    img_url: str  # 词云图片

@dataclass
class NcmToMp3Mp3:
    """ncm转mp3结果-音乐文件信息"""
    url: str  # 播放链接
    cover: str  # 封面链接
    name: str  # 音乐名称
    artist: str  # 音乐作者

@dataclass
class NcmToMp3Resp:
    """ncm转mp3结果"""
    mp3: NcmToMp3Mp3  # 音乐文件信息

@dataclass
class Music163ParseMp3:
    """网易云音乐解析结果-MP3播放信息"""
    url: str  # 播放链接
    cover: str  # 封面链接
    name: str  # 音乐名称
    artist: str  # 音乐作者

@dataclass
class Music163ParseResp:
    """网易云音乐解析结果"""
    mp3: Music163ParseMp3  # MP3播放信息

@dataclass
class XhsPicDownloadResp:
    """小红书图片下载结果"""
    img_list: list[str]  # 解析出的图片列表

@dataclass
class TextCloudGenerateResp:
    """词云生成结果"""
    img_url: str  # 词云图片链接

@dataclass
class DouyinVideoDownloadVideo:
    """抖音视频下载结果-视频下载链接"""
    url: str  # 视频下载链接
    filename: str  # 视频下载链接
    headers: dict[str, str]  # 视频下载链接

@dataclass
class DouyinVideoDownloadResp:
    """抖音视频下载结果"""
    video: DouyinVideoDownloadVideo  # 视频下载链接

@dataclass
class WebContentGetResp:
    """网页内容获取结果"""
    content: str  # 网页内容

@dataclass
class AnimateRecognizeInfo:
    """动漫人脸识别结果-识别信息"""
    img_url: str  # 角色头像链接
    name: str  # 角色名称
    url: str  # 角色百科链接
    conf: int  # 置信度

@dataclass
class AnimateRecognizeResp:
    """动漫人脸识别结果"""
    img: str  # 识别结果
    info: list[AnimateRecognizeInfo]  # 识别信息
