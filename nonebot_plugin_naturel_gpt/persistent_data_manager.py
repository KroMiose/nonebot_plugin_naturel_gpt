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
    is_locked:bool  = False
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
    enable_auto_switch_identity = False     # 是否允许自动切换人格
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
        
        """-------------------数据版本兼容开始-------------------"""
        # 兼容 bot_name 字段的pickle数据，下个版本将取消兼容
        for v in self._datas.values():
            for v2 in v.preset_datas.values():
                if (not hasattr(v2, 'preset_key')) and hasattr(v2, 'bot_name'):
                    setattr(v2, 'preset_key', getattr(v2, 'bot_name'))
                    delattr(v2, 'bot_name')
        
        # 兼容聊天记录人格分离版本的数据，将 active_preset 的聊天记录复制到ChatData内
        for v in self._datas.values():
            if not hasattr(v, 'chat_history'):
                chat_history = []
                setattr(v, 'chat_history', chat_history)
                setattr(v, 'chat_summarized', '')

                preset_data = v.preset_datas.get(v.active_preset, None)
                if preset_data:
                    preset_chat_history:List[str] = getattr(preset_data, 'chat_history')
                    preset_summary = getattr(preset_data, 'chat_summarized')
                    for item in preset_chat_history:
                        chat_history.append(item)
                    setattr(v, 'chat_summarized', preset_summary)
                
                for v2 in v.preset_datas.values():
                    delattr(v2, 'chat_history')
                    delattr(v2, 'chat_summarized')
        
        """-------------------数据版本兼容结束-------------------"""

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

    def get_all_chat_keys(self):
        """返回所有的chat_key"""
        return self._datas.keys()

    def get_preset_names(self, chat_key:str):
        """获取指定chat_key的人格名称列表"""
        return self._datas[chat_key].preset_datas.keys() if chat_key in self._datas else []


    def get_chat_data(self, chat_key:str) -> ChatData:
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
    
    def get_presets(self, chat_key:str) -> Dict[str, PresetData]:
        """获取指定chat_key的人格数据集合, 不存在时从配置模板的预设列表自动创建"""

        chat_data = self.get_chat_data(chat_key=chat_key)
        return chat_data.preset_datas
        
    def get_active_preset_name(self, chat_key:str) ->str:
        """获取指定chat_key当前preset_name"""
        if chat_key in self._datas:
            return self._datas[chat_key].active_preset
        else:
            return None
        
    def add_preset(self, chat_key:str, preset_key:str, bot_self_introl: str) -> bool:
        """给指定chat_key添加新人格"""
        presets = self.get_presets(chat_key)
        if preset_key in presets:
            return False

        presets[preset_key] = PresetData(preset_key=preset_key, bot_self_introl=bot_self_introl)
        return True
    
    def add_preset_for_all(self, chat_key:str, preset_key:str, bot_self_introl: str) -> Tuple[int, int]:
        """将预设添加到所有的会话中, 返回值为(成功数量，失败数量)"""
        success_cnt = 0
        fail_cnt = 0
        for chat_key in self.get_all_chat_keys():
            if(self.add_preset(chat_key=chat_key,preset_key=preset_key, bot_self_introl=bot_self_introl)):
                success_cnt += 1
            else:
                fail_cnt += 1
        return (success_cnt, fail_cnt)
    
    def add_preset_from_config(self, chat_key:str, preset_key:str, preset_config: PresetConfig) -> bool:
        """给指定chat_key添加新人格, config_preset为config中的全局配置"""
        presets = self.get_presets(chat_key)
        if preset_key in presets:
            return False

        presets[preset_key] = PresetData.create_from_config(preset_config)
        # 更新默认值
        if preset_config.is_default:
            for v in presets.values():
                v.is_default = v.preset_key == preset_key
        return True
    
    def update_preset(self, chat_key:str, preset_key:str, bot_self_introl: str) -> bool:
        """修改指定chat_key人格预设"""
        presets = self.get_presets(chat_key)
        if preset_key not in presets:
            return False
        
        presets[preset_key].bot_self_introl = bot_self_introl
        return True
    
    def update_preset_for_all(self, chat_key:str, preset_key:str, bot_self_introl: str) -> Tuple[int, int]:
        """修改所有会话的人格预设, 返回值为(成功数量，失败数量)"""
        success_cnt = 0
        fail_cnt = 0
        for chat_key in self.get_all_chat_keys():
            if(self.update_preset(chat_key=chat_key,preset_key=preset_key, bot_self_introl=bot_self_introl)):
                success_cnt += 1
            else:
                fail_cnt += 1
        return (success_cnt, fail_cnt)

    def del_preset(self, chat_key:str, preset_key:str) -> bool:
        """删除指定chat_key的指定性格(允许删除系统人格)"""
        presets = self.get_presets(chat_key)
        if preset_key not in presets:
            return False
        
        del presets[preset_key]
        return True
    
    def del_preset_for_all(self, chat_key:str, preset_key:str) -> Tuple[int, int]:
        """删除所有会话的指定预设， 返回值为(成功数量，失败数量)"""
        success_cnt = 0
        fail_cnt = 0
        for chat_key in self.get_all_chat_keys():
            if self._datas[chat_key].active_preset == chat_key: # 正在使用的 preset 不允许删除
                fail_cnt += 1
                continue
            if(self.del_preset(chat_key=chat_key,preset_key=preset_key)):
                success_cnt += 1
            else:
                fail_cnt += 1
        return (success_cnt, fail_cnt)
    
    def reset_preset(self, chat_key:str, preset_key:str) -> bool:
        """重置指定会话系统预设的人格设定, 如果是系统预设名将还原默认人格设定"""
        preset_config = config.PRESETS.get(preset_key, None)
        
        preset_datas = self.get_presets(chat_key)
        if preset_key not in preset_datas:
            return False
        preset_datas[preset_key].reset_to_default(preset_config)
        return True
    
    def reset_preset_for_all(self, chat_key:str, preset_key:str) -> Tuple[int, int]:
        """重置所有会话的指定预设，返回值为(成功数量，失败数量)"""
        success_cnt = 0
        fail_cnt = 0
        for chat_key in self.get_all_chat_keys():
            if(self.reset_preset(chat_key=chat_key,preset_key=preset_key)):
                success_cnt += 1
            else:
                fail_cnt += 1
        return (success_cnt, fail_cnt)
    
    def reset_chat(self, chat_key:str) -> bool:
        """重置当前会话所有预设，将丢失性格或历史数据"""
        chat_data = self.get_chat_data(chat_key=chat_key)
        chat_data.reset()
        return True
    
    def reset_chat_for_all(self, chat_key:str) -> Tuple[int, int]:
        """重置所有会话，返回值为(成功数量，失败数量)"""
        success_cnt = 0
        fail_cnt = 0
        for chat_key in self.get_all_chat_keys():
            if(self.reset_chat(chat_key=chat_key)):
                success_cnt += 1
            else:
                fail_cnt += 1
        return (success_cnt, fail_cnt)

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