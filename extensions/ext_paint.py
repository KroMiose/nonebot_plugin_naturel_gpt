import uuid

import anyio
import openai
from httpx import AsyncClient
from nonebot import logger
from transformers import GPT2TokenizerFast

from .Extension import Extension

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")


# 拓展的配置信息，用于ai理解拓展的功能 *必填*
ext_config: dict = {
    "name": "paint",  # 拓展名称，用于标识拓展
    "arguments": {
        "content": "str",  # 绘画内容描述
    },
    "description": "paint a picture，使用/#paint&CONTENT#/，其中CONTENT是用逗号分隔的描述性词语。(例如：/#paint&兔子,草地,彩虹#/)",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": ["paint", "画", "图"],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 3,
    # 作者信息
    "author": "OREOREO",
    # 版本
    "version": "0.0.1",
    # 拓展简介
    "intro": "绘图",
    # 可用会话类型 (server即MC服务器 | chat即QQ聊天)
    "available": ["chat"],
}


class CustomExtension(Extension):
    async def call(self, arg_dict: dict, _: dict) -> dict:
        """当拓展被调用时执行的函数 *由拓展自行实现*

        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值(类型为str)}
        """
        custom_config: dict = self.get_custom_config()  # 获取yaml中的配置信息
        cache = custom_config.get("cache", False)
        proxy = custom_config.get("prxoy", None)
        custom_size = custom_config.get("size", "512")
        style = custom_config.get("style", "anime style, colored-pencil")
        cache_path = anyio.Path(custom_config.get("cache_path", "./data/ng_paint"))

        # 从arg_dict中获取参数
        content = arg_dict.get("content", "")

        if proxy:
            if not proxy.startswith("http"):
                proxy = "http://" + proxy
            openai.proxy = proxy

        response = openai.Image.create(
            prompt=content + "," + style, n=1, size=f"{custom_size}x{custom_size}"
        )
        image_url = response["data"][0]["url"]  # type: ignore
        res = response

        if image_url is None:
            return {
                "text": "图片生成错误...",
                "image": None,  # 图片url
                "voice": None,  # 语音url
            }
        if "rejected" in res:
            # 返回的信息将会被发送到会话中
            return {
                "text": "抱歉，这个图违反了ai生成规定，可能是太色了吧",  # 文本信息
                "image": None,  # 图片url
                "voice": None,  # 语音url
            }

        # 创建图片缓存路径
        if not (await cache_path.exists()):
            await cache_path.mkdir(parents=True)
        filename = f"{uuid.uuid4()}.png" if cache else "temp.png"
        image_path = await (cache_path / filename).resolve()

        try:
            async with AsyncClient(proxies=proxy) as cli:
                response = await cli.get(image_url)
            assert response.status_code == 200
        except:
            logger.exception("无法获取图片数据")
            return {
                "text": "下载图片失败",  # 文本信息
                "image": None,  # 图片url
                "voice": None,  # 语音url
            }

        await image_path.write_bytes(response.content)
        logger.info(f"图片已成功保存到 {image_path}")

        # 返回的信息将会被发送到会话中
        return {
            "text": "画好了!",  # 文本信息
            "image": image_path.as_uri(),  # 图片url
            "voice": None,  # 语音url
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
