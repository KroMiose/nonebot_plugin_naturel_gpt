from .Extension import Extension
import requests

# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config:dict = {
    "name": "AnimePic",   # 扩展名称，用于标识扩展
    "arguments": {
        'keyword': 'str',  # 关键字
    },
    "description": "send 1 anime picture by keyword. (usage in response: /#AnimePic&萝莉#/)",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": ["图", "pic", "Pic", "再", "还", "涩", "色", "萝莉", "元"],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 3,
    # 作者信息
    "author": "KroMiose",
    # 版本
    "version": "0.0.1",
    # 扩展简介
    "intro": "Sexnyan二次元图片",
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """ 当扩展被调用时执行的函数 *由扩展自行实现*
        
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值(类型为str)}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息

        keyword = arg_dict.get('keyword', '')

        r18 = custom_config.get('r18', False)

        params = {
            'r18': r18,
            'keyword': keyword,
        }

        url = "https://sex.nyan.xyz/api/v2"

        try:
            res = requests.get(url, params=params, verify=False, timeout=10).json().get("data")

            if not res:
                params['keyword'] = None
                res = requests.get(url, params=params, verify=False, timeout=10).json().get("data")[0]
            else:
                res = res[0]

            img_data = {
                'url': res.get('url'),
                'title': res.get('title'),
                'author': res.get('author'),
            }
            return {
                'text': f"{img_data['title']} by: {img_data['author']}",    # 文本信息
                'image': img_data['url'],   # 图片url
                'voice': None,              # 语音url
            }
        except Exception as e:
            return {
                'text': f"[sexnyan] 找不到关于 {keyword} 的图片",
                'image': None,  # 图片url
                'voice': None,  # 语音url
            }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
