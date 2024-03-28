import time
from typing import Optional

from nonebot import logger

from .Extension import Extension

try:
    from bing_chat import BingGPT
    from bing_chat.conversation_style import ConversationStyle
except ImportError:
    logger.error("BingChat 模块导入失败，请在 Bot 运行环境中使用 `pip install bing-chat` 安装")

# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config: dict = {
    "name": "ask",  # 扩展名称，用于标识扩展
    "arguments": {
        "question": "str",  # 关键字
    },
    # 扩展的描述信息，用于提示ai理解扩展的功能 *必填* 尽量简短 使用英文更节省token
    # 如果bot无法理解扩展的功能，可适当添加使用示例 格式: /#扩展名&参数1&...&参数n#/
    "description": "Ask a **specific question** through BingChat online search. (usage in response: /#ask&什么是BingChat?#/ Because BingChat is a chat AI, you need to ask questions in a chat tone, not just simple search terms. Generally you should ask questions in Chinese)",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 1,
    # 作者信息
    "author": "KroMiose",
    # 版本
    "version": "0.0.1",
    # 扩展简介
    "intro": "使用 BingChat 进行在线查询",
    # 调用时是否打断响应 启用后将会在调用后截断后续响应内容
    "interrupt": True,
}


class CustomExtension(Extension):
    async def call(self, arg_dict: dict, _: dict) -> dict:
        custom_config: dict = self.get_custom_config()
        proxy = custom_config.get("proxy", None)
        _u = custom_config.get("_u", None)
        res_size = custom_config.get("res_size", 1000)
        re_use_time = custom_config.get("re_use_time", 10)

        if proxy and (not proxy.startswith("http")):
            proxy = "http://" + proxy

        raw_question = arg_dict.get("question", None)

        if (
            raw_question is None
            or raw_question == self._last_question
            or time.time() - self._last_call_time < 10
        ):
            return {}

        question = f"在下面的对话中，请尽可能准确简洁地回答我的问题。不要提供任何无关的信息或回应，也不要问我是否需要帮助。 \n\n我的第一个问题是: {raw_question} (请使用中文回答)"

        try:
            text = await ask_question(_u, question, proxy)
            text = text[: res_size] + "..." if len(text) > res_size else text
        except Exception:
            return {
                "text": f"[BingChat] 未找到关于 '{raw_question}' 的信息或请求发生错误",
                "image": None,
                "voice": None,
            }
        else:
            self._last_question = raw_question
            self._last_call_time = time.time()
            return {
                "text": f"[BingChat] 搜索: {raw_question} [完成]",
                "notify": {
                    "sender": "[BingChat]",
                    "msg": f"[Question answer from BingChat (question:{raw_question}) (The following information will not be sent directly to chat. Please make a statement based on that information.y)]\n{text}",
                },
                "wake_up": True,
            }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
        self._last_question = None
        self._last_call_time = 0
        self._current_reuse_time = 0


async def ask_question(_u: str, question: str, proxy: Optional[str]) -> str:
    c = BingGPT.Chatbot(
        proxy=proxy,
        cookies=[{"name": "_U", "value": _u}],
    )
    response = await c.ask(question, conversation_style=ConversationStyle.precise)
    return response["item"]["result"]["message"]
