import os
import pickle
import time
from typing import Set, Dict, List, Tuple, overload
from dataclasses import dataclass, field

from nonebot import logger
from .singleton import Singleton
from .config import config, PresetConfig

@dataclass
class ImpressionData:
    """某个会话中对某个用户的印象"""
    user_id:str
    chat_history:List[str] = field(default_factory=lambda:[])
    """特定预设与特定用户的聊天记录，用于生成chat_impression"""
    chat_impression:str = ''
    """特定预设对特定用户的印象"""

@dataclass
class PresetData:
    """特定chat_key的特定preset人格预设及其产生的聊天数据"""
    preset_key:str
    bot_self_introl:str
    is_locked:bool  = False # 是否锁定人格，锁定后无法编辑人格
    is_default:bool = False
    is_only_private:bool = False
    """此预设是否仅限私聊"""

    # 以下为对话产生的数据
    chat_impressions:Dict[str, ImpressionData]  = field(default_factory=lambda:{}) # 对(群聊中)特定用户的印象
    chat_memory:Dict[str, str]  = field(default_factory=lambda:{})
    """当前预设的记忆"""

    @classmethod
    def create_from_config(cls, preset_config:PresetConfig):
        """从PresetConfig创建一个PresetData实例"""
        preset_data = PresetData(**preset_config.dict())
        return preset_data

    def reset_to_default(self, preset_config:PresetConfig):
        """清空数据，并将人格设定为config_data中的值(如果存在的话)"""
        if preset_config is not None:
            if preset_config.preset_key != self.preset_key:
                raise Exception(f"wrong preset key, expect `{self.preset_key}` but get `{preset_config.preset_key}`")
            
            self.is_locked          = preset_config.is_locked
            self.is_default         = preset_config.is_default
            self.is_only_private    = preset_config.is_only_private
        else:
            self.is_locked          = False
            self.is_default         = False
            self.is_only_private    = False
        
        self.chat_impressions.clear()
        self.chat_memory.clear()

@dataclass
class ChatData:
    """用户聊天数据(群，私聊)"""
    chat_key:str  # group_123456, private_123456
    is_enable:bool              = True      # 是否启用会话
    enable_auto_switch_identity:bool = config.NG_ENABLE_AWAKE_IDENTITIES     # 是否允许自动切换人格
    active_preset:str           = ''        # 当前 preset_name
    preset_datas:Dict[str, PresetData] = field(default_factory=lambda:{}) # [preset_name, data]

    # 以下为对话产生的数据
    chat_history:List[str]      = field(default_factory=lambda:[]) # 当前会话全局历史
    """当前会话的全局对话历史"""
    chat_summarized:str         = ''
    """总结"""
    
    def reset(self):
        """重置当前会话历史数据"""
        self.chat_history.clear()
        self.chat_summarized = ''

        for k, v in self.preset_datas.items():
            v.reset_to_default(preset_config = config.PRESETS.get(k, None))


class PersistentDataManager(Singleton["PersistentDataManager"]):
    """用户聊天(群，私聊)持久化数据管理器"""

    # chat相关数据和行为请通过调用Chat/ChatManager类相关函数实现，禁止直接操纵本类数据, 否则会丢失数据同步

    _datas:Dict[str, ChatData] = {}
    _last_save_data_time:float
    _file_path:str
    _inited:bool

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
        self._inited = True

    @property
    def is_inited(self) -> bool:
        return self._inited

    def save_to_file(self):
        """使用pickle将用户数据保存到文件"""
        if time.time() - self._last_save_data_time < 60:  # 如果距离上次保存时间不足60秒则不保存
            return
        # 保存到pickle文件
        with open(self._file_path, 'wb') as f:
            pickle.dump(self._datas, f)
        self._last_save_data_time = time.time()
        logger.info("数据保存成功")

    def get_all_chat_keys(self) -> List[str]:
        """获取所有的chat_key"""
        return list(self._datas.keys())
    
    def get_all_chat_datas(self) -> List[ChatData]:
        """获取所有的ChatData"""
        return list(self._datas.values())

    def get_preset_names(self, chat_key:str):
        """获取指定chat_key的人格名称列表"""
        return self._datas[chat_key].preset_datas.keys() if chat_key in self._datas else []

    def get_or_create_chat_data(self, chat_key:str) -> ChatData:
        """获取指定chat_key的聊天数据, 不存在时从配置模板的预设列表自动创建"""

        if chat_key in self._datas:
            return self._datas[chat_key]
        else:
            chat_data = ChatData(chat_key=chat_key)
            for v in config.PRESETS.values():
                preset_data = PresetData.create_from_config(v)
                chat_data.preset_datas[preset_data.preset_key] = preset_data
            
            self._datas[chat_key] = chat_data
            return chat_data

