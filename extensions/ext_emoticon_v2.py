from httpx import AsyncClient

from .Extension import Extension

ext_config: dict = {
    "name": "EmoticPic",
    "arguments": {
        "name": "str",
    },
    "description": "send 1 specified name emotic picture. (usage in response:)",
    "refer_word": ["图", "pic", "Pic", "再", "还"],
    "max_call_times_per_msg": 3,
    "author": "白羽",
    "version": "0.0.1",
    "intro": "发送指定名称表情包",
    "available": ["chat"],
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, _: dict) -> dict:
        name = arg_dict.get("name", None)
        url = f"http://111.230.15.231/emotic/readEmotic?name={name}&page=1&limit=1"

        async with AsyncClient() as cli:
            data = (await cli.get(url)).json()

        img_src = None
        if data["count"] > 0:
            img_src = data["list"][0]["url"]
        else:
            return {
                "text": "[来自扩展] 没有找到这个名称的表情包...",
                "image": None,
                "voice": None,
            }

        if img_src is None:
            return {
                "text": "[来自扩展] 发送表情包错误或超时...",
                "image": None,
                "voice": None,
            }

        return {
            "text": None,
            "image": img_src,
            "voice": None,
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
