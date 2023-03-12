from .Extension import Extension
import requests

# 拓展的配置信息，用于ai理解拓展的功能 *必填*
ext_config:dict = {
    "name": "LoliconPic",   # 拓展名称，用于标识拓展
    "arguments": {      
        "tag": "str",   # 关键字
    },
    "description": "send 1 specified tag anime picture. (usage in response: /#LoliconPic&萝莉#/)",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": ["图", "pic", "Pic", "再", "还", "涩", "色"],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 3,
    # 作者信息
    "author": "CCYellowStar",
    # 版本
    "version": "0.0.1",
    # 拓展简介
    "intro": "发送指定tag二次元图片",
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """ 当拓展被调用时执行的函数 *由拓展自行实现*
        
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值(类型为str)}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息
        r18 = custom_config.get('r18', 0) #添加r18参数 0为否，1为是，2为混合
        tag = arg_dict.get('tag', None)

        url = f"https://api.lolicon.app/setu/v2?tag={tag}&r18={r18}"
        res = requests.get(url, verify=False, timeout=10)
        data=res.json()
        if not data["error"]:
            if data["data"]:
                data = data["data"][0]
                img_src = data["urls"]["original"]
            else:
                return {
                    'text': f"[来自拓展] 没有这个tag的图片...",
                    'image': None,  # 图片url
                    'voice': None,  # 语音url
                }
        if img_src is None:
            return {
                'text': f"[来自拓展] 发送图片错误或超时...",
                'image': None,  # 图片url
                'voice': None,  # 语音url
            }
        else:
            # 返回的信息将会被发送到会话中
            return {
                'text': None,       # 文本信息
                'image': img_src,   # 图片url
                'voice': None,      # 语音url
            }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
