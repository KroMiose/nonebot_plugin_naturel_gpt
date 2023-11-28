from typing import Union
from .Extension import Extension
import requests

# 扩展的配置信息
ext_config = {
    "name": "draw",
    "arguments": {
        "prompt": "str",
        "size": "str",
    },
    "description": "绘制一副图像，可选尺寸1024x1024，1792x1024，1024x1792，prompt必须为英文，用法:/#draw&prompt&size#/。示例:/#draw&a cute cat&1024x1024#/",
    "refer_word": ["画", "图"],
    "max_call_times_per_msg": 3,
    "author": "微量元素",
    "version": "0.0.1",
    "intro": "调用dall-e-3绘制图像",
}


class CustomExtension(Extension):

    async def call(self, arg_dict: dict, custom_config: dict) -> Union[dict, str]:

        # 获取参数
        prompt = arg_dict.get("prompt")
        size = arg_dict.get("size")

        # 获取配置信息
        custom_config: dict = self.get_custom_config()
        api_key = custom_config.get("key")
        proxy = custom_config.get("proxy", "")
        api_url = custom_config.get("url", "https://api.openai.com/v1/images/generations")

        # 构造请求
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        proxies = {
            "https": proxy
        }
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": size,
        }

        # 发送请求
        response = requests.post(api_url, headers=headers, json=payload, proxies=proxies)

        # 检查响应状态码
        if response.status_code == 200:

            # 返回图片URL
            image_url = response.json()["data"][0]["url"]
            return {
                "text": f"画好了喵~",
                "image": image_url,
            }

        else:
            return {
                "text": f"呜呜呜画不出来喵"
                        f"Error: {response.status_code} {response.text}"
            }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config, custom_config)