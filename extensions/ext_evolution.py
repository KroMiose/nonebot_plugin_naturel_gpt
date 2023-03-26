from .Extension import Extension

# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config:dict = {
    "name": "UpdateCharacter",   # 扩展名称，用于标识扩展
    "arguments": {      
        "setting_text": "str",   # 新的预设文本
    },
    # 扩展的描述信息，用于提示ai理解扩展的功能 *必填* 尽量简短 使用英文更节省token
    # 如果bot无法理解扩展的功能，可适当添加使用示例 格式: /#扩展名&参数1&...&参数n#/
    "description": "Use a new character setting to replace the original one. Can be used whenever you want to modify your own character setting (usage in response: /#UpdateCharacter&xxx is a person who ...#/))",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 5,
    # 作者信息
    "author": "KroMiose",
    # 版本
    "version": "0.0.1",
    # 扩展简介
    "intro": "赋予bot成长型人格",
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """ 当扩展被调用时执行的函数 *由扩展自行实现*
        
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息
        
        # 从arg_dict中获取参数
        setting_text = arg_dict["setting_text"]

        if not setting_text:
            raise Exception("缺少参数: setting_text")

        # 返回的信息将会被发送到会话中
        return {
            "text": f"[evolution] 已将人格预设修改为: |\n    {setting_text}",
            "preset": setting_text,
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
