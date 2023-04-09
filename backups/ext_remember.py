from .Extension import Extension


# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config:dict = {
    "name": "remember",   # 扩展名称，用于标识扩展
    "arguments": {
        'key': 'str',   # 记忆的键
        'value': 'str', # 记忆的值
    },
    "description": "Set the memory according to the key and value. (usage in response: /#remember&topic&we are talking about ...#/)))",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 5,
    # 作者信息
    "author": "KroMiose",
    # 版本
    "version": "0.0.1",
    # 扩展简介
    "intro": "主动记忆模块",
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """ 当扩展被调用时执行的函数 *由扩展自行实现*
        
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值(类型为str)}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息

        # 从arg_dict中获取参数
        key = arg_dict.get('key', None)
        value = arg_dict.get('value', None)
        if key is None:
            raise ValueError('记忆的键不能为空')

        return {
            'memory': {'key': key, 'value': value},
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
