from .Extension import Extension
import requests, time

# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config:dict = {
    "name": "search",   # 扩展名称，用于标识扩展
    "arguments": {      
        "keyword": "str",   # 关键字
    },
    # 扩展的描述信息，用于提示ai理解扩展的功能 *必填* 尽量简短 使用英文更节省token
    # 如果bot无法理解扩展的功能，可适当添加使用示例 格式: /#扩展名&参数1&...&参数n#/
    "description": "Search for keywords on Google and wait for the results. Use when you need to get real-time information or uncertain answers. (usage in response: /#search&keyword#/))",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 1,
    # 作者信息
    "author": "KroMiose, 投冥",
    # 版本
    "version": "0.0.1",
    # 扩展简介
    "intro": "使用Google进行在线搜索",
    # 调用时是否打断响应 启用后将会在调用后截断后续响应内容
    "interrupt": True,
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        custom_config:dict = self.get_custom_config()
        proxy = custom_config.get('proxy', None)
        max_results = custom_config.get('max_results', 3)
        apiKey= custom_config.get('apiKey', None)
        cxKey = custom_config.get('cxKey', None)

        if apiKey is None or cxKey is None:
            return {
                    "text": f"[Google] 未配置apiKey或cxKey",
                    "image": None,
                    "voice": None,
                }

        if proxy:
            if not proxy.startswith('http'):
                proxy = 'http://' + proxy        

        keyword = arg_dict.get('keyword', None)

        if keyword is None or keyword == self._last_keyword or time.time() - self._last_call_time < 10:
            return {}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63'
        }

        url=f"https://www.googleapis.com/customsearch/v1?key={apiKey}&cx={cxKey}&q={keyword}"

        res=requests.get(url,headers=headers, proxies={"http": proxy, "https": proxy})
        response=res.json()

        try:
            items=response["items"]
            text="\n".join([f"[{item['title']}] {item['snippet']} - from: {item['link']}" for item in items[:max_results]])
        except:
            return {
                    "text": f"[Google] 未找到关于'{keyword}'的信息",
                    "image": None,
                    "voice": None,
                }

        self._last_keyword = keyword
        self._last_call_time = time.time()
        return {
            'text': f'[Google] 搜索: {keyword} [完成]',
            'notify': {
                'sender': f'[Search results for {keyword} (The following infomation will not be sent directly to chat. Please summarize the search results as desired in your reply)]',
                'msg': f"{text}"
            },
            'wake_up': True, 
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
        self._last_keyword = None
        self._last_call_time = 0
