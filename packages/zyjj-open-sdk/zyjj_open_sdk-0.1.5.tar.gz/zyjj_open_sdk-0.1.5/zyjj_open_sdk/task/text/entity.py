from dataclasses import dataclass

@dataclass
class ArticleFrameworkAnalysisResp:
    """文章框架分析结果"""
    text: str  # 分析结果

@dataclass
class ArticleScoringResp:
    """文章打分结果"""
    text: str  # 打分结果

@dataclass
class ArticleEnhanceResp:
    """文章表达优化结果"""
    text: str  # 优化结果

@dataclass
class ArticleTranslateResp:
    """文章翻译结果"""
    text: str  # 翻译结果

@dataclass
class ArticleSummaryResp:
    """文章总结结果"""
    text: str  # 总结结果

@dataclass
class ArticleLayoutResp:
    """文章排版结果"""
    text: str  # 排版结果

@dataclass
class ArticleKeySummaryResp:
    """文章重点总结结果"""
    text: str  # 总结结果

@dataclass
class ArticleRewriteResp:
    """文章改写结果"""
    text: str  # 改写结果

@dataclass
class ArticleExpansionResp:
    """文章扩写结果"""
    text: str  # 扩写结果

@dataclass
class XhsTitleResp:
    """小红书标题生成结果"""
    text: str  # 生成结果

@dataclass
class XhsArtitleResp:
    """小红书文案生成结果"""
    text: str  # 生成结果

@dataclass
class DouyinScriptResp:
    """抖音短视频脚本生成结果"""
    text: str  # 生成的脚本内容

@dataclass
class PoemGenerateResp:
    """诗歌创作结果"""
    text: str  # 创作结果

@dataclass
class NovelGenerateResp:
    """小说生成结果"""
    text: str  # 生成的小说

@dataclass
class MovieReviewGenerateResp:
    """影评生成结果"""
    text: str  # 影评内容

@dataclass
class JokeGenerateResp:
    """段子生成结果"""
    text: str  # 生成的段子

@dataclass
class SloganGenerateResp:
    """slogan生成结果"""
    text: str  # slogan信息

@dataclass
class NovelScienceGenerateResp:
    """科幻小说生成结果"""
    text: str  # 创作结果

@dataclass
class NovelGouxueGenerateResp:
    """狗血软文生成结果"""
    text: str  # 狗血软文内容

@dataclass
class SpeechLeijunGenerateResp:
    """雷军演讲生成结果"""
    text: str  # 演讲的内容
