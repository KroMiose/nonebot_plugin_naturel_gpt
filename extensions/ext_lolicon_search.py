from typing import Dict, Optional

from httpx import AsyncClient
from nonebot import logger

from .Extension import Extension

# 扩展的配置信息，用于 AI 理解扩展的功能
ext_config = {
    # 扩展名称，用于标识扩展，尽量简短
    "name": "get_anime_pic",
    # 填写期望的参数类型，尽量使用简单类型，便于 AI 理解含义使用
    # 注意：实际接收到的参数类型为 str (由 AI 生成)，需要自行转换
    "arguments": {
        "tag": "str",
    },
    # 扩展的描述信息，用于提示 AI 理解扩展的功能，尽量简短
    # 使用英文更节省 token，添加使用示例可提高 bot 调用的准确度
    "description": (
        "Get an anime image information using Lolicon API. "
        "Use this extension when user wants you to get an anime picture (色图, 涩图, and so on). "
        'For example, You can get a random image by using "/#get_anime_pic&#/" in your response; '
        'Or you can get a image with keywords ("可爱") AND ("白丝" OR "黑丝") '
        'by using "/#get_anime_pic&可爱,白丝|黑丝#/".'
    ),
    # 参考词，用于上下文参考使用，为空则每次都会被参考 (消耗 token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为 99
    "max_call_times_per_msg": 2,
    # 作者信息
    "author": "student_2333",
    # 版本
    "version": "0.1.0",
    # 扩展简介
    "intro": "让 Bot 能够使用 LoliconAPI 搜索并获取图片信息，并让 Bot 使用 Markdown 格式发出",
    # 调用时是否打断响应 启用后将会在调用后截断后续响应内容
    "interrupt": True,
    # 可用会话类型 (`server` 即 MC服务器 | `chat` 即 QQ聊天)
    "available": ["chat"],
}


def dict_del_none(will_del: dict) -> dict:
    return {k: v for k, v in will_del.items() if v is not None}


class CustomExtension(Extension):
    def __init__(self, custom_config):
        super().__init__(ext_config.copy(), custom_config)

        config = self.get_custom_config()  # 获取yaml中的配置信息
        self.proxy: Optional[str] = config.get("proxy")
        self.r18: int = config.get("r18", 0)
        self.pic_proxy: Optional[str] = config.get("pic_proxy")
        self.exclude_ai: bool = config.get("exclude_ai", False)
        self.provide_tags: bool = config.get("provide_tags", True)

        if self.proxy and (not self.proxy.startswith("http")):
            self.proxy = "http://" + self.proxy

    async def call(self, arg_dict: Dict[str, str], _: dict) -> dict:
        tag = [x for x in arg_dict.get("tag", "").split(",") if x] or None
        tag_str = ",".join(tag) if tag else ""

        try:
            async with AsyncClient(proxies=self.proxy) as cli:
                resp = await cli.post(
                    "https://api.lolicon.app/setu/v2",
                    json=dict_del_none(
                        {
                            "tag": tag,
                            "num": 1,
                            "r18": self.r18,
                            "proxy": self.pic_proxy,
                            "excludeAI": self.exclude_ai,
                        },
                    ),
                )
                assert resp.status_code // 100 == 2, resp.text
                data: dict = resp.json()

        except Exception as e:
            logger.exception("获取图片信息失败")
            return {
                "text": f"[Lolicon Search] 搜索失败 ({e!r})",
                "notify": {
                    "sender": "[Lolicon Search]",
                    "msg": (
                        f"Search Failed: {e!r}. "
                        "Please explain this error message to the user."
                    ),
                },
                "wake_up": True,
            }

        pic_list: Optional[list] = data.get("data")
        if (not pic_list) or (not isinstance(pic_list, list)):
            return {
                "text": f"[Lolicon Search] 未找到关于 {tag_str} 的图片",
                "notify": {
                    "sender": "[Lolicon Search]",
                    "msg": (
                        f"No picture found for `{tag_str}`. "
                        "You should remind the user of this message. "
                        "You can also adjust the tag text and search again using this extension."
                    ),
                },
                "wake_up": True,
            }

        pic_data = pic_list[0]
        tip = f"搜索 {tag_str} 完毕" if tag_str else "已获取一张随机图"
        tags = f"\nTags: {', '.join(pic_data['tags'])}" if self.provide_tags else ""
        return {
            "text": f"[Lolicon Search] {tip} (PID: {pic_data['pid']})",
            "notify": {
                "sender": "[Lolicon Search]",
                "msg": (
                    "[This is the image information found through your extension call. "
                    "This image was posted on Pixiv. "
                    "This image will NOT BE AUTOMATICALLY SENT to the chat, "
                    "you MUST MANUALLY SEND this image out in your response USING MARKDOWN FORMAT "
                    '("![Image Title](Image URL)")!'
                    'DO NOT use any other extensions like "#readLink&url#" in your response this time.]\n'
                    f"URL: {pic_data['urls']['original']}\n"
                    f"Title: {pic_data['title']} (PID: {pic_data['pid']})\n"
                    f"Author: {pic_data['author']} (UID: {pic_data['uid']})"
                    f"{tags}"
                ),
            },
            "wake_up": True,
        }
