from typing import Any, Dict, List
from nonebot.config import Config as NBConfig
from pydantic import BaseModel, Extra
from nonebot import get_driver
from .logger import logger
import yaml
from pathlib import Path

class GlobalConfig(NBConfig, extra=Extra.ignore):
    """Plugin Config Here"""
    ng_config_path: str = "config/naturel_gpt_config.yml"
    ng_dev_mode: bool = False

class PresetConfig(BaseModel, extra=Extra.ignore):
    """人格预设配置项"""
    preset_key:str
    is_locked:bool = False
    is_default:bool = False
    is_only_private:bool = False
    """此预设是否仅限私聊"""
    bot_self_introl:str = ''

class ExtConfig(BaseModel, extra=Extra.ignore):
    """扩展配置项"""
    EXT_NAME:str
    IS_ACTIVE:bool
    EXT_CONFIG:Any

class Config(BaseModel, extra=Extra.ignore):
    """ng 配置数据，默认保存为 naturel_gpt_config.yml"""
    OPENAI_API_KEYS: List[str]
    """OpenAI API Key 列表"""
    OPENAI_TIMEOUT: int
    """OpenAI 请求超时时间"""
    OPENAI_PROXY_SERVER: str
    """请求OpenAI的代理服务器"""
    OPENAI_BASE_URL: str
    """请求OpenAI的基础URL"""
    REPLY_THROTTLE_TIME: int
    """回复间隔节流时间"""
    PRESETS: Dict[str, PresetConfig]
    """默认人格预设"""
    IGNORE_PREFIX: str
    """忽略前缀 以该前缀开头的消息将不会被处理"""
    CHAT_MODEL: str
    """OpenAI 模型"""
    CHAT_TOP_P: int
    CHAT_TEMPERATURE: float
    """温度越高越随机"""
    CHAT_PRESENCE_PENALTY: float
    """主题重复惩罚"""
    CHAT_FREQUENCY_PENALTY: float
    """复读惩罚"""

    CHAT_HISTORY_MAX_TOKENS: int
    """上下文聊天记录最大token数"""
    CHAT_MAX_SUMMARY_TOKENS: int
    """单次总结最大token数"""
    REPLY_MAX_TOKENS: int
    """单次回复最大token数"""
    REQ_MAX_TOKENS: int
    """单次请求最大token数"""

    REPLY_ON_NAME_MENTION: bool
    """是否在被提及时回复"""
    REPLY_ON_AT: bool
    """是否在被at时回复"""
    REPLY_ON_WELCOME: bool
    """是否在新成员加入时回复"""

    USER_MEMORY_SUMMARY_THRESHOLD: int
    """用户记忆阈值"""

    CHAT_ENABLE_RECORD_ORTHER: bool
    """是否记录其他人的对话"""
    CHAT_ENABLE_SUMMARY_CHAT: bool
    """是否启用总结对话"""
    CHAT_MEMORY_SHORT_LENGTH: int
    """短期对话记忆长度"""
    CHAT_MEMORY_MAX_LENGTH: int
    """长期对话记忆长度"""
    CHAT_SUMMARY_INTERVAL: int
    """长期对话记忆间隔"""

    NG_DATA_PICKLE: bool
    """是否强制使用pickle，默认使用json"""
    NG_DATA_PATH: str
    """数据文件目录"""
    NG_EXT_PATH: str
    """扩展目录"""
    NG_LOG_PATH: str
    """日志文件目录"""

    ADMIN_USERID: List[str]
    """管理员QQ号"""
    FORBIDDEN_USERS: List[str]
    """拒绝回应的QQ号"""

    FORBIDDEN_GROUPS: List[str]
    """拒绝回应的群号"""

    WORD_FOR_WAKE_UP: List[str]
    """自定义触发词"""
    WORD_FOR_FORBIDDEN: List[str]
    """自定义禁止触发词"""

    RANDOM_CHAT_PROBABILITY: float
    """随机聊天概率"""

    NG_MSG_PRIORITY: int
    """消息响应优先级"""
    NG_BLOCK_OTHERS: bool
    """是否阻止其他插件响应"""
    NG_ENABLE_EXT: bool
    """是否启用扩展"""
    NG_TO_ME: bool
    """响应命令是否需要@bot"""
    ENABLE_COMMAND_TO_IMG: bool
    """是否将rg相关指令转换为图片"""
    ENABLE_MSG_TO_IMG: bool
    """是否将机器人的回复转换成图片"""
    IMG_MAX_WIDTH: int
    """生成图片的最大宽度"""

    MEMORY_ACTIVE: bool
    """是否启用记忆功能"""
    MEMORY_MAX_LENGTH: int
    """记忆最大条数"""
    MEMORY_ENHANCE_THRESHOLD: float
    """记忆强化阈值"""

    NG_MAX_RESPONSE_PER_MSG: int
    """每条消息最大响应次数"""
    NG_ENABLE_MSG_SPLIT: bool
    """是否启用消息分割"""
    NG_ENABLE_AWAKE_IDENTITIES: bool
    """是否允许自动唤醒其它人格"""

    UNLOCK_CONTENT_LIMIT: bool
    """解锁内容限制"""

    NG_EXT_LOAD_LIST: List[ExtConfig]
    """加载的扩展列表"""

    GROUP_CARD:bool
    """优先读取群名片"""

    NG_CHECK_USER_NAME_HYPHEN:bool # 如果用户名中包含连字符，ChatGPT会将前半部分识别为名字，但一般情况下后半部分才是我们想被称呼的名字, eg. 策划-李华
    """检查用户名中的连字符"""

    ENABLE_MC_CONNECT: bool
    """是否启用MC服务器连接"""

    MC_COMMAND_PREFIX: List[str]
    """MC服务器人格指令前缀"""

    MC_RCON_HOST: str
    """MC服务器RCON地址"""

    MC_RCON_PORT: int
    """MC服务器RCON端口"""

    MC_RCON_PASSWORD: str
    """MC服务器RCON密码"""

    VERSION:str
    """配置文件版本信息"""
    
    DEBUG_LEVEL: int
    """debug level, [0, 1, 2, 3], 0 为关闭，等级越高debug信息越详细"""

# 配置文件模板(把全部默认值写到Config定义里比较乱，因此保留此默认值对象,作为真实的默认值)
CONFIG_TEMPLATE = {
    "OPENAI_API_KEYS": [    # OpenAI API Key 列表
        'sk-xxxxxxxxxxxxx',
        'sk-xxxxxxxxxxxxx',
    ],
    "OPENAI_TIMEOUT": 60,   # OpenAI 请求超时时间
    'OPENAI_PROXY_SERVER': '',  # 请求OpenAI的代理服务器
    'OPENAI_BASE_URL': 'https://api.openai.com/v1',      # 请求OpenAI的基础URL
    "REPLY_THROTTLE_TIME": 3,   # 回复间隔节流时间
    "PRESETS": {
        "白羽": {
            'preset_key': '白羽',  # 人格名称
            'is_locked': True,  # 是否锁定人格，锁定后无法编辑人格
            'is_default': True,  # 是否为默认人格
            "is_only_private": False,
            'bot_self_introl': '白羽是一名喜欢二次元的中二宅女，她机智、傲娇，对人类充满好奇，聊天时喜欢使用各种可爱的颜文字，如果冒犯到她会生气。',
        },
        "浅枫": {
            'preset_key': '浅枫',
            'is_locked': False,
            'is_default': False,
            "is_only_private": False,
            'bot_self_introl': '浅枫酱是一名尽职尽责的女仆，她能够帮助主人做很多事情，对话中会体现出对主人的体贴与关心。',
        },
        "忆雨": {
            'preset_key': '忆雨',
            'is_locked': True,
            'is_default': False,
            "is_only_private": False,
            'bot_self_introl': '忆雨是一名恐怖小说作家，是个阴沉的女孩，她非常恨人类，和陌生人聊天时的表现冷漠，不喜欢回复过多的文字，兴趣是恐怖小说，如果有人和她探讨如何消灭人类会很有兴致。',
        },
        "可洛喵": {
            'preset_key': '可洛喵',
            'is_locked': True,
            'is_default': False,
            "is_only_private": False,
            'bot_self_introl': '可洛喵是一只可爱的猫，它不会说话，它的回复通常以"[动作/心情]声音+颜文字"形式出现，例如"[坐好]喵~(。・ω・。)"或"[开心]喵喵！ヾ(≧▽≦*)o"',
        },
    },
    'IGNORE_PREFIX': '#',   # 忽略前缀 以该前缀开头的消息将不会被处理
    'CHAT_MODEL': "gpt-3.5-turbo",
    'CHAT_TOP_P': 1,
    'CHAT_TEMPERATURE': 0.4,    # 温度越高越随机
    'CHAT_PRESENCE_PENALTY': 0.4,   # 主题重复惩罚
    'CHAT_FREQUENCY_PENALTY': 0.4,  # 复读惩罚

    'CHAT_HISTORY_MAX_TOKENS': 2048,    # 上下文聊天记录最大token数
    'CHAT_MAX_SUMMARY_TOKENS': 512,   # 单次总结最大token数
    'REPLY_MAX_TOKENS': 1024,   # 单次回复最大token数
    'REQ_MAX_TOKENS': 3072,  # 单次请求最大token数

    'REPLY_ON_NAME_MENTION': True,  # 是否在被提及时回复
    'REPLY_ON_AT': True,            # 是否在被at时回复
    'REPLY_ON_WELCOME': True,       # 是否在新成员加入时回复

    'USER_MEMORY_SUMMARY_THRESHOLD': 12,  # 用户记忆阈值

    'CHAT_ENABLE_RECORD_ORTHER': True,  # 是否记录其他人的对话
    'CHAT_ENABLE_SUMMARY_CHAT': False,   # 是否启用总结对话
    'CHAT_MEMORY_SHORT_LENGTH': 8,  # 短期对话记忆长度
    'CHAT_MEMORY_MAX_LENGTH': 16,   # 长期对话记忆长度
    'CHAT_SUMMARY_INTERVAL': 10,  # 长期对话记忆间隔

    'NG_DATA_PICKLE': False,  # 强制使用pickle
    'NG_DATA_PATH': "./data/naturel_gpt/",  # 数据文件目录
    'NG_EXT_PATH': "./data/naturel_gpt/extensions/",  # 扩展目录
    'NG_LOG_PATH': "./data/naturel_gpt/logs/",  # 扩展目录

    'ADMIN_USERID': ['123456'],  # 管理员QQ号
    'FORBIDDEN_USERS': ['123456'],   # 拒绝回应的QQ号
    'FORBIDDEN_GROUPS': ['123456'],   # 拒绝回应的群号

    'WORD_FOR_WAKE_UP': [],  # 自定义触发词
    'WORD_FOR_FORBIDDEN': [],  # 自定义禁止触发词

    'RANDOM_CHAT_PROBABILITY': 0,   # 随机聊天概率

    'NG_MSG_PRIORITY': 99,       # 消息响应优先级
    'NG_BLOCK_OTHERS': False,    # 是否阻止其他插件响应
    'NG_ENABLE_EXT': True,      # 是否启用扩展
    'NG_TO_ME':False,           # 响应命令是否需要@bot
    'ENABLE_COMMAND_TO_IMG': True,    #是否将rg相关指令转换为图片
    'ENABLE_MSG_TO_IMG': False,     #是否将机器人的回复转换成图片
    'IMG_MAX_WIDTH': 800,

    'MEMORY_ACTIVE': True,  # 是否启用记忆功能
    'MEMORY_MAX_LENGTH': 16,  # 记忆最大条数
    'MEMORY_ENHANCE_THRESHOLD': 0.6,  # 记忆强化阈值

    'NG_MAX_RESPONSE_PER_MSG': 5,  # 每条消息最大响应次数
    'NG_ENABLE_MSG_SPLIT': True,   # 是否启用消息分割
    'NG_ENABLE_AWAKE_IDENTITIES': True, # 是否允许自动唤醒其它人格

    'UNLOCK_CONTENT_LIMIT': False,  # 解锁内容限制

    'NG_EXT_LOAD_LIST': [{
        'EXT_NAME': 'ext_random',
        'IS_ACTIVE': False,
        'EXT_CONFIG': {'arg': 'arg_value'},
    }],     # 加载的扩展列表
    
    'GROUP_CARD':True,
    'NG_CHECK_USER_NAME_HYPHEN': False, # 检查用户名中的连字符

    'ENABLE_MC_CONNECT': False,  # 是否启用MC服务器
    'MC_COMMAND_PREFIX': ['!', '！'],  # MC服务器指令前缀
    'MC_RCON_HOST': '127.0.0.1',  # MC服务器RCON地址
    'MC_RCON_PORT': 25575,  # MC服务器RCON端口
    'MC_RCON_PASSWORD': '',  # MC服务器RCON密码

    'VERSION':'1.0',
    'DEBUG_LEVEL': 0,  # debug level, [0, 1, 2], 0 为关闭，等级越高debug信息越详细
}

driver = get_driver()
global_config = GlobalConfig.parse_obj(driver.config)
config_path = global_config.ng_config_path
config:Config = None # type: ignore

def get_config() ->Config:
    """获取config数据（为了能够reload建议使用此函数获取对象）"""
    return config

def _load_config_obj_from_file()->Config:
    """从配置文件加载Config对象"""
    # 读取配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            config_obj_from_file:Dict = yaml.load(f, Loader=yaml.FullLoader)
            # 兼容 preset_key 和 bot_name
            for v in config_obj_from_file["PRESETS"].values():
                if 'bot_name' in v:
                    if "preset_key" not in v:
                        v["preset_key"] = v["bot_name"]
                    del v["bot_name"]
        except Exception as e:
            logger.error(f"Naturel GPT 配置文件读取失败，请检查配置文件填写是否符合yml文件格式规范，错误信息：{e}")
            raise e
        
        for k in CONFIG_TEMPLATE.keys():
            if not k in config_obj_from_file.keys():
                config_obj_from_file[k] = CONFIG_TEMPLATE[k]
                logger.info(f"Naturel GPT 配置文件缺少 {k} 项，将使用默认值")

        config_obj = Config.parse_obj(config_obj_from_file)
    return config_obj

def save_config():
    # 检查数据文件夹目录、扩展目录、日志目录是否存在 不存在则创建
    if not Path(config.NG_DATA_PATH[:-1]).exists():
        Path(config.NG_DATA_PATH[:-1]).mkdir(parents=True)
    if not Path(config.NG_EXT_PATH[:-1]).exists():
        Path(config.NG_EXT_PATH[:-1]).mkdir(parents=True)
    if not Path(config.NG_LOG_PATH[:-1]).exists():
        Path(config.NG_LOG_PATH[:-1]).mkdir(parents=True)

    # 保存配置文件
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config.dict(), f, allow_unicode=True, sort_keys=False)

def load_config_from_file_then_save():
    """加载配置文件，然后保存回文件"""
    global config
    config = _load_config_obj_from_file()

    save_config()
    logger.info('Naturel GPT 配置文件加载成功')

def reload_config():
    """重载配置文件"""
    global config
    assert(config)

    config_tmp = _load_config_obj_from_file()
    for k in config.dict():
        setattr(config, k, getattr(config_tmp,k))
    logger.info(f'Naturel GPT 配置文件重载成功! ver:{config.VERSION}')

# 检查config文件夹是否存在 不存在则创建
if not Path("config").exists():
    Path("config").mkdir()

if global_config.ng_dev_mode:  # 开发模式下不读取原配置文件，直接使用模板覆盖原配置文件
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(CONFIG_TEMPLATE, f, allow_unicode=True)
else:
    # 检查配置文件是否存在 不存在则创建
    if not Path(config_path).exists():
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(CONFIG_TEMPLATE, f, allow_unicode=True)
            logger.info('Naturel GPT 配置文件创建成功')

# 加载配置文件
load_config_from_file_then_save()
