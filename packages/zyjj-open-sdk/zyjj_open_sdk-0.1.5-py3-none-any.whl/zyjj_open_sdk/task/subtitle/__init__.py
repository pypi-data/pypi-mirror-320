from zyjj_open_sdk.core import OpenClient, OpenAsyncClient, MqttAsyncClient, FileObject, TaskExecute, TaskExecuteAsync, get_input, async_get_input, MqttClient
from typing import Literal, Type
from zyjj_open_sdk.task.subtitle.entity import *

class Subtitle:
    def __init__(self, client: OpenClient, mqtt: MqttClient):
        self.__client = client
        self.__mqtt = mqtt

    def subtitle_generate(self, audio: FileObject) -> TaskExecute[Type[SubtitleGenerateResp]]:
        """
        字幕识别（中英文）
        :param audio: 音频文件,支持mp3、wav格式
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1022,
            {},
            {'audio': audio},
            SubtitleGenerateResp
        )

    def subtitle_generate_multilingual(self, audio: FileObject, language: Literal['auto', 'af', 'ar', 'az', 'be', 'bs', 'bg', 'ca', 'zh', 'hr', 'cs', 'da', 'nl', 'en', 'et', 'fi', 'fr', 'gl', 'de', 'el', 'he', 'hi', 'hu', 'is', 'id', 'it', 'ja', 'kn', 'kk', 'ko', 'lv', 'lt', 'mk', 'ms', 'mr', 'mi', 'ne', 'no', 'fa', 'pl', 'pt', 'ro', 'ru', 'sr', 'sk', 'sl', 'es', 'sw', 'sv', 'tl', 'ta', 'th', 'tr', 'uk', 'ur', 'vi', 'cy']) -> TaskExecute[Type[SubtitleGenerateMultilingualResp]]:
        """
        字幕识别（多语种）
        :param audio: 音频文件,支持mp3、wav格式
        :param language: 字幕语言,auto(自动、准确率较低)、af(南非荷兰语)、ar(阿拉伯语)、az(阿塞拜疆语)、be(白俄罗斯语)、bs(波斯尼亚语)、bg(保加利亚语)、ca(加泰罗尼亚语)、zh(中文)、hr(克罗地亚语)、cs(捷克语)、da(丹麦语)、nl(荷兰语)、en(英语)、et(爱沙尼亚语)、fi(芬兰语)、fr(法语)、gl(加利西亚语)、de(德语)、el(希腊语)、he(希伯来语)、hi(印地语)、hu(匈牙利语)、is(冰岛语)、id(印度尼西亚语)、it(意大利语)、ja(日语)、kn(卡纳达语)、kk(哈萨克语)、ko(韩语)、lv(拉脱维亚语)、lt(立陶宛语)、mk(马其顿语)、ms(马来语)、mr(马拉地语)、mi(毛利语)、ne(尼泊尔语)、no(挪威语)、fa(波斯语)、pl(波兰语)、pt(葡萄牙语)、ro(罗马尼亚语)、ru(俄语)、sr(塞尔维亚) 、sk(斯洛伐克语)、sl(斯洛文尼亚语)、es(西班牙语)、sw(斯瓦希里语)、sv(瑞典语)、tl(塔加路语)、ta(泰米尔语)、th(泰语)、tr(土耳其语)、uk(乌克兰语)、ur(乌尔都语)、vi(越南语)、cy(威尔士语)
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1021,
            {},
            {'audio': audio, 'language': language},
            SubtitleGenerateMultilingualResp
        )

    def subtitle_translate(self, subtitle: FileObject, language: Literal['中文', '英语', '日语', '韩语'], mode: int) -> TaskExecute[Type[SubtitleTranslateResp]]:
        """
        字幕翻译
        :param subtitle: 字幕文件,仅支持srt
        :param language: 目标语言,支持中文、英语、日语、韩语
        :param mode: 返回形式,0：双语字幕、1：字幕翻译
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1025,
            {},
            {'subtitle': subtitle, 'language': language, 'mode': mode},
            SubtitleTranslateResp
        )


class AsyncSubtitle:
    def __init__(self, client: OpenAsyncClient, mqtt: MqttAsyncClient):
        self.__client = client
        self.__mqtt = mqtt

    def subtitle_generate(self, audio: FileObject) -> TaskExecuteAsync[Type[SubtitleGenerateResp]]:
        """
        字幕识别（中英文）
        :param audio: 音频文件,支持mp3、wav格式
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1022,
            {},
            {'audio': audio},
            SubtitleGenerateResp
        )

    def subtitle_generate_multilingual(self, audio: FileObject, language: Literal['auto', 'af', 'ar', 'az', 'be', 'bs', 'bg', 'ca', 'zh', 'hr', 'cs', 'da', 'nl', 'en', 'et', 'fi', 'fr', 'gl', 'de', 'el', 'he', 'hi', 'hu', 'is', 'id', 'it', 'ja', 'kn', 'kk', 'ko', 'lv', 'lt', 'mk', 'ms', 'mr', 'mi', 'ne', 'no', 'fa', 'pl', 'pt', 'ro', 'ru', 'sr', 'sk', 'sl', 'es', 'sw', 'sv', 'tl', 'ta', 'th', 'tr', 'uk', 'ur', 'vi', 'cy']) -> TaskExecuteAsync[Type[SubtitleGenerateMultilingualResp]]:
        """
        字幕识别（多语种）
        :param audio: 音频文件,支持mp3、wav格式
        :param language: 字幕语言,auto(自动、准确率较低)、af(南非荷兰语)、ar(阿拉伯语)、az(阿塞拜疆语)、be(白俄罗斯语)、bs(波斯尼亚语)、bg(保加利亚语)、ca(加泰罗尼亚语)、zh(中文)、hr(克罗地亚语)、cs(捷克语)、da(丹麦语)、nl(荷兰语)、en(英语)、et(爱沙尼亚语)、fi(芬兰语)、fr(法语)、gl(加利西亚语)、de(德语)、el(希腊语)、he(希伯来语)、hi(印地语)、hu(匈牙利语)、is(冰岛语)、id(印度尼西亚语)、it(意大利语)、ja(日语)、kn(卡纳达语)、kk(哈萨克语)、ko(韩语)、lv(拉脱维亚语)、lt(立陶宛语)、mk(马其顿语)、ms(马来语)、mr(马拉地语)、mi(毛利语)、ne(尼泊尔语)、no(挪威语)、fa(波斯语)、pl(波兰语)、pt(葡萄牙语)、ro(罗马尼亚语)、ru(俄语)、sr(塞尔维亚) 、sk(斯洛伐克语)、sl(斯洛文尼亚语)、es(西班牙语)、sw(斯瓦希里语)、sv(瑞典语)、tl(塔加路语)、ta(泰米尔语)、th(泰语)、tr(土耳其语)、uk(乌克兰语)、ur(乌尔都语)、vi(越南语)、cy(威尔士语)
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1021,
            {},
            {'audio': audio, 'language': language},
            SubtitleGenerateMultilingualResp
        )

    def subtitle_translate(self, subtitle: FileObject, language: Literal['中文', '英语', '日语', '韩语'], mode: int) -> TaskExecuteAsync[Type[SubtitleTranslateResp]]:
        """
        字幕翻译
        :param subtitle: 字幕文件,仅支持srt
        :param language: 目标语言,支持中文、英语、日语、韩语
        :param mode: 返回形式,0：双语字幕、1：字幕翻译
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1025,
            {},
            {'subtitle': subtitle, 'language': language, 'mode': mode},
            SubtitleTranslateResp
        )
