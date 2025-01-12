from zyjj_open_sdk.core import OpenClient, OpenAsyncClient, MqttAsyncClient, FileObject, TaskExecute, TaskExecuteAsync, get_input, async_get_input, MqttClient
from typing import Literal, Type
from zyjj_open_sdk.task.text.entity import *

class Text:
    def __init__(self, client: OpenClient, mqtt: MqttClient):
        self.__client = client
        self.__mqtt = mqtt

    def article_framework_analysis(self, user: str) -> TaskExecute[Type[ArticleFrameworkAnalysisResp]]:
        """
        文章框架分析
        :param user: 文章内容,1w字以内
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efcabd65cbfec06ccd72f8'},
            {'user': user},
            ArticleFrameworkAnalysisResp
        )

    def article_scoring(self, user: str) -> TaskExecute[Type[ArticleScoringResp]]:
        """
        文章打分
        :param user: 文章内容,1w字以内
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efd09065cbfec06ccd7303'},
            {'user': user},
            ArticleScoringResp
        )

    def article_enhance(self, user: str) -> TaskExecute[Type[ArticleEnhanceResp]]:
        """
        文章表达优化
        :param user: 文章内容,1w字以内
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efcb7565cbfec06ccd72fb'},
            {'user': user},
            ArticleEnhanceResp
        )

    def article_translate(self, user: str, language: Literal['中文', '英语', '日语', '韩语']) -> TaskExecute[Type[ArticleTranslateResp]]:
        """
        文章翻译
        :param user: 原文,1w字以内
        :param language: 翻译语言,中文、英语、日语、韩语
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '676c28f55fc393c74bbe67c6'},
            {'user': user, 'data.language': language},
            ArticleTranslateResp
        )

    def article_summary(self, user: str) -> TaskExecute[Type[ArticleSummaryResp]]:
        """
        文章总结
        :param user: 文章内容,1w字以内
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efc90965cbfec06ccd72f3'},
            {'user': user},
            ArticleSummaryResp
        )

    def article_layout(self, user: str) -> TaskExecute[Type[ArticleLayoutResp]]:
        """
        文章排版
        :param user: 文章内容,1w字以内
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efd10f5d98650e8adb1ff1'},
            {'user': user},
            ArticleLayoutResp
        )

    def article_key_summary(self, user: str) -> TaskExecute[Type[ArticleKeySummaryResp]]:
        """
        文章重点总结
        :param user: 文章内容,1w字以内
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efc9df5d98650e8adb1fe5'},
            {'user': user},
            ArticleKeySummaryResp
        )

    def article_rewrite(self, user: str, style: str) -> TaskExecute[Type[ArticleRewriteResp]]:
        """
        文章改写
        :param user: 文章内容,1w字以内
        :param style: 改写风格,详细说明你希望改写的风格要求
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '676cae995fc393c74bbe67eb'},
            {'user': user, 'data.style': style},
            ArticleRewriteResp
        )

    def article_expansion(self, user: str, num: str) -> TaskExecute[Type[ArticleExpansionResp]]:
        """
        文章扩写
        :param user: 文章内容,2千字以内
        :param num: 文章字数要求,希望扩写多少字，不一定准确
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '676ce4355fc393c74bbe6806'},
            {'user': user, 'data.num': num},
            ArticleExpansionResp
        )

    def xhs_title(self, user: str) -> TaskExecute[Type[XhsTitleResp]]:
        """
        小红书标题生成
        :param user: 文章的主要信息,比如：一款口红，特点是很可爱
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efc9a85d98650e8adb1fe4'},
            {'user': user},
            XhsTitleResp
        )

    def xhs_artitle(self, user: str) -> TaskExecute[Type[XhsArtitleResp]]:
        """
        小红书文案生成
        :param user: 文章主题信息,比如 杭州西湖
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efc8a765cbfec06ccd72f1'},
            {'user': user},
            XhsArtitleResp
        )

    def douyin_script(self, user: str) -> TaskExecute[Type[DouyinScriptResp]]:
        """
        抖音短视频脚本生成
        :param user: 视频主题信息,比如 如何赚钱
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efc95d5d98650e8adb1fe3'},
            {'user': user},
            DouyinScriptResp
        )

    def poem_generate(self, user: str, style: Literal['现代诗', '七言律诗', '五言律诗'] = None) -> TaskExecute[Type[PoemGenerateResp]]:
        """
        诗歌创作
        :param user: 诗歌主题,比如：51周末还要加班非常累，希望可以早点下班
        :param style: 诗歌风格,现代诗、七言律诗、五言律诗
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '676d65329cb619e427ea28f7'},
            {'user': user, 'data.style': style},
            PoemGenerateResp
        )

    def novel_generate(self, user: str) -> TaskExecute[Type[NovelGenerateResp]]:
        """
        小说生成
        :param user: 故事背景,包括时间、地点、人物等信息，越详细越好
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efcf8c5d98650e8adb1ff0'},
            {'user': user},
            NovelGenerateResp
        )

    def movie_review_generate(self, user: str) -> TaskExecute[Type[MovieReviewGenerateResp]]:
        """
        影评生成
        :param user: 电影名称,电影作品名称和创作要求
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efca8965cbfec06ccd72f7'},
            {'user': user},
            MovieReviewGenerateResp
        )

    def joke_generate(self, user: str) -> TaskExecute[Type[JokeGenerateResp]]:
        """
        段子生成
        :param user: 场景的描述信息,
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efd0c965cbfec06ccd7304'},
            {'user': user},
            JokeGenerateResp
        )

    def slogan_generate(self, user: str) -> TaskExecute[Type[SloganGenerateResp]]:
        """
        slogan生成
        :param user: 产品的特点,详细描述一下产品的特点信息
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efd05565cbfec06ccd7302'},
            {'user': user},
            SloganGenerateResp
        )

    def novel_science_generate(self, user: str) -> TaskExecute[Type[NovelScienceGenerateResp]]:
        """
        科幻小说生成
        :param user: 设定信息,详细描述音效科幻小说的设定
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efcfcc65cbfec06ccd7300'},
            {'user': user},
            NovelScienceGenerateResp
        )

    def novel_gouxue_generate(self, user: str) -> TaskExecute[Type[NovelGouxueGenerateResp]]:
        """
        狗血软文生成
        :param user: 背景信息,详细描述一下故事的背景信息
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efcaef5d98650e8adb1fec'},
            {'user': user},
            NovelGouxueGenerateResp
        )

    def speech_leijun_generate(self, user: str) -> TaskExecute[Type[SpeechLeijunGenerateResp]]:
        """
        雷军演讲生成
        :param user: 演讲主题,演讲的主题内容
        :return: 可执行对象
        """
        return TaskExecute(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efd01865cbfec06ccd7301'},
            {'user': user},
            SpeechLeijunGenerateResp
        )


class AsyncText:
    def __init__(self, client: OpenAsyncClient, mqtt: MqttAsyncClient):
        self.__client = client
        self.__mqtt = mqtt

    def article_framework_analysis(self, user: str) -> TaskExecuteAsync[Type[ArticleFrameworkAnalysisResp]]:
        """
        文章框架分析
        :param user: 文章内容,1w字以内
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efcabd65cbfec06ccd72f8'},
            {'user': user},
            ArticleFrameworkAnalysisResp
        )

    def article_scoring(self, user: str) -> TaskExecuteAsync[Type[ArticleScoringResp]]:
        """
        文章打分
        :param user: 文章内容,1w字以内
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efd09065cbfec06ccd7303'},
            {'user': user},
            ArticleScoringResp
        )

    def article_enhance(self, user: str) -> TaskExecuteAsync[Type[ArticleEnhanceResp]]:
        """
        文章表达优化
        :param user: 文章内容,1w字以内
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efcb7565cbfec06ccd72fb'},
            {'user': user},
            ArticleEnhanceResp
        )

    def article_translate(self, user: str, language: Literal['中文', '英语', '日语', '韩语']) -> TaskExecuteAsync[Type[ArticleTranslateResp]]:
        """
        文章翻译
        :param user: 原文,1w字以内
        :param language: 翻译语言,中文、英语、日语、韩语
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '676c28f55fc393c74bbe67c6'},
            {'user': user, 'data.language': language},
            ArticleTranslateResp
        )

    def article_summary(self, user: str) -> TaskExecuteAsync[Type[ArticleSummaryResp]]:
        """
        文章总结
        :param user: 文章内容,1w字以内
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efc90965cbfec06ccd72f3'},
            {'user': user},
            ArticleSummaryResp
        )

    def article_layout(self, user: str) -> TaskExecuteAsync[Type[ArticleLayoutResp]]:
        """
        文章排版
        :param user: 文章内容,1w字以内
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efd10f5d98650e8adb1ff1'},
            {'user': user},
            ArticleLayoutResp
        )

    def article_key_summary(self, user: str) -> TaskExecuteAsync[Type[ArticleKeySummaryResp]]:
        """
        文章重点总结
        :param user: 文章内容,1w字以内
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efc9df5d98650e8adb1fe5'},
            {'user': user},
            ArticleKeySummaryResp
        )

    def article_rewrite(self, user: str, style: str) -> TaskExecuteAsync[Type[ArticleRewriteResp]]:
        """
        文章改写
        :param user: 文章内容,1w字以内
        :param style: 改写风格,详细说明你希望改写的风格要求
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '676cae995fc393c74bbe67eb'},
            {'user': user, 'data.style': style},
            ArticleRewriteResp
        )

    def article_expansion(self, user: str, num: str) -> TaskExecuteAsync[Type[ArticleExpansionResp]]:
        """
        文章扩写
        :param user: 文章内容,2千字以内
        :param num: 文章字数要求,希望扩写多少字，不一定准确
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '676ce4355fc393c74bbe6806'},
            {'user': user, 'data.num': num},
            ArticleExpansionResp
        )

    def xhs_title(self, user: str) -> TaskExecuteAsync[Type[XhsTitleResp]]:
        """
        小红书标题生成
        :param user: 文章的主要信息,比如：一款口红，特点是很可爱
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efc9a85d98650e8adb1fe4'},
            {'user': user},
            XhsTitleResp
        )

    def xhs_artitle(self, user: str) -> TaskExecuteAsync[Type[XhsArtitleResp]]:
        """
        小红书文案生成
        :param user: 文章主题信息,比如 杭州西湖
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efc8a765cbfec06ccd72f1'},
            {'user': user},
            XhsArtitleResp
        )

    def douyin_script(self, user: str) -> TaskExecuteAsync[Type[DouyinScriptResp]]:
        """
        抖音短视频脚本生成
        :param user: 视频主题信息,比如 如何赚钱
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efc95d5d98650e8adb1fe3'},
            {'user': user},
            DouyinScriptResp
        )

    def poem_generate(self, user: str, style: Literal['现代诗', '七言律诗', '五言律诗'] = None) -> TaskExecuteAsync[Type[PoemGenerateResp]]:
        """
        诗歌创作
        :param user: 诗歌主题,比如：51周末还要加班非常累，希望可以早点下班
        :param style: 诗歌风格,现代诗、七言律诗、五言律诗
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '676d65329cb619e427ea28f7'},
            {'user': user, 'data.style': style},
            PoemGenerateResp
        )

    def novel_generate(self, user: str) -> TaskExecuteAsync[Type[NovelGenerateResp]]:
        """
        小说生成
        :param user: 故事背景,包括时间、地点、人物等信息，越详细越好
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efcf8c5d98650e8adb1ff0'},
            {'user': user},
            NovelGenerateResp
        )

    def movie_review_generate(self, user: str) -> TaskExecuteAsync[Type[MovieReviewGenerateResp]]:
        """
        影评生成
        :param user: 电影名称,电影作品名称和创作要求
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efca8965cbfec06ccd72f7'},
            {'user': user},
            MovieReviewGenerateResp
        )

    def joke_generate(self, user: str) -> TaskExecuteAsync[Type[JokeGenerateResp]]:
        """
        段子生成
        :param user: 场景的描述信息,
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efd0c965cbfec06ccd7304'},
            {'user': user},
            JokeGenerateResp
        )

    def slogan_generate(self, user: str) -> TaskExecuteAsync[Type[SloganGenerateResp]]:
        """
        slogan生成
        :param user: 产品的特点,详细描述一下产品的特点信息
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efd05565cbfec06ccd7302'},
            {'user': user},
            SloganGenerateResp
        )

    def novel_science_generate(self, user: str) -> TaskExecuteAsync[Type[NovelScienceGenerateResp]]:
        """
        科幻小说生成
        :param user: 设定信息,详细描述音效科幻小说的设定
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efcfcc65cbfec06ccd7300'},
            {'user': user},
            NovelScienceGenerateResp
        )

    def novel_gouxue_generate(self, user: str) -> TaskExecuteAsync[Type[NovelGouxueGenerateResp]]:
        """
        狗血软文生成
        :param user: 背景信息,详细描述一下故事的背景信息
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efcaef5d98650e8adb1fec'},
            {'user': user},
            NovelGouxueGenerateResp
        )

    def speech_leijun_generate(self, user: str) -> TaskExecuteAsync[Type[SpeechLeijunGenerateResp]]:
        """
        雷军演讲生成
        :param user: 演讲主题,演讲的主题内容
        :return: 可执行对象
        """
        return TaskExecuteAsync(
            self.__client,
            self.__mqtt,
            1001,
            {'system': '66efd01865cbfec06ccd7301'},
            {'user': user},
            SpeechLeijunGenerateResp
        )
