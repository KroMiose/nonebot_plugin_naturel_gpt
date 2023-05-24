from typing import Union
from .Extension import Extension
import random

# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config: dict = {
    "name": "Random",  # 扩展名称，用于标识扩展
    "arguments": {
        "min": "int",  # 填写希望的参数类型，尽量使用简单类型，便于ai理解含义使用
        "max": "int",  # 注意：实际接收到的参数类型为str(由ai生成)，需要自行转换
    },
    # 扩展的描述信息，用于提示ai理解扩展的功能 *必填* 尽量简短 使用英文更节省token
    # 如果bot无法理解扩展的功能，可适当添加使用示例 格式: /#扩展名&参数1&...&参数n#/
    "description": "send a random number beteen the range. (usage in response: /#Random&0&20#/))",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 5,
    # 作者信息
    "author": "KroMiose",
    # 版本
    "version": "0.0.1",
    # 扩展简介
    "intro": "随机数生成模块",
}


class CustomExtension(Extension):
    async def call(self, arg_dict: dict, _: dict) -> Union[dict, str]:
        """当扩展被调用时执行的函数 *由扩展自行实现*

        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        # custom_config: dict = self.get_custom_config()  # 获取yaml中的配置信息
        # 随机数生成器例子
        min_num = arg_dict.get("min", 0)
        max_num = arg_dict.get("max", 100)

        try:
            min_num = int(min_num)
            max_num = int(max_num)
        except ValueError:
            return "参数错误，参数必须是整数"

        if min_num > max_num:
            min_num, max_num = max_num, min_num

        # 返回的信息将会被发送到会话中
        return {
            "text": f"[来自扩展]你要的数字是: {random.randint(min_num, max_num)} ^_^",
            "image": None,  # 图片url
            "voice": None,  # 语音url
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
