class OpenError(Exception):
    """开放平台服务错误"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = str(message)

    def __str__(self):
        return f'错误码：{self.code} 错误信息：{self.message}'

class SDKError(OpenError):
    """sdk本身错误"""
    def __init__(self, msg=''):
        super().__init__(-2, msg)

class RequestError(OpenError):
    """请求错误"""
    def __init__(self, status_code, msg=''):
        super().__init__(status_code, msg)

    def __str__(self):
        return f'请求错误！错误码：{self.code} 错误信息：{self.message}'

class ServerError(OpenError):
    """服务错误"""
    def __init__(self, status_code, msg=''):
        super().__init__(status_code, msg)

    def __str__(self):
        return f'服务错误！错误码：{self.code} 错误信息：{self.message}'