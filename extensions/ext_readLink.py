from .Extension import Extension
import requests

# 拓展的配置信息，用于ai理解拓展的功能 *必填*
ext_config:dict = {
    "name": "readLink",   # 拓展名称，用于标识拓展
    "arguments": {      
        "url": "str",   # 关键字
    },
    # 拓展的描述信息，用于提示ai理解拓展的功能 *必填* 尽量简短 使用英文更节省token
    # 如果bot无法理解拓展的功能，可适当添加使用示例 格式: /#拓展名&参数1&...&参数n#/
    "description": "Open the link and read the text and wait for the results. (usage in response: /#readLink&https://www.bilibili.com/#/))",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 5,
    # 作者信息
    "author": "CCYellowStar",
    # 版本
    "version": "0.0.1",
    # 拓展简介
    "intro": "让机器人openai能阅读链接内容",
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """ 当拓展被调用时执行的函数 *由拓展自行实现*
        
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息

        # 从arg_dict中获取参数
        U = arg_dict.get('url', None)

        if U is None:
            return {}
        else:
            quote = requests.utils.quote(U)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63'
        }

        url = f"https://ddg-webapp-aagd.vercel.app/url_to_text?url={quote}"

        res = requests.get(url, headers=headers)
        print(res.json())
        
        try:
            data=res.json()    
            text = data[0]['body'].replace("\n"," ")
            title = data[0]['title']
            from_ = "auto"
            to_ = "en"
            d = {"data": [text, from_, to_]}
            r = requests.post("https://hf.space/embed/mikeee/gradio-gtr/+/api/predict", json=d) #翻译成英文
            result = r.json()
            text = result["data"][0]           
        except:
            return {
                'text': f"[ext_readLink] 读取链接错误",
                'image': None,  # 图片url
                'voice': None,  # 语音url
            }
        # 返回的信息将会被发送到会话中
        if text != "Put something there, man.":
            return {
                'text': f'[ext_readLink] 读取: {U} ...',
                'notify': {
                    'sender': '[readLink]',
                    'msg': f"[ext_readLink] 读取 {U} 结果:(To save tokens, the content of the web page has been translated into English)\n{text}\n{title}"
                },
                'wake_up': True,  # 是否再次响应
            }
        else:
            return {
                'text': f'[ext_readLink] 读取: {U} ...',
                'notify': {
                    'sender': '[readLink]',
                    'msg': f"[ext_readLink] 读取 {U} 结果: null\n{title}"
                },
                'wake_up': True,  # 是否再次响应
            }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
