from .Extension import Extension
import requests, random

# 拓展的配置信息，用于ai理解拓展的功能 *必填*
ext_config:dict = {
    "name": "Emoticon",
    "arguments": {
        "keyword": "str",   # 关键字
    },
    "description": "Send a emoticon related to the keyword(in chinese). eg: /#Emoticon&开心#/",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 3,
}

class CustomExtension(Extension):
    async def run(self, arg_dict: dict) -> dict:
        """ 当拓展被调用时执行的函数 *由拓展自行实现*
    
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息

        token = custom_config.get('token', None)
        if token is None:
            return {
                'text': "[ext_emoticon] 请在配置文件中填写alapi访问token"
            }

        keyword = arg_dict.get('keyword', '')
        req_args = {
            'token': custom_config['token'],
            'keyword': str(keyword),
            'page': 1,
            'type': 7,
        }

        url = f"https://v2.alapi.cn/api/doutu"

        try:
            res = requests.get(url, params=req_args, timeout=10).json()
        except Exception as e:
            return {
                'text': f"[ext_emoticon] 访问api时发生错误: {e}"
            }

        if res.get('data') and len(res['data']) > 0:
            # 从返回的data中随机选择一个返回
            return {
                'image': random.choice(res['data'])
            }
        else:
            return {
                'text': f"[ext_emoticon] 未找到与'{keyword}'相关的表情"
            }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)