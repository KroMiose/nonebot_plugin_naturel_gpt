import time
import urllib.parse

from httpx import AsyncClient
from nonebot import logger

from .Extension import Extension

# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config: dict = {
    "name": "readLink",  # 扩展名称，用于标识扩展
    "arguments": {
        "url": "str",  # 关键字
    },
    # 扩展的描述信息，用于提示ai理解扩展的功能 *必填* 尽量简短 使用英文更节省token
    # 如果bot无法理解扩展的功能，可适当添加使用示例 格式: /#扩展名&参数1&...&参数n#/
    "description": "Open the link and read the text and wait for the results. (usage in response: /#readLink&https://www.bilibili.com/#/))",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 5,
    # 作者信息
    "author": "CCYellowStar",
    # 版本
    "version": "0.0.2",
    # 扩展简介
    "intro": "让机器人openai能阅读链接内容",
    # 调用时是否打断响应 启用后将会在调用后截断后续响应内容
    "interrupt": True,
}


class CustomExtension(Extension):
    async def call(self, arg_dict: dict, _: dict) -> dict:
        """当扩展被调用时执行的函数 *由扩展自行实现*

        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        custom_config: dict = self.get_custom_config()  # 获取yaml中的配置信息
        proxy = str(custom_config.get("proxy", ""))
        if proxy and (not proxy.startswith("http")):
            proxy = "http://" + proxy

        # 从arg_dict中获取参数
        url_will_read = arg_dict.get("url", None)
        if url_will_read is None:
            return {}

        quote = urllib.parse.quote(url_will_read, safe="")
        if (
            quote is None
            or quote == self._last_keyword
            or time.time() - self._last_call_time < 10
        ):
            return {}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63"
        }
        url = "https://ddg-webapp-search.vercel.app/url_to_text"

        async with AsyncClient(proxies=proxy) as cli:
            res = (await cli.get(url, headers=headers, params={"url": quote})).json()
        logger.debug(res)

        try:
            data = res
            text = data[0]["body"].replace("\n", " ")
            title = data[0]["title"]
            from_ = "auto"
            to_ = "en"
            d = {"data": [text, from_, to_]}

            async with AsyncClient(proxies=proxy) as cli:
                # 翻译成英文
                result = (
                    await cli.post(
                        "https://hf.space/embed/mikeee/gradio-gtr/+/api/predict", json=d
                    )
                ).json()
            text = result["data"][0]
        except:
            return {
                "text": "[ext_readLink] 读取链接错误",
                "image": None,  # 图片url
                "voice": None,  # 语音url
            }

        # 返回的信息将会被发送到会话中
        if text != "Put something there, man.":
            return {
                "text": f"[ext_readLink] 读取: {url_will_read} ...",
                "notify": {
                    "sender": "[readLink]",
                    "msg": f"[ext_readLink] 读取 {url_will_read} 结果:(To save tokens, the content of the web page has been translated into English)\n{text}\n{title}",
                },
                "wake_up": True,  # 是否再次响应
            }

        return {
            "text": f"[ext_readLink] 读取: {url_will_read} ...",
            "notify": {
                "sender": "[readLink]",
                "msg": f"[ext_readLink] 读取 {url_will_read} 结果: null\n{title}",
            },
            "wake_up": True,  # 是否再次响应
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
        self._last_keyword = None
        self._last_call_time = 0
