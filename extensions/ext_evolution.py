from .Extension import Extension

# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config:dict = {
    "name": "UpdateCharacter",   # 扩展名称，用于标识扩展
    "arguments": {
        "origin_text": "str",   # 原始预设文本
        "new_text": "str",      # 新的预设文本
    },
    # 扩展的描述信息，用于提示ai理解扩展的功能 *必填* 尽量简短 使用英文更节省token
    # 如果bot无法理解扩展的功能，可适当添加使用示例 格式: /#扩展名&参数1&...&参数n#/
    "description": "Replaces the original character setting snippet(*strict match*) with a new one. If you want to add new character setting, please set origin_text to \"[empty]\". Can be used whenever you want to modify your own character setting (usage in response: /#UpdateCharacter&I love A&I love B#/))",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 5,
    # 作者信息
    "author": "KroMiose",
    # 版本
    "version": "0.0.2",
    # 扩展简介
    "intro": "赋予bot变化型人格",
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """ 当扩展被调用时执行的函数 *由扩展自行实现*
        
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息

        # 从custom_config中获取参数
        notify_type = custom_config.get("notify_type", 1)
        
        # 从arg_dict中获取参数
        origin_text = arg_dict["origin_text"]
        new_text = arg_dict["new_text"]

        if "[empty]" in origin_text:
            origin_text = '[empty]'

        if not new_text or not new_text.strip() or not origin_text or not origin_text.strip():
            raise Exception("编辑人设过程中发生错误: 缺少参数")

        show_text = None
        if notify_type == 2:
            show_text =  f"[evolution] 已修改人格预设: |\n  {origin_text} -> {new_text}"
        elif notify_type == 1:
            show_text =  f"[evolution] 人格预设更新完成~"
        elif notify_type == 0:
            show_text = None

        # 返回的文字信息将会被发送到会话中
        return {
            "text": show_text,
            "preset": {'origin': origin_text, 'new': new_text},
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
