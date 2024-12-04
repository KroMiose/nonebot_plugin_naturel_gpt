from typing import Union
from .Extension import Extension
import requests
import re

# 扩展的配置信息
ext_config = {
    # 扩展名称，用于标识扩展，尽量简短
    "name": "analyzeimage",
    "arguments": {
        "url": "str",
    },
    # 扩展的描述信息，用于提示 AI 理解扩展的功能，尽量简短
    # 使用英文更节省 token，添加使用示例可提高 bot 调用的准确度
    "description": "analyze image content and provide relevant feedback. (Usage: /#analyzeimage&url#/). Example: /#analyzeimage&https://gchat.qpic.cn/download?...#/.",
    # 参考词，用于上下文参考使用，为空则每次都会被参考 (消耗 token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为 99
    "max_call_times_per_msg": 1,
    "author": "Bear_lele",
    "version": "1.0.0",
    # 扩展简介
    "intro": "调用AI分析图像",
}

# 配置项（例子）：
# apiKey: sk-abc12*****
# apiUrl: https://oneapi.xxx.com/v1/chat/completions
# model: gpt-4o-mini

class CustomExtension(Extension):

    async def call(self, arg_dict: dict, custom_config: dict) -> Union[dict, str]:

        #获取图片url
        url = arg_dict.get("url").replace("~", "&")

        # 使用正则表达式匹配 URL
        url_pattern = r"https?://[^\s]+"
        url_match = re.search(url_pattern, url)

        if url_match:
            # 提取 URL
            url = url_match.group(0)
            
            # 去除 URL 后的文本部分
            text = url.replace(url, "")
            
        # 获取配置信息
        custom_config: dict = self.get_custom_config()
        api_key = custom_config.get("apiKey")
        api_url = custom_config.get("apiUrl")
        model = custom_config.get("model")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": model,
            "messages": [
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": "What’s in this image?"
                    },
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": url
                    }
                    }
                ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post(api_url, headers=headers, json=payload)
        # print(f"[analyzeimage] {response.json()}")
        content = response.json()['choices'][0]['message']['content']

        return {
            "notify": {
                "sender": "[analyzeimage]",
                "msg": f"[Image Description]\n{content}",
            },
            "wake_up": True,
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config, custom_config)