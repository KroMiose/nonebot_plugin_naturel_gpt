from typing import Dict, List, Optional

from httpx import AsyncClient
from nonebot import logger
from nonebot_plugin_naturel_gpt.config import config as plugin_config
from pydantic import BaseModel, Field

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
        "Use this extension at the end of response when user wants an anime image (图, 色图, and more). "
        'Typically, you can pass empty tag like "/#get_anime_pic&#/" for a random image. '
        'You can also specify Chinese tags (do not include "#" in tags) '
        'like "/#get_anime_pic&tag1,tag2|tag3#/" (means "tag1" AND ("tag2" OR "tag3")) '
        "to get a specific image."
    ),
    # 参考词，用于上下文参考使用，为空则每次都会被参考 (消耗 token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为 99
    "max_call_times_per_msg": 2,
    # 作者信息
    "author": "student_2333",
    # 版本
    "version": "0.2.0",
    # 扩展简介
    "intro": "更人性化的 Lolicon API 色图扩展，让 AI 可以知道自己发了什么",
    # 调用时是否打断响应 启用后将会在调用后截断后续响应内容
    "interrupt": True,
    # 可用会话类型 (`server` 即 MC服务器 | `chat` 即 QQ聊天)
    "available": ["chat"],
}


class LoliconPicUrls(BaseModel):
    original: str


class LoliconPicData(BaseModel):
    pid: int
    p: int
    uid: int
    title: str
    author: str
    r18: bool
    width: int
    height: int
    tags: List[str]
    ext: str
    ai_type: int = Field(..., alias="aiType")
    upload_date: int = Field(..., alias="uploadDate")
    urls: LoliconPicUrls


class LoliconReturn(BaseModel):
    error: str
    data: List[LoliconPicData]


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
        self.send_manually: bool = config.get("send_manually", False)

        if self.proxy and (not self.proxy.startswith("http")):
            self.proxy = "http://" + self.proxy

    async def call(self, arg_dict: Dict[str, str], _: dict) -> dict:
        tag_str = arg_dict.get("tag", "").strip()

        tags = [x for x in tag_str.split(",") if x] or None
        tag_str = ",".join(tags) if tags else ""

        try:
            async with AsyncClient(proxies=self.proxy) as cli:
                resp = await cli.post(
                    "https://api.lolicon.app/setu/v2",
                    json=dict_del_none(
                        {
                            "tag": tags,
                            "num": 1,
                            "r18": self.r18,
                            "proxy": self.pic_proxy,
                            "excludeAI": self.exclude_ai,
                        },
                    ),
                )
                assert resp.status_code // 100 == 2, resp.text
                data = LoliconReturn(**resp.json())

        except Exception as e:
            logger.exception("获取图片信息失败")
            return {
                "text": f"[LoliconAPI] 搜索失败 ({e!r})",
                "notify": {
                    "sender": "[LoliconAPI]",
                    "msg": (
                        f"Search Failed: {e!r}. "
                        "Please explain this error message to the user."
                    ),
                },
                "wake_up": True,
            }

        if (not data.data) or (not (pic := data.data[0]).title):
            return {
                "text": f"[LoliconAPI] 未找到关于 {tag_str} 的图片",
                "notify": {
                    "sender": "[LoliconAPI]",
                    "msg": (
                        f"No picture found for `{tag_str}`. "
                        "You should remind the user of this message. "
                        "You can also adjust the tag text and search again using this extension."
                    ),
                },
                "wake_up": True,
            }

        user_tip = f"搜索 {tag_str} 完毕" if tag_str else "已获取一张随机图"
        tags_tip = f"\nTags: {', '.join(pic.tags)}" if self.provide_tags else ""

        send_manually = (not plugin_config.ENABLE_MSG_TO_IMG) or self.send_manually
        ai_tip_tail = (
            f'for tag "{tag_str}"' if tag_str else "through your extension call"
        )
        send_tip = "You sent a image via this extension.\n" if send_manually else ""
        output_tip = (
            " "
            if send_manually
            else f' and output this image by using "![{pic.title}]({pic.urls.original})" '
        )

        return {
            "text": f"[LoliconAPI] {user_tip} (PID: {pic.pid})",
            "image": pic.urls.original if send_manually else None,
            "notify": {
                "sender": "[LoliconAPI]",
                "msg": (
                    f"{send_tip}"
                    f"Below is the image information found {ai_tip_tail}. "
                    "This image was posted on Pixiv. "
                    f"You should summary the image information{output_tip}in your response.\n"
                    f"Title: {pic.title} (https://pixiv.net/artworks/{pic.pid})\n"
                    f"Author: {pic.author} (https://www.pixiv.net/users/{pic.uid})"
                    f"{tags_tip}"
                ),
            },
            "wake_up": True,
        }
