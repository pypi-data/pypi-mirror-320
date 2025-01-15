class TaskError(Exception):
    """自定义异常类
    
    用于处理任务相关的异常。
    
    :param message: 异常的消息字符串。
    :param data: 可选的附加数据字典。
    """

    def __init__(self, message: str, data: dict | None = None, code: int = None) -> None:
        """
        初始化 TaskError 异常。

        :param message: 异常的消息内容。
        :param data: 可选的附加数据，默认为 None。
        """
        self.message: str = message
        self.data: dict | None = data
        # 防止传入空的code
        if not code:
            self.code = 500
        else:
            self.code = code
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        返回异常的字符串表示形式。

        :return: 异常消息字符串。
        """
        return self.message
class TimeoutError(Exception):
    """自定义超时异常"""
    pass

class ElementNotInViewportError(Exception):
    """自定义元素不在视窗内，需要滚动窗口"""
    pass

class NotImplementError(Exception):
    """尚未实现"""
    pass

class NotSupportError(Exception):
    """不支持"""
    pass

class RequestParameterError(Exception):
    """请求参数错误"""
    pass

class CookieExpiredError(Exception):
    """Cookie过期"""
    pass

class InternalError(Exception):
    pass

class HTTPError(Exception):
    """HTTP请求错误"""

    def __init__(self, code: int, message: str) -> None:
        """
        初始化 HTTPError 异常。

        :param code: HTTP 状态码。
        :param message: 错误消息。
        """
        self.code: int = code
        self.message: str = message
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        返回异常的字符串表示形式。

        :return: 格式化的 HTTP 错误信息字符串。
        """
        return f"HttpCode: {self.code}\nMessage: {self.message}"
    
