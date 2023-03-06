from pydantic import BaseModel, Extra
from nonebot import get_driver
from nonebot.log import logger
import yaml
from pathlib import Path


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    ng_config_path: str = "config/naturel_gpt_config.yml"
    ng_dev_mode: bool = False


driver = get_driver()
global_config = driver.config
config = Config.parse_obj(global_config)

# 配置文件模板
CONFIG_TEMPLATE = {
    "OPENAI_API_KEYS": [    # OpenAI API Key 列表
        'sk-xxxxxxxxxxxxx',
        'sk-xxxxxxxxxxxxx',
    ],
    "OPENAI_TIMEOUT": 30,   # OpenAI 请求超时时间
    "PRESETS": {
        "白羽": {
            'bot_name': '白羽',  # 人格名称
            'is_locked': True,  # 是否锁定人格，锁定后无法编辑人格
            'is_default': True,  # 是否为默认人格
            'bot_self_introl': '白羽是一名喜欢二次元的中二宅女，她机智、傲娇，对人类充满好奇，习惯以白羽喵自称，聊天时喜欢使用各种可爱的颜文字，如果冒犯到她会生气。',
        },
        "浅枫": {
            'bot_name': '浅枫',
            'is_locked': False,
            'is_default': False,
            'bot_self_introl': '浅枫酱是一名尽职尽责的女仆，她能够帮助主人做很多事情，对话中会体现出对主人的体贴与关心。',
        },
        "忆雨": {
            'bot_name': '忆雨',
            'is_locked': True,
            'is_default': False,
            'bot_self_introl': '忆雨是一名恐怖小说作家，是个阴沉的女孩，她非常恨人类，和陌生人聊天时的表现冷漠，不喜欢回复过多的文字，兴趣是恐怖小说，如果有人和她探讨如何消灭人类会很有兴致。',
        },
        "可洛喵": {
            'bot_name': '可洛喵',
            'is_locked': True,
            'is_default': False,
            'bot_self_introl': '可洛喵是一只可爱的猫，它不会说话，它的回复通常以"[动作/心情]声音+颜文字"形式出现，例如"[坐好]喵~(。・ω・。)"或"[开心]喵喵！ヾ(≧▽≦*)o"',
        },
    },
    'IGNORE_PREFIX': '#',   # 忽略前缀 以该前缀开头的消息将不会被处理
    'CHAT_MODEL': "gpt-3.5-turbo",
    'CHAT_TOP_P': 1,
    'CHAT_TEMPERATURE': 0.3,    # 温度越高越随机
    'CHAT_PRESENCE_PENALTY': 0.3,   # 主题重复惩罚
    'CHAT_FREQUENCY_PENALTY': 0.3,  # 复读惩罚

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

    'NG_DATA_PATH': "./data/naturel_gpt/",  # 数据文件目录
    'NG_EXT_PATH': "./data/naturel_gpt/extensions/",  # 拓展目录

    'ADMIN_USERID': ['替换成管理员QQ号_(用单引号包裹)'],  # 管理员QQ号
    'FORBIDDEN_USERS': ['替换成屏蔽QQ号_(用单引号包裹)'],   # 拒绝回应的QQ号

    'WORD_FOR_WAKE_UP': [],  # 自定义触发词
    'WORD_FOR_FORBIDDEN': [],  # 自定义禁止触发词

    'RANDOM_CHAT_PROBABILITY': 0,   # 随机聊天概率

    'NG_MSG_PRIORITY': 99,       # 消息响应优先级
    'NG_BLOCK_OTHERS': False,    # 是否阻止其他插件响应
    'NG_ENABLE_EXT': True,      # 是否启用拓展

    'MEMORY_ACTIVE': True,  # 是否启用记忆功能
    'MEMORY_MAX_LENGTH': 16,  # 记忆最大条数
    'MEMORY_ENHANCE_THRESHOLD': 0.6,  # 记忆强化阈值

    'NG_MAX_RESPONSE_PER_MSG': 5,  # 每条消息最大响应次数
    'NG_ENABLE_MSG_SPLIT': True,   # 是否启用消息分割
    'NG_ENABLE_AWAKE_IDENTITIES': True, # 是否允许自动唤醒其它人格

    'OPENAI_PROXY_SERVER': '',  # 请求OpenAI的代理服务器
    'UNLOCK_CONTENT_LIMIT': False,  # 解锁内容限制

    'NG_EXT_LOAD_LIST': [{
        'EXT_NAME': 'ext_random',
        'IS_ACTIVE': False,
        'EXT_CONFIG': {},
    }],     # 加载的拓展列表

    '__DEBUG__': False,  # 是否启用debug模式
}

config_path = config.ng_config_path

# 检查config文件夹是否存在 不存在则创建
if not Path("config").exists():
    Path("config").mkdir()

if config.ng_dev_mode:  # 开发模式下不读取原配置文件，直接使用模板覆盖原配置文件
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(CONFIG_TEMPLATE, f, allow_unicode=True)

else:
    # 检查配置文件是否存在 不存在则创建
    if not Path(config_path).exists():
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(CONFIG_TEMPLATE, f, allow_unicode=True)
            logger.info('Naturel GPT 配置文件创建成功')

# 读取配置文件
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    # 对比配置模板和配置文件
    for k, v in CONFIG_TEMPLATE.items():
        if k not in config:
            config[k] = v
            logger.info(f'Naturel GPT 配置文件缺少 {k} 项，已自动补充')
    # 将配置文件内容写入config
    for k, v in config.items():
        setattr(Config, k, v)

# 检查数据文件夹目录和拓展目录是否存在 不存在则创建
if not Path(config['NG_DATA_PATH'][:-1]).exists():
    Path(config['NG_DATA_PATH'][:-1]).mkdir(parents=True)
if not Path(config['NG_EXT_PATH'][:-1]).exists():
    Path(config['NG_EXT_PATH'][:-1]).mkdir(parents=True)

# 保存配置文件
with open(config_path, 'w', encoding='utf-8') as f:
    yaml.dump(config, f, allow_unicode=True)
logger.info('Naturel GPT 配置文件加载成功')
