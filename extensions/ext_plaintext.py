from typing import List, cast
from nonebot_plugin_naturel_gpt.config import config as plugin_config

from .Extension import Extension

# 扩展的配置信息，用于 AI 理解扩展的功能
ext_config = {
    # 扩展名称，用于标识扩展，尽量简短
    "name": "send_plaintext",
    # 填写期望的参数类型，尽量使用简单类型，便于 AI 理解含义使用
    # 注意：实际接收到的参数类型为 str (由 AI 生成)，需要自行转换
    "arguments": {"msg": "str"},
    # 扩展的描述信息，用于提示 AI 理解扩展的功能，尽量简短
    # 使用英文更节省 token，添加使用示例可提高 bot 调用的准确度
    "description": (
        "Send message directly to the chat. "
        "As your response will be converted into an image and sent out, "
        "this extension allows you to send messages that users can interact (e.g. copy, visit url). "
        'e.g. "/#send_plaintext&google.com#/" (singleline); "/#send_plaintext&print("1")\nprint("2")#/" (multiline) .'
    ),
    # 参考词，用于上下文参考使用，为空则每次都会被参考 (消耗 token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为 99
    "max_call_times_per_msg": 99,
    # 作者信息
    "author": "student_2333",
    # 版本
    "version": "0.1.0",
    # 扩展简介
    "intro": "让回复转图的Bot拥有直接发送文本消息的能力",
    # 调用时是否打断响应 启用后将会在调用后截断后续响应内容
    "interrupt": False,
    # 可用会话类型 (`server` 即 MC服务器 | `chat` 即 QQ聊天)
    "available": ["chat"],
}


def escape_line_break(string: str) -> str:
    buffer = []

    next_escape = False
    for char in string:
        if char == "\\":
            next_escape = True
        elif next_escape:
            buffer.append("\n" if char == "n" else f"\\{char}")
        else:
            buffer.append(char)

    return "".join(buffer)


class CustomExtension(Extension):
    def __init__(self, custom_config: dict):
        if not plugin_config.ENABLE_MSG_TO_IMG:
            raise RuntimeError("本扩展仅适用于启用回复转图的 Bot，没启用回复转图请不要安装本扩展")

        super().__init__(ext_config.copy(), custom_config)
        self.black_words = [
            x.lower() for x in cast(List[str], custom_config.get("black_words", []))
        ]

    async def call(self, arg_dict: dict, _: dict) -> dict:
        msg = arg_dict.get("msg")
        if not msg:
            return {}

        for bw in self.black_words:
            if bw in msg:
                return {
                    "notify": {
                        "sender": "system",
                        "msg": (
                            f'[SendPlaintext]\nYou cannot send "{bw}" directly! '
                            "Please reconsider the content you want to send."
                        ),
                    },
                    "wake_up": True,
                }

        return {"text": escape_line_break(msg)}
