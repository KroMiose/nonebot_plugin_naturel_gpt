from .Extension import Extension
import requests

# 拓展的配置信息，用于ai理解拓展的功能 *必填*
ext_config:dict = {
    "name": "Pic",   # 拓展名称，用于标识拓展
    "arguments": {      
        
    },
    # 拓展的描述信息，用于提示ai理解拓展的功能 *必填* 尽量简短 使用英文更节省token
    "description": "send 1 random pic. (not parameters!)",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": ["图", "pic", "Pic", "再"],
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict) -> dict:
        """ 当拓展被调用时执行的函数 *由拓展自行实现*
        
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息

        url = "https://api.ixiaowai.cn/api/api.php?return=json"
        img_src = requests.get(url, verify=False, timeout=10).json().get("imgurl", None)

        if img_src is None:
            return {
                'text': f"[来自拓展] 发送图片超时...",
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
