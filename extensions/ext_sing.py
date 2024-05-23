
import asyncio
from time import time
from loguru import logger
from .Extension import Extension
from pathlib import Path
# 读取JSON文件
from gradio_client import Client, file
import time


import asyncio
from functools import partial
ext_config: dict = {
    "name": "sing",  # 扩展名称，用于标识扩展
    "arguments": {
        "song": "str" 
    },
    # 扩展的描述信息，用于提示ai理解扩展的功能 *必填* 尽量简短 使用英文更节省token
    "description": "Sing a song (usage in response: /#sing&Song title#/)",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 作者信息
    "author": "Mff",
    # 版本
    "version": "0.0.1",
    # 扩展简介
    "intro": "唱歌",
    # 可用会话类型 (server即MC服务器 | chat即QQ聊天)
    "available": ["chat"],
}

class CustomExtension(Extension):
    async def async_predict(self, client, *args, **kwargs):
        fn = partial(client.predict, *args, **kwargs)
        loop = asyncio.get_running_loop()  # 获取当前的事件循环
        return await loop.run_in_executor(None, fn)

    async def main(self, client, *args, **kwargs):
        result = await self.async_predict(client, *args, **kwargs)
        return result

    async def process(self, client, kwargs):
        task = asyncio.create_task(self.main(client, **kwargs))
        result = await task
        return result

    async def call(self, arg_dict: dict, _: dict) -> dict:
        song_name = arg_dict.get("song", None)

        custom_config: dict = self.get_custom_config()  # 获取yaml中的配置信息
        singer = custom_config.get("singer")
        api = custom_config.get("api")
        url = None
        if singer.startswith("http"):
            url = file(singer)
            singer = None
        elif  not singer.startswith("BV"):
            singer="AI"+singer

        kwargs = {
            "start_time": 30,
            "song_name_src": song_name,
            "song_name_ref": singer,
            "ref_audio": url,
            "check_song": True,
            "auto_key": True,
            "key_shift": 0,
            "api_name": "/convert"
        }

        try:
            client = Client(api)
            kwargs.update({
                "client": client,
                "src_audio": None,
                "vocal_vol": 2,
                "inst_vol": 0,
            })
            result = await self.process(client, kwargs)
        except:
            try:
                client = Client("Delik/NeuCoSVC-2")
                kwargs.update({
                    "client": client,
                    "vocal_vol": 0,
                    "inst_vol": 0,
                })
                result = await self.process(client, kwargs)
            except Exception as exc:
                logger.info("扩展sing报错：" + str(exc))
                return {
                    "text": "唱不出来呜呜",
                }

        file_uri = Path(result).as_uri()
        return {
            "voice": file_uri,
        }
    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)