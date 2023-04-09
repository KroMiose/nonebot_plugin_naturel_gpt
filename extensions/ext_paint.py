import openai
import os
import uuid
from transformers import GPT2TokenizerFast

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

from .Extension import Extension
import requests

# 拓展的配置信息，用于ai理解拓展的功能 *必填*
ext_config:dict = {
    "name": "paint",   # 拓展名称，用于标识拓展
     "arguments": {
        'content': 'str',  # 绘画内容描述
    },
    "description": "paint a picture，使用/#paint&CONTENT#/，其中CONTENT是用逗号分隔的描述性词语。(例如：/#paint&兔子,草地,彩虹#/)",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": ['paint', '画', '图'],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 3,
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
        cache=custom_config.get("cache",False)
        proxy=custom_config.get("prxoy","http://127.0.0.1:7890")
        custom_size=custom_config.get("size","512")
        style=custom_config.get("style",'anime style, colored-pencil')
        cache_path=custom_config.get("cache_path","./data/ng_paint")
        
        # 从arg_dict中获取参数
        content = arg_dict.get('content', None)
        
        openai.proxies ={'http':proxy}
        response = openai.Image.create(
          prompt= content + ',' + style ,
          n=1,
          size=f"{custom_size}x{custom_size}"
        )
        image_url = response['data'][0]['url']
        res = response

        # 先定义一个本地下载并重名名的函数
        def download(url,dir_path,proxy):

            # 创建图片缓存路径
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            if cache:
                filename = str(uuid.uuid4()) + ".png"
            else:
                filename="temp.png"
            image_path = os.path.join(dir_path, filename)

            response = requests.get(url,proxies={"http":proxy,"https":proxy})
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                    image_path=f"files:///{os.path.abspath(image_path)}"
                print(f"图片已成功保存到 {image_path}")
            else:
                print("无法获取图片数据")
            return image_path


        if image_url is None:
            return {
                'text': "图片生成错误...",
                'image': None,  # 图片url
                'voice': None,  # 语音url
            }
        elif "rejected" in res:
            # 返回的信息将会被发送到会话中
            return {
                'text': "抱歉，这个图违反了ai生成规定，可能是太色了吧",       # 文本信息
                'image': None,   # 图片url
                'voice': None,      # 语音url
            }
        else:
            # 返回的信息将会被发送到会话中
            image_path=download(image_url,cache_path,proxy)
            return {
                'text': "画好了!",       # 文本信息
                'image': image_path,   # 图片url
                'voice': None,      # 语音url
            }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)


