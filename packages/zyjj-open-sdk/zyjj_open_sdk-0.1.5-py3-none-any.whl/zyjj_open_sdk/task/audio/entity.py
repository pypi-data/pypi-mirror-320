from dataclasses import dataclass

@dataclass
class VoiceRecognizeResp:
    """语音识别结果"""
    text: str  # 识别的文字

@dataclass
class VoiceGenerateAzureResp:
    """语音合成（微软）结果"""
    audio_url: str  # 合成的音频连接

@dataclass
class AudioSeparateResp:
    """人声伴奏分离结果"""
    vocals: str  # 人声或者伴奏文件链接
