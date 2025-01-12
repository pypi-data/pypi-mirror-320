from zyjj_open_sdk.core import OpenClient, OpenAsyncClient, MqttAsyncClient, FileObject, TaskExecute, TaskExecuteAsync, get_input, async_get_input, MqttClient
from typing import Literal, Type
from zyjj_open_sdk.task.audio.entity import *

class Audio:
    def __init__(self, client: OpenClient, mqtt: MqttClient):
        self.__client = client
        self.__mqtt = mqtt

    def voice_recognize(self, audio: FileObject) -> TaskExecute[Type[VoiceRecognizeResp]]:
        """
        语音识别
        :param audio: 音频文件,仅支持中文且时长不超过60s的文件
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1002,
            {},
            {'audio': audio},
            VoiceRecognizeResp
        )

    def voice_generate_azure(self, voice_name: Literal['zh-CN-YunzeNeural', 'zh-CN-XiaoxiaoNeural', 'zh-CN-YunxiNeural', 'zh-CN-YunjianNeural', 'zh-CN-XiaochenNeural', 'zh-CN-XiaoyiNeural', 'zh-CN-YunyangNeural', 'zh-CN-XiaohanNeural', 'zh-CN-XiaomengNeural', 'zh-CN-XiaomoNeural', 'zh-CN-XiaozhenNeural', 'zh-CN-XiaoyouNeural', 'zh-CN-YunfengNeural', 'zh-CN-YunhaoNeural', 'zh-CN-YunxiaNeural', 'zh-CN-YunyeNeural'], text: str) -> TaskExecute[Type[VoiceGenerateAzureResp]]:
        """
        语音合成（微软）
        :param voice_name: 说话人,具体效果可以点效果示意试听。支持：zh-CN-YunzeNeural（云泽）、zh-CN-XiaoxiaoNeural（晓晓）、zh-CN-YunxiNeural（云希）、zh-CN-YunjianNeural（云健）、zh-CN-XiaochenNeural（晓辰）、zh-CN-XiaoyiNeural（晓伊）、zh-CN-YunyangNeural（云扬）、zh-CN-XiaohanNeural（晓涵）、zh-CN-XiaomengNeural（晓梦）、zh-CN-XiaomoNeural（晓墨）、zh-CN-XiaozhenNeural（晓甄）、zh-CN-XiaoyouNeural（晓悠）、zh-CN-YunfengNeural（云枫）、zh-CN-YunhaoNeural（云皓）、zh-CN-YunxiaNeural（云夏）、zh-CN-YunyeNeural（云野）
        :param text: 待合成文本,100字以内
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1004,
            {},
            {'voice_name': voice_name, 'text': text},
            VoiceGenerateAzureResp
        )

    def audio_separate(self, audio: FileObject, option: Literal['vocals', 'no_vocals']) -> TaskExecute[Type[AudioSeparateResp]]:
        """
        人声伴奏分离
        :param audio: 音乐文件,需要有人声和伴奏
        :param option: 需要的内容,vocals（人声），no_vocals（伴奏）
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1030,
            {},
            {'audio': audio, 'option': option},
            AudioSeparateResp
        )


class AsyncAudio:
    def __init__(self, client: OpenAsyncClient, mqtt: MqttAsyncClient):
        self.__client = client
        self.__mqtt = mqtt

    def voice_recognize(self, audio: FileObject) -> TaskExecuteAsync[Type[VoiceRecognizeResp]]:
        """
        语音识别
        :param audio: 音频文件,仅支持中文且时长不超过60s的文件
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1002,
            {},
            {'audio': audio},
            VoiceRecognizeResp
        )

    def voice_generate_azure(self, voice_name: Literal['zh-CN-YunzeNeural', 'zh-CN-XiaoxiaoNeural', 'zh-CN-YunxiNeural', 'zh-CN-YunjianNeural', 'zh-CN-XiaochenNeural', 'zh-CN-XiaoyiNeural', 'zh-CN-YunyangNeural', 'zh-CN-XiaohanNeural', 'zh-CN-XiaomengNeural', 'zh-CN-XiaomoNeural', 'zh-CN-XiaozhenNeural', 'zh-CN-XiaoyouNeural', 'zh-CN-YunfengNeural', 'zh-CN-YunhaoNeural', 'zh-CN-YunxiaNeural', 'zh-CN-YunyeNeural'], text: str) -> TaskExecuteAsync[Type[VoiceGenerateAzureResp]]:
        """
        语音合成（微软）
        :param voice_name: 说话人,具体效果可以点效果示意试听。支持：zh-CN-YunzeNeural（云泽）、zh-CN-XiaoxiaoNeural（晓晓）、zh-CN-YunxiNeural（云希）、zh-CN-YunjianNeural（云健）、zh-CN-XiaochenNeural（晓辰）、zh-CN-XiaoyiNeural（晓伊）、zh-CN-YunyangNeural（云扬）、zh-CN-XiaohanNeural（晓涵）、zh-CN-XiaomengNeural（晓梦）、zh-CN-XiaomoNeural（晓墨）、zh-CN-XiaozhenNeural（晓甄）、zh-CN-XiaoyouNeural（晓悠）、zh-CN-YunfengNeural（云枫）、zh-CN-YunhaoNeural（云皓）、zh-CN-YunxiaNeural（云夏）、zh-CN-YunyeNeural（云野）
        :param text: 待合成文本,100字以内
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1004,
            {},
            {'voice_name': voice_name, 'text': text},
            VoiceGenerateAzureResp
        )

    def audio_separate(self, audio: FileObject, option: Literal['vocals', 'no_vocals']) -> TaskExecuteAsync[Type[AudioSeparateResp]]:
        """
        人声伴奏分离
        :param audio: 音乐文件,需要有人声和伴奏
        :param option: 需要的内容,vocals（人声），no_vocals（伴奏）
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1030,
            {},
            {'audio': audio, 'option': option},
            AudioSeparateResp
        )
