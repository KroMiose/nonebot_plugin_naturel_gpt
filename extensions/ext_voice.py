from .Extension import Extension
import urllib, requests, uuid, os

# 拓展的配置信息，用于ai理解拓展的功能 *必填*
ext_config:dict = {
    "name": "voice",   # 拓展名称，用于标识拓展
    "arguments": {
        'sentence': 'str',  # 需要转换的文本
    },
    # 拓展的描述信息，用于提示ai理解拓展的功能 *必填* 尽量简短 使用英文更节省token
    "description": "Send a voice sentence. (use eg: /#voice&你好#/)",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 作者信息
    "author": "KroMiose",
    # 版本
    "version": "v0.0.1"
}

class CustomExtension(Extension):
    async def run(self, arg_dict: dict) -> dict:
        """ 当拓展被调用时执行的函数 *由拓展自行实现*
        
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息

        voice_path = 'voice_cache/'
        # 创建缓存文件夹
        if not os.path.exists(voice_path):
            os.mkdir(voice_path)

        # 获取参数
        text = arg_dict.get('sentence', None) + '喵' # 加上一个字符，避免合成语音丢失结尾
        text = urllib.parse.quote(text) # url编码

        url = f"http://127.0.0.1:23211/to_voice?text={text}"

        # 下载语音文件
        r = requests.get(url)
        file_name = f"{voice_path}{uuid.uuid1()}.ogg"
        with open(file_name, "wb") as f:
            f.write(r.content)

        local_url = f"file:///{os.path.abspath(file_name)}"

        if text is not None:
            return {
                'voice': local_url,    # 语音url
            }
        return {}

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
