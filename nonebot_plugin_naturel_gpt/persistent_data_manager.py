import os
import pickle
import time
from typing import Set, Dict, List, overload
from dataclasses import dataclass, field

from nonebot import logger
from .singleton import Singleton
from .config import config, PresetConfig

@dataclass
class ImpressionData:
    """某个会话中对某个用户的印象"""
    user_id:str
    chat_history:List[str] = field(default_factory=lambda:[])
    chat_impression:str = ''

@dataclass
class PresetData:
    """特定chat_key的特定preset人格预设及其产生的聊天数据"""
    bot_name:str
    bot_self_introl:str
    is_locked:bool  = False
    is_default:bool = False
    is_enable:bool  = True

    # 以下为对话产生的数据
    chat_history:List[str]  = field(default_factory=lambda:[])
    chat_summarized:str     = ''
    chat_impressions:Dict[str, ImpressionData]  = field(default_factory=lambda:{}) # 对(群聊中)特定用户的印象
    chat_memory:Dict[str, str]                  = field(default_factory=lambda:{})

    def reset_to_default(self, config_data:PresetConfig):
        """清空数据，并将人格设定为config_data中的值(如果存在的话)"""
        if config_data is not None:
            if config_data["bot_name"] != self.bot_name:
                raise Exception(f"wrong bot_name, expect `{self.bot_name}` but get `{config_data['bot_name']}`")
            
            # self.bot_self_introl    = config_data.get("bot_self_introl", "")
            self.is_locked          = config_data.get("is_locked", False)
            self.is_default         = config_data.get("is_default", False)
            self.is_enable          = config_data.get("is_enable", True)
        else:
            # self.bot_self_introl    = ''
            self.is_locked          = False
            self.is_default         = False
            self.is_enable          = True
        
        self.chat_history.clear()
        self.chat_summarized=''
        self.chat_impressions.clear()
        self.chat_memory.clear()

@dataclass
class ChatData:
    """用户聊天数据(群，私聊)"""
    chat_key:str  # group_123456, private_123456
    active_preset:str = '' # 当前 preset_name
    preset_datas:Dict[str, PresetData] = field(default_factory=lambda:{}) # [preset_name/bot_name, data]

class PersistentDataManager(Singleton["PersistentDataManager"]):
    """用户聊天(群，私聊)持久化数据管理器"""
    _datas:Dict[str, ChatData] = {}
    _last_save_data_time:float
    _file_path:str

    def load_from_file(self, file_path:str):
        """使用pickle从文件中载入数据"""
        self._file_path = file_path

        # 检测历史数据pickle文件是否存在 不存在则初始化 存在则读取
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                self._datas = pickle.load(f)  # 读取历史数据pickle文件
                logger.info("读取历史数据成功")
        else:   # 如果不存在历史数据json文件，则初始化
            # 检测目录是否存在 不存在则创建
            if not os.path.exists(config.NG_DATA_PATH):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

            logger.info("找不到历史数据，初始化成功")
        self._last_save_data_time = time.time()

    def save_to_file(self):
        """使用pickle将用户数据保存到文件"""
        if time.time() - self._last_save_data_time < 60:  # 如果距离上次保存时间不足60秒则不保存
            return
        # 保存到pickle文件
        with open(self._file_path, 'wb') as f:
            pickle.dump(self._datas, f)
        self._last_save_data_time = time.time()
        logger.info("数据保存成功")

    def get_preset_names(self, chat_key:str) -> Set[str]:
        """获取指定chat_key的人格名称列表"""
        return self._datas[chat_key].preset_datas.keys() if chat_key in self._datas else {}


    def get_chat_data(self, chat_key:str) -> ChatData:
        """获取指定chat_key的聊天数据, 不存在时从配置模板的预设列表自动创建"""

        if chat_key in self._datas:
            return self._datas[chat_key]
        else:
            chat_data = ChatData(chat_key=chat_key)
            for v in config.PRESETS.values():
                preset_data = PresetData(**dict(v))
                chat_data.preset_datas[preset_data.bot_name] = preset_data
            
            self._datas[chat_key] = chat_data
            return chat_data
    
    def get_presets(self, chat_key:str) -> Dict[str, PresetData]:
        """获取指定chat_key的人格数据集合, 不存在时从配置模板的预设列表自动创建"""

        chat_data = self.get_chat_data(chat_key=chat_key)
        return chat_data.preset_datas if chat_data else None
        
    def get_active_preset_name(self, chat_key:str) ->str:
        """获取指定chat_key当前preset_name"""
        if chat_key in self._datas:
            return self._datas[chat_key].active_preset
        else:
            return None
        
    def add_preset(self, chat_key:str, bot_name:str, bot_self_introl: str) -> bool:
        """给指定chat_key添加新人格"""
        presets = self.get_presets(chat_key)
        if bot_name in presets:
            return False

        presets[bot_name] = PresetData(bot_name=bot_name, bot_self_introl=bot_self_introl)
        return True
    
    def add_preset_from_config(self, chat_key:str, bot_name:str, config_preset: PresetConfig) -> bool:
        """给指定chat_key添加新人格, config_preset为config中的全局配置"""
        presets = self.get_presets(chat_key)
        if bot_name in presets:
            return False

        presets[bot_name] = PresetData(**config_preset)
        # 更新默认值
        if config_preset["is_default"]:
            for v in presets.values():
                v.is_default = v.bot_name == bot_name
        return True
    
    def update_preset(self, chat_key:str, bot_name:str, bot_self_introl: str) -> bool:
        """修改指定chat_key人格预设"""
        presets = self.get_presets(chat_key)
        if bot_name not in presets:
            return False
        
        presets[bot_name].bot_self_introl = bot_self_introl

    def del_preset(self, chat_key:str, bot_name:str) -> bool:
        """删除指定chat_key的指定性格(允许删除系统人格)"""
        presets = self.get_presets(chat_key)
        if bot_name not in presets:
            return False
        
        del presets[bot_name]
        return True
    
    def reset_preset(self, chat_key:str, bot_name:str):
        """重置指定chat_key系统预设的人格设定, 如果是系统预设名将还原默认人格设定"""
        config_data = config.PRESETS[bot_name] if bot_name in config.PRESETS else None
        
        presets = self.get_presets(chat_key)
        if bot_name not in presets:
            presets[bot_name] = PresetData(bot_name=bot_name,
                                           bot_self_introl=config_data.bot_self_introl if config_data else '')
        else:
            presets[bot_name].reset_to_default(config_data)

    def reset_all_system_preset(self, chat_key:str):
        """重置指定chat_key的所有系统预设的人格设定"""
        for k in config.PRESETS.keys():
            self.reset_preset(chat_key=chat_key, bot_name=k)

    def update_all_system_identity_presets():
        """配置文件更新时将新的人格数据同步到已有chat_key中"""
        pass

    def clear_all_chat_summary(self):
        """清除所有的聊天摘要"""
        for user_data in self._datas.values():
            for preset_data in user_data.preset_datas.values():
                preset_data.chat_summarized = ''

    def load_from_old_format():
        """从旧格式载入数据"""
        pass