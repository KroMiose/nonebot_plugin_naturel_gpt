import importlib
import time
import os
import sys
import shutil
import nonebot
from typing import TYPE_CHECKING, Any, Dict, Type, Union

if TYPE_CHECKING:
    from loguru import Record


def __path(record: "Record"):
    record["name"] = "NG聊天扩展"


logger = nonebot.logger.bind()
logger = logger.patch(__path)


# 扩展插件基类
class Extension:

    def __init__(self, ext_config, custom_config):
        self._ext_config = ext_config
        self._custom_config = custom_config

    async def run(self, arg_dict: dict, ctx_data: dict) -> dict:
        """ 扩展运行 """
        raise NotImplementedError

    async def call(self, arg_dict, ctx_data) -> Union[str, dict]:
        """ 调用扩展 """
        self._call_time -= 1
        if self._call_time < 0:
            return {}
        else:
            return await self.run(arg_dict, ctx_data)

    def generate_description(self, chat_history_text='') -> str:
        """ 生成扩展描述prompt(供bot参考用) """
        # print(chat_history_text)
        # 判断参考词
        if self._ext_config["refer_word"] and chat_history_text:
            for refer_word in self._ext_config["refer_word"]:
                if refer_word in chat_history_text:
                    break
            else:
                return ""
        args_desc: str = "; ".join([
            f"{k}:{v}"
            for k, v in self._ext_config.get('arguments', {}).items()
        ])
        args_desc = 'no args' if args_desc == '' else args_desc
        return f"- {self._ext_config['name']}: {args_desc} ({self._ext_config['description']})\n"

    def generate_short_description(self) -> str:
        """ 生成扩展简短描述(供生成扩展简报用) """
        return f"- [{self._ext_config.get('name', '未知扩展')} v{self._ext_config.get('version', '0')}]: {self._ext_config.get('intro', '暂无描述')} by: {self._ext_config.get('author', '未知')}\n"

    def get_config(self) -> dict:
        """ 获取扩展配置 """
        return self._ext_config

    def get_custom_config(self) -> dict:
        """ 获取扩展自定义配置 """
        return self._custom_config

    def reset_call_times(self):
        """ 重置调用次数 """
        self._call_time = self._ext_config.get('max_call_times_per_msg', 99)


def load_extensions(config: Dict[str, Any]) -> None:
    """加载扩展模块"""
    global global_extensions
    global_extensions.clear()
    if not config.get('NG_ENABLE_EXT'):
        return

    ext_path = config['NG_EXT_PATH']
    abs_ext_path = os.path.abspath(ext_path)

    # 在当前文件夹下建立一个ext_cache文件夹 用于暂存扩展模块的.py文件以便于动态导入
    if not os.path.exists('ext_cache'):
        os.makedirs('ext_cache', exist_ok=True)
    # 删除ext_cache文件夹下的所有文件和文件夹
    for file in os.listdir('ext_cache'):
        file_path = os.path.join('ext_cache', file)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
    # 在ext_cache文件夹下建立一个__init__.py文件 用于标记该文件夹为一个python包
    if not os.path.exists('ext_cache/__init__.py'):
        with open('ext_cache/__init__.py', 'w', encoding='utf-8') as f:
            f.write('')

    # 根据 Extension 文件 生成 Extension.py 并覆盖到扩展模块路径和 ext_cache 文件夹下
    with open(os.path.join(os.path.dirname(__file__), 'Extension.py'),
              'r',
              encoding='utf-8') as f:
        ext_file = f.read()
    with open(f'{ext_path}Extension.py', 'w', encoding='utf-8') as f:
        f.write(ext_file)
    with open(f'ext_cache/Extension.py', 'w', encoding='utf-8') as f:
        f.write(ext_file)

    sys.path.append(os.getcwd())  # 不加这一行在 docker 下会找不到 ext_cache

    for tmpExt in config['NG_EXT_LOAD_LIST']:  # 遍历扩展模块列表
        if tmpExt.get('IS_ACTIVE') and tmpExt.get('EXT_NAME'):
            logger.info(f"正在从加载扩展模块 \"{tmpExt.get('EXT_NAME')}\" ...")
            try:
                file_name = tmpExt.get("EXT_NAME") + '.py'  # 扩展模块文件名

                # 复制扩展模块文件到ext_cache文件夹下
                shutil.copyfile(f'{ext_path}{file_name}',
                                f'ext_cache/{file_name}')
                time.sleep(0.3)  # 等待文件复制完成
                # 从 ext_cache 文件夹下导入扩展模块
                CustomExtension: type = getattr( # Type[CustomExtension]
                    importlib.import_module(
                        f'ext_cache.{tmpExt.get("EXT_NAME")}'),
                    'CustomExtension')
                time.sleep(0.3)  # 等待文件导入完成

                ext_config_dict = tmpExt.get("EXT_CONFIG") if isinstance(
                    tmpExt.get("EXT_CONFIG"), dict) else {}

                # 加载扩展模块并实例化
                ext = CustomExtension(ext_config_dict)
                # 将扩展模块添加到全局扩展模块字典中
                global_extensions[ext.get_config().get('name').lower()] = ext
                logger.info(f"加载扩展模块 {tmpExt.get('EXT_NAME')} 成功！")
            except Exception as e:
                logger.error(
                    f"加载扩展模块 \"{tmpExt.get('EXT_NAME')}\" 失败 | 原因: {e}")


global_extensions: Dict[str, Extension] = {}  # 用于存储所有扩展的字典

if __name__ == '__main__':
    import os, shutil
    # 复制 Extension.py 到 ../extensions/ 目录下
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__), 'Extension.py'),
        os.path.join(os.path.dirname(__file__), '..', 'extensions',
                     'Extension.py'))
    # 复制 Extension.py 到 ../share_exts/ 目录下
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__), 'Extension.py'),
        os.path.join(os.path.dirname(__file__), '..', 'share_exts',
                     'Extension.py'))
