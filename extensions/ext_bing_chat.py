import time
from typing import Dict, List, Optional, Tuple

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
        "continue": "str", # 是否继续对话
    },
    # 扩展的描述信息，用于提示ai理解扩展的功能 *必填* 尽量简短 使用英文更节省token
    # 如果bot无法理解扩展的功能，可适当添加使用示例 格式: /#扩展名&参数1&...&参数n#/
    "description": "Ask a **specific question** through BingChat online search. (usage in response: /#ask&什么是BingChat?&false#/ Because BingChat is a powful chat AI, you need to ask questions in a chat tone, not just simple search terms. If your question depends on the previous conversation with BingChat, please set `continue` to true. Generally you should ask questions in Chinese)",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 1,
    # 作者信息
    "author": "KroMiose",
    # 版本
    "version": "0.0.2",
    # 扩展简介
    "intro": "使用 BingChat 进行在线查询",
    # 调用时是否打断响应 启用后将会在调用后截断后续响应内容
    "interrupt": True,
}


class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        custom_config: dict = self.get_custom_config()
        proxy = custom_config.get("proxy", None)
        _u = custom_config.get("_u", None)
        res_size = custom_config.get("res_size", 500)
        show_res = custom_config.get("show_res", False)

        if proxy and (not proxy.startswith("http")):
            proxy = "http://" + proxy

        raw_question = arg_dict.get("question", None)
        continue_text = arg_dict.get("continue", False)

        continue_ = True if continue_text and continue_text.lower() == "true" else False

        if continue_ and time.time() - self._last_call_time > 300:
            continue_ = False

        if (
            raw_question is None
            or raw_question == self._last_question
            or time.time() - self._last_call_time < 10
        ):
            return {}

        question = raw_question if continue_ else f"在下面的对话中，请尽可能准确简洁地回答我的问题。不要提供任何无关的信息或回应，也不要问我是否需要帮助。 \n\n我的第一个问题是: {raw_question} (请使用中文回答)"

        try:
            if continue_:
                text, client = await ask_question(_u, question, proxy, self._last_client)
            else:
                text, client = await ask_question(_u, question, proxy)
            text = text[: res_size] + "..." if len(text) > res_size else text
            self._last_client = client
        except Exception as e:
            logger.error(f"BingChat 模块调用失败: {e}")
            if "User needs to solve CAPTCHA to continue" in e:
                return {
                    "text": f"[BingChat] 查询'{raw_question}'时发生错误: 需要处理验证码",
                    "notify": {
                        "sender": "[BingChat API ERROR]",
                        "msg": "Need to solve CAPTCHA to continue, Please contact the manager to solve it."
                    },
                    "image": None,
                    "voice": None,
                }
            else:
                return {
                    "text": f"[BingChat] 查询'{raw_question}'时发生错误",
                    "image": None,
                    "voice": None,
                }
        else:
            self._last_question = raw_question
            self._last_call_time = time.time()
            notify_text = "(The following information will be sent directly to chat.)" if show_res else "(The following information will not be sent directly to chat. Please make a statement based on that information.)"
            return {
                "text": f"[Bing Copilot]> \n<Question>: {raw_question}\n\n<Answer>: {text}" if show_res else None,
                "notify": {
                    "sender": "[BingChat]",
                    "msg": f"[Answer from BingChat (question:{raw_question}) {notify_text})]\n{text}",
                },
                "wake_up": True,
            }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
        self._last_question = None
        self._last_call_time = 0
        self._current_reuse_time = 0
        self._last_client = None


async def ask_question(_u: str, question: str, proxy: Optional[str], client: Optional[BingGPT.Chatbot] = None) -> Tuple[str, BingGPT.Chatbot]:
    if client is None:
        client = BingGPT.Chatbot(
            proxy=proxy,
            cookies=[{"name": "_U", "value": _u}],
        )
    response = await client.ask(question, conversation_style=ConversationStyle.precise)
    return response["item"]["result"]["message"], client
