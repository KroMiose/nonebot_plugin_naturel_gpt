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
        proxy = custom_config.get("proxy")
        if proxy and (not proxy.startswith("http")):
            proxy = "http://" + proxy

        # 从arg_dict中获取参数
        url_will_read = arg_dict.get("url", None)
        if not url_will_read:
            return {}

        quote = urllib.parse.quote(url_will_read, safe="")
        if (
            quote
            is None
            # or quote == self._last_keyword
            # or time.time() - self._last_call_time < 10
        ):
            return {}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63",
        }
        url = "https://ddg-webapp-search.vercel.app/url_to_text"

        try:
            async with AsyncClient(proxies=proxy) as cli:
                res = (
                    await cli.get(url, headers=headers, params={"url": quote})
                ).json()
            text = res[0]["body"].replace("\n", " ")
            title = res[0]["title"]
        except:
            logger.exception("读取链接失败")
            return {"text": "[ext_readLink] 读取链接失败"}

        translated = False
        try:
            from_ = "auto"
            to_ = "en"
            d = {"data": [text, from_, to_]}
            async with AsyncClient(proxies=proxy) as cli:
                # 翻译成英文
                resp = await cli.post(
                    "https://hf.space/embed/mikeee/gradio-gtr/+/api/predict",
                    json=d,
                    headers=headers,
                )
                assert resp.status_code // 100 == 2, resp.text
                result = resp.json()
            text = result["data"][0]
            translated = True
        except Exception as e:
            logger.error(f"翻译失败，直接将原文传入GPT ({e})")

        # 返回的信息将会被发送到会话中
        if text == "Put something there, man.":
            text = "null"
            title = ""
            translated = False

        title = f"[Title: {title}]\n" if title else ""
        return {
            "text": f"[ext_readLink] 读取: {url_will_read} ...",
            "notify": {
                "sender": "[readLink]",
                "msg": (
                    f"[Content of url {url_will_read} "
                    f"({'The content of the web page has been translated into English. ' if translated else ''}"
                    f"The following information will not be sent directly to chat. Please summarize the content as desired in your reply)]\n"
                    f"{title}{text}"
                ),
            },
            "wake_up": True,  # 是否再次响应
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
        self._last_keyword = None
        self._last_call_time = 0
