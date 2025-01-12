from zyjj_open_sdk.core import OpenClient, OpenAsyncClient, MqttAsyncClient, FileObject, TaskExecute, TaskExecuteAsync, get_input, async_get_input, MqttClient
from typing import Literal, Type
from zyjj_open_sdk.task.tool.entity import *

class Tool:
    def __init__(self, client: OpenClient, mqtt: MqttClient):
        self.__client = client
        self.__mqtt = mqtt

    def bili_video_parse(self, url: str, quality: int) -> TaskExecute[Type[BiliVideoParseResp]]:
        """
        B站视频解析
        :param url: B站视频链接,https://www.bilibili.com/video/BVxxxx
        :param quality: 清晰度,116（1080P60）、80（1080P）、64（720P）、32（480P）、16（360P）
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1014,
            {},
            {'url': url, 'quality': quality},
            BiliVideoParseResp
        )

    def bili_pic_parse(self, url: str) -> TaskExecute[Type[BiliPicParseResp]]:
        """
        B站封面解析
        :param url: B站视频链接,https://www.bilibili.com/video/BVxxxx
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1015,
            {},
            {'url': url},
            BiliPicParseResp
        )

    def bili_subtitle_download(self, url: str) -> TaskExecute[Type[BiliSubtitleDownloadResp]]:
        """
        B站字幕下载
        :param url: B站视频链接,https://www.bilibili.com/video/BVxxxx
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1018,
            {},
            {'url': url},
            BiliSubtitleDownloadResp
        )

    def bili_danmu_download(self, url: str, ext: Literal['xml', 'txt', 'srt', 'json']) -> TaskExecute[Type[BiliDanmuDownloadResp]]:
        """
        B站弹幕下载
        :param url: B站视频链接,https://www.bilibili.com/video/BVxxxx
        :param ext: 弹幕格式,xml（原始）、txt（文本）、srt（字幕）、json（json）
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1028,
            {},
            {'url': url, 'ext': ext},
            BiliDanmuDownloadResp
        )

    def bili_video_summary(self, url: str) -> TaskExecute[Type[BiliVideoSummaryResp]]:
        """
        B站视频总结
        :param url: B站视频链接,https://www.bilibili.com/video/BVxxxx
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1027,
            {},
            {'url': url},
            BiliVideoSummaryResp
        )

    def bili_comment_cloud(self, url: str) -> TaskExecute[Type[BiliCommentCloudResp]]:
        """
        B站评论词云
        :param url: B站视频链接,https://www.bilibili.com/video/BVxxxx
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1029,
            {},
            {'url': url},
            BiliCommentCloudResp
        )

    def ncm_to_mp3(self, ncm: FileObject) -> TaskExecute[Type[NcmToMp3Resp]]:
        """
        ncm转mp3
        :param ncm: ncm文件,网易云音乐下载的ncm文件
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1016,
            {},
            {'ncm': ncm},
            NcmToMp3Resp
        )

    def music_163_parse(self, url: str) -> TaskExecute[Type[Music163ParseResp]]:
        """
        网易云音乐解析
        :param url: 网易云音乐链接,https://music.163.com/#/song?id=xxx
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1020,
            {},
            {'url': url},
            Music163ParseResp
        )

    def xhs_pic_download(self, url: str) -> TaskExecute[Type[XhsPicDownloadResp]]:
        """
        小红书图片下载
        :param url: 小红书链接,https://www.xiaohongshu.com/explore/xxxx
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1019,
            {},
            {'url': url},
            XhsPicDownloadResp
        )

    def text_cloud_generate(self, text: str, refer: FileObject = None) -> TaskExecute[Type[TextCloudGenerateResp]]:
        """
        词云生成
        :param text: 文本信息,
        :param refer: 参考图片,
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1023,
            {},
            {'text': text, 'refer': refer},
            TextCloudGenerateResp
        )

    def douyin_video_download(self, url: str) -> TaskExecute[Type[DouyinVideoDownloadResp]]:
        """
        抖音视频下载
        :param url: 抖音视频链接,点击抖音分享复制链接
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1026,
            {},
            {'url': url},
            DouyinVideoDownloadResp
        )

    def web_content_get(self, url: str) -> TaskExecute[Type[WebContentGetResp]]:
        """
        网页内容获取
        :param url: 网页地址,需要国内可以访问
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1034,
            {},
            {'url': url},
            WebContentGetResp
        )

    def animate_recognize(self, img: FileObject) -> TaskExecute[Type[AnimateRecognizeResp]]:
        """
        动漫人脸识别
        :param img: 动漫图片,带动漫人脸的图片
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1036,
            {},
            {'img': img},
            AnimateRecognizeResp
        )


class AsyncTool:
    def __init__(self, client: OpenAsyncClient, mqtt: MqttAsyncClient):
        self.__client = client
        self.__mqtt = mqtt

    def bili_video_parse(self, url: str, quality: int) -> TaskExecuteAsync[Type[BiliVideoParseResp]]:
        """
        B站视频解析
        :param url: B站视频链接,https://www.bilibili.com/video/BVxxxx
        :param quality: 清晰度,116（1080P60）、80（1080P）、64（720P）、32（480P）、16（360P）
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1014,
            {},
            {'url': url, 'quality': quality},
            BiliVideoParseResp
        )

    def bili_pic_parse(self, url: str) -> TaskExecuteAsync[Type[BiliPicParseResp]]:
        """
        B站封面解析
        :param url: B站视频链接,https://www.bilibili.com/video/BVxxxx
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1015,
            {},
            {'url': url},
            BiliPicParseResp
        )

    def bili_subtitle_download(self, url: str) -> TaskExecuteAsync[Type[BiliSubtitleDownloadResp]]:
        """
        B站字幕下载
        :param url: B站视频链接,https://www.bilibili.com/video/BVxxxx
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1018,
            {},
            {'url': url},
            BiliSubtitleDownloadResp
        )

    def bili_danmu_download(self, url: str, ext: Literal['xml', 'txt', 'srt', 'json']) -> TaskExecuteAsync[Type[BiliDanmuDownloadResp]]:
        """
        B站弹幕下载
        :param url: B站视频链接,https://www.bilibili.com/video/BVxxxx
        :param ext: 弹幕格式,xml（原始）、txt（文本）、srt（字幕）、json（json）
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1028,
            {},
            {'url': url, 'ext': ext},
            BiliDanmuDownloadResp
        )

    def bili_video_summary(self, url: str) -> TaskExecuteAsync[Type[BiliVideoSummaryResp]]:
        """
        B站视频总结
        :param url: B站视频链接,https://www.bilibili.com/video/BVxxxx
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1027,
            {},
            {'url': url},
            BiliVideoSummaryResp
        )

    def bili_comment_cloud(self, url: str) -> TaskExecuteAsync[Type[BiliCommentCloudResp]]:
        """
        B站评论词云
        :param url: B站视频链接,https://www.bilibili.com/video/BVxxxx
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1029,
            {},
            {'url': url},
            BiliCommentCloudResp
        )

    def ncm_to_mp3(self, ncm: FileObject) -> TaskExecuteAsync[Type[NcmToMp3Resp]]:
        """
        ncm转mp3
        :param ncm: ncm文件,网易云音乐下载的ncm文件
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1016,
            {},
            {'ncm': ncm},
            NcmToMp3Resp
        )

    def music_163_parse(self, url: str) -> TaskExecuteAsync[Type[Music163ParseResp]]:
        """
        网易云音乐解析
        :param url: 网易云音乐链接,https://music.163.com/#/song?id=xxx
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1020,
            {},
            {'url': url},
            Music163ParseResp
        )

    def xhs_pic_download(self, url: str) -> TaskExecuteAsync[Type[XhsPicDownloadResp]]:
        """
        小红书图片下载
        :param url: 小红书链接,https://www.xiaohongshu.com/explore/xxxx
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1019,
            {},
            {'url': url},
            XhsPicDownloadResp
        )

    def text_cloud_generate(self, text: str, refer: FileObject = None) -> TaskExecuteAsync[Type[TextCloudGenerateResp]]:
        """
        词云生成
        :param text: 文本信息,
        :param refer: 参考图片,
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1023,
            {},
            {'text': text, 'refer': refer},
            TextCloudGenerateResp
        )

    def douyin_video_download(self, url: str) -> TaskExecuteAsync[Type[DouyinVideoDownloadResp]]:
        """
        抖音视频下载
        :param url: 抖音视频链接,点击抖音分享复制链接
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1026,
            {},
            {'url': url},
            DouyinVideoDownloadResp
        )

    def web_content_get(self, url: str) -> TaskExecuteAsync[Type[WebContentGetResp]]:
        """
        网页内容获取
        :param url: 网页地址,需要国内可以访问
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1034,
            {},
            {'url': url},
            WebContentGetResp
        )

    def animate_recognize(self, img: FileObject) -> TaskExecuteAsync[Type[AnimateRecognizeResp]]:
        """
        动漫人脸识别
        :param img: 动漫图片,带动漫人脸的图片
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1036,
            {},
            {'img': img},
            AnimateRecognizeResp
        )
