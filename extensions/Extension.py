# 拓展插件基类
class Extension:
    def __init__(self, ext_config, custom_config):
        self._ext_config = ext_config
        self._custom_config = custom_config

    async def run(self, arg_dict) -> dict:
        """ 插件运行 """
        raise NotImplementedError

    async def call(self, arg_dict) -> dict:
        """ 调用插件 """
        self._call_time -= 1
        if self._call_time < 0:
            return {}
        else:
            return await self.run(arg_dict)

    def generate_description(self, chat_history_text='') -> str:
        """ 生成插件描述 """
        print(chat_history_text)
        # 判断参考词
        if self._ext_config["refer_word"] and chat_history_text:
            for refer_word in self._ext_config["refer_word"]:
                if refer_word in chat_history_text:
                    break
            else:
                return ""
        args_desc:str = "; ".join([f"{k}: {v}" for k, v in self._ext_config.get('arguments', {}).items()])
        return f"- {self._ext_config['name']} > {args_desc} ({self._ext_config['description']})\n"

    def get_config(self) -> dict:
        """ 获取插件配置 """
        return self._ext_config

    def get_custom_config(self) -> dict:
        """ 获取插件自定义配置 """
        return self._custom_config

    def reset_call_times(self):
        """ 重置调用次数 """
        self._call_time = self._ext_config.get('max_call_times_per_msg', 99)

if __name__ == '__main__':
    import os, shutil
    # 复制 Extension.py 到 ../extensions/ 目录下
    shutil.copyfile(os.path.join(os.path.dirname(__file__), 'Extension.py'), os.path.join(os.path.dirname(__file__), '..', 'extensions', 'Extension.py'))