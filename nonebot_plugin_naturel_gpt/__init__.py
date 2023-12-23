from typing import Awaitable, Callable, Optional, Tuple
from nonebot import get_driver
from .logger import logger
from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event

from .config import *
from .preset_hub_funcs import check_presethub_connection
from . import utils

global_config = get_driver().config
# logger.info(config) # 这里可以打印出配置文件的内容

from .openai_func import TextGenerator
from .Extension import load_extensions
from .persistent_data_manager import PersistentDataManager
from .chat_manager import ChatManager
from . import matcher
from . import matcher_MCRcon # noqa: F401


def set_permission_check_func(callback:Callable[[Matcher, Event, Bot, str, str], Awaitable[Tuple[bool,Optional[str]]]]):
    """设置Matcher的权限检查函数"""
    matcher.permission_check_func = callback

# 设置默认权限检查函数，有需求时可以覆盖
set_permission_check_func(utils.default_permission_check_func)

""" ======== 读取历史记忆数据 ======== """
PersistentDataManager.instance.load_from_file()
ChatManager.instance.create_all_chat_object() # 启动时创建所有的已有Chat对象，以便被 -all 相关指令控制

# 读取ApiKeys
api_keys = config.OPENAI_API_KEYS
logger.info(f"共读取到 {len(api_keys)} 个API Key")

# 检查聊天摘要功能是否开启 未开启则清空所有聊天摘要
if not config.CHAT_ENABLE_SUMMARY_CHAT:
    logger.warning("聊天摘要功能已关闭，将自动清理历史聊天摘要数据")
    ChatManager.instance.clear_all_chat_summary()

""" ======== 初始化对话文本生成器 ======== """
TextGenerator.instance.init(api_keys=api_keys, config={
        'model': config.CHAT_MODEL,
        'max_tokens': config.REPLY_MAX_TOKENS,
        'temperature': config.CHAT_TEMPERATURE,
        'top_p': config.CHAT_TOP_P,
        'frequency_penalty': config.CHAT_FREQUENCY_PENALTY,
        'presence_penalty': config.CHAT_PRESENCE_PENALTY,
        'max_summary_tokens': config.CHAT_MAX_SUMMARY_TOKENS,
        'timeout': config.OPENAI_TIMEOUT,
}, 
proxy=config.OPENAI_PROXY_SERVER if config.OPENAI_PROXY_SERVER else None, # 代理服务器配置
base_url=config.OPENAI_BASE_URL if config.OPENAI_BASE_URL else '', # OpenAI API的base_url
)

""" ======== 加载扩展模块 ======== """
# Extension 模块有作为 __main__ 执行的需求，此时无法加载 class Config, 因此需要传递字典
load_extensions(config.dict())

""" ======== 预设中心连接检查 ======== """
if check_presethub_connection():
    logger.info(f"已连接到预设中心: {config.PRESETHUB_BED_URL}")
else:
    logger.warning("预设中心连接失败，请检查网络连接或预设中心地址是否正确")
