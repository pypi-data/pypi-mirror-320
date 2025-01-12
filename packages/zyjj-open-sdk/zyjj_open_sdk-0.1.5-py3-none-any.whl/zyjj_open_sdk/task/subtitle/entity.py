from dataclasses import dataclass

@dataclass
class SubtitleGenerateResp:
    """字幕识别（中英文）结果"""
    subtitle: str  # 字幕链接

@dataclass
class SubtitleGenerateMultilingualResp:
    """字幕识别（多语种）结果"""
    subtitle: str  # 字幕链接

@dataclass
class SubtitleTranslateResp:
    """字幕翻译结果"""
    translated: str  # 翻译好的字幕链接
