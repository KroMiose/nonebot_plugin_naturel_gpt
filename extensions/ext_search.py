from .Extension import Extension
import requests

# 拓展的配置信息，用于ai理解拓展的功能 *必填*
ext_config:dict = {
    "name": "search",   # 拓展名称，用于标识拓展
    "arguments": {      
        "keyword": "str",   # 关键字
    },
    # 拓展的描述信息，用于提示ai理解拓展的功能 *必填* 尽量简短 使用英文更节省token
    # 如果bot无法理解拓展的功能，可适当添加使用示例 格式: /#拓展名&参数1&...&参数n#/
    "description": "Search for keywords on the Internet and wait for the results. Use when you need to get real-time information or uncertain answers. After calling this extension, you need to stop responding and wait for the search results before continuing to respond. (usage in response: /#search&keyword#/))",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 5,
    # 作者信息
    "author": "CCYellowStar",
    # 版本
    "version": "0.0.2",
    # 拓展简介
    "intro": "让机器人openai能上网搜索",
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """ 当拓展被调用时执行的函数 *由拓展自行实现*
        
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息
        proxy = custom_config.get('proxy', '')
        max_results = custom_config.get('max_results', 3)
        if proxy:
            if not proxy.startswith('http'):
                proxy = 'http://' + proxy        
        # 从arg_dict中获取参数
        keyword = arg_dict.get('keyword', None)

        if keyword is None:
            return {}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63'
        }

        url = f"https://ddg-webapp-aagd.vercel.app/search?q={keyword}&max_results={max_results}&region=cn-zh"

        res = requests.get(url, headers=headers,proxies={'http':proxy})
        print(res.json())
        
        try:
            data=res.json()    
            text = '\n'.join([f"{data[i]['body']}" for i in range(len(data)) if i < max_results])
            # text = data[0]['body']+"\n"+data[0]['href']+"\n"+data[1]['body']+"\n"+data[1]['href']+"\n"+data[2]['body']+"\n"+data[2]['href']
            #refer_url = data[0]['href']+"\n"+data[1]['href']+"\n"+data[2]['href']
        except:
            return {
                'text': f"[ext_search] 未找到关于'{keyword}'的信息",
                'image': None,  # 图片url
                'voice': None,  # 语音url
            }
        # 返回的信息将会被发送到会话中
        return {
            'text': f'[ext_search] 搜索: {keyword} [完成]',
            'notify': {
                'sender': '[search]',
                'msg': f"[ext_search] Search results for xxx {keyword} (Please refer to the following information to respond):\n{text}\n"
            },
            'wake_up': True,  # 是否再次响应
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
