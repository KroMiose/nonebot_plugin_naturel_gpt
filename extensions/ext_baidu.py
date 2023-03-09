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
    "description": "Search for keywords on the Internet and wait for the results. (usage in response: /#search&keyword#/))",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 5,
    # 作者信息
    "author": "KroMiose",
    # 版本
    "version": "0.0.1"
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """ 当拓展被调用时执行的函数 *由拓展自行实现*
        
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息

        # 从arg_dict中获取参数
        keyword = arg_dict.get('keyword', None)

        if keyword is None:
            return {}
        else:
            quote = requests.utils.quote(keyword)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63'
        }

        url = f"http://baike.baidu.com/api/openapi/BaikeLemmaCardApi?scope=103&format=json&appid=379020&bk_key={quote}_length=600"

        res = requests.get(url, headers=headers)
        print(res.json())   # todo 此处拿不到数据，原因暂时不明
        
        try:
            abstract = res.json()['abstract']
            refer_url = res.json()['url']
        except:
            return {
                'text': f"[ext_baidu] 未找到关于{keyword}的百科信息",
                'image': None,  # 图片url
                'voice': None,  # 语音url
            }
        # 返回的信息将会被发送到会话中
        return {
            'text': f'[ext_baidu] 调用百度百科搜索: {keyword} ...',
            'notify': {
                'sender': '[baidu]',
                'msg': f"[ext_baidu] 百度百科搜索 {keyword} 结果:\n{abstract}\n{refer_url}"
            },
            'wake_up': True,  # 是否再次响应
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
