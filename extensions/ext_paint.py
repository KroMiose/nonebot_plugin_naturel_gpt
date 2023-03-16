import openai

from .Extension import Extension

# 拓展的配置信息，用于ai理解拓展的功能 *必填*
ext_config:dict = {
    "name": "paint",   # 拓展名称，用于标识拓展
    "arguments": {
        'style': 'str',  # 绘画风格
        'content': 'str',  # 绘画内容描述
    },
    "description": "paint a picture.",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": ['paint', '画', '图'],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 1,
    # 作者信息
    "author": "OREOREO",
    # 版本
    "version": "0.0.1",
    # 拓展简介
    "intro": "绘图",
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """ 当拓展被调用时执行的函数 *由拓展自行实现*
        
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值(类型为str)}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息
        
        # 从arg_dict中获取参数
        content = arg_dict.get('content', None)
        style = arg_dict.get('style', None)

        if style is None:
            style = ',anime style, colored-pencil'

        response = openai.Image.create(
            prompt= content + ',' + style + ', high detail.',
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        res = response

        if image_url is None:
            return {
                'text': "[ext_paint] 图片生成错误...",
                'image': None,  # 图片url
                'voice': None,  # 语音url
            }
        elif "rejected" in res:
            # 返回的信息将会被发送到会话中
            return {
                'text': "[ext_paint] 抱歉，这个图违反了ai生成规定，可能是太色了吧",       # 文本信息
                'image': None,   # 图片url
                'voice': None,      # 语音url
            }
        else:
            # 返回的信息将会被发送到会话中
            return {
                'text': None,       # 文本信息
                'image': image_url,   # 图片url
                'voice': None,      # 语音url
            }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)