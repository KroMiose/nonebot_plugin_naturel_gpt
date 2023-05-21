from typing import Dict, Optional, Tuple
from .singleton import Singleton
from .chat import Chat
from .persistent_data_manager import PersistentDataManager
from .config import *

class ChatManager(Singleton["ChatManager"]):
    """全局会话管理器"""

    # 对Chat的查找和批量操作必须通过调用此类函数实现，不允许直接读写 PersistentDataManager
    # 对单个Chat的操作相关函数定义在Chat类定义内

    _chat_dict:Dict[str, Chat] = {}
    """进程中存在的所有聊天Session"""

    def create_all_chat_object(self) -> None:
        """创建所有的已有Chat对象"""
        all_chat_datas = PersistentDataManager.instance.get_all_chat_datas()
        for chat_data in all_chat_datas:
            chat_key = chat_data.chat_key
            if chat_key not in self._chat_dict:
                self._chat_dict[chat_key] = Chat(chat_data)

    def has_chat_key(self, chat_key:str) -> bool:
        """是否存在指定chat_key"""
        return chat_key in self._chat_dict
    
        """通过chat_key获取一个Chat对象"""
    def get_chat(self, chat_key: str) -> Optional[Chat]:
        return self._chat_dict.get(chat_key, None)
    
    def get_all_chats(self) -> List[Chat]:
        """获取所有的会话"""
        return list(self._chat_dict.values())
    
    def get_all_chat_keys(self) -> List[str]:
        """获取所有的会话名称"""
        return list(self._chat_dict.keys())
    
    def get_or_create_chat(self, chat_key: str) -> Chat:
        """通过chat_key获取一个Chat对象，不存在时自动创建一个"""
        # 判断是否已经存在对话
        if chat_key in self._chat_dict:
            if config.DEBUG_LEVEL > 1: logger.info(f"已存在对话 {chat_key} - 继续对话")
        else:
            if config.DEBUG_LEVEL > 0: logger.info("不存在对话 - 创建新对话")
            # 创建新对话
            chat_data = PersistentDataManager.instance.get_or_create_chat_data(chat_key=chat_key)
            self._chat_dict[chat_key] = Chat(chat_data)
        
        chat = self._chat_dict[chat_key]
        return chat
    
    def toggle_chat_for_all(self, enabled:bool=True) -> None:
        """开关所有会话"""
        for chat in self._chat_dict.values():
            chat.toggle_chat(enabled=enabled)

    def toggle_auto_switch_for_all(self, enabled:bool=True) -> None:
        """开关所有会话自动切换人格"""
        for chat in self._chat_dict.values():
            chat.toggle_auto_switch(enabled=enabled)

    def del_preset_for_all(self, preset_key:str) -> Tuple[int, int]:
        """删除所有会话的指定预设， 返回值为(成功数量，失败数量)"""
        success_cnt = fail_cnt = 0
        for chat in self._chat_dict.values():
            if(chat.del_preset(preset_key=preset_key)[0]):
                success_cnt += 1
            else:
                fail_cnt += 1
        return (success_cnt, fail_cnt)
    
    def rename_preset_for_all(self, old_preset_key:str, new_preset_key: str) -> Tuple[int, int]:
        """改名所有会话指定预设, 对话历史将全部丢失！"""
        success_cnt = fail_cnt = 0
        for chat in self._chat_dict.values():
            if(chat.rename_preset(old_preset_key=old_preset_key, new_preset_key=new_preset_key)[0]):
                success_cnt += 1
            else:
                fail_cnt += 1
        return (success_cnt, fail_cnt)
    
    def add_preset_for_all(self, preset_key:str, bot_self_introl: str) -> Tuple[int, int]:
        """将预设添加到所有的会话中, 返回值为(成功数量，失败数量)"""
        success_cnt = fail_cnt = 0
        for chat in self._chat_dict.values():
            success, _ = chat.add_preset(preset_key=preset_key, bot_self_introl=bot_self_introl)
            if(success):
                success_cnt += 1
            else:
                fail_cnt += 1
        return (success_cnt, fail_cnt)

    def change_presettings_for_all(self, preset_key:str) -> Tuple[int, int]:
        """设置所有会话的预设, 返回值为(成功数量，失败数量)"""
        success_cnt = fail_cnt = 0
        for chat in self._chat_dict.values():
            if chat.change_presettings(preset_key=preset_key)[0]:
                success_cnt += 1
            else:
                fail_cnt += 1
        return (success_cnt, fail_cnt)
    
    def update_preset_for_all(self, preset_key:str, bot_self_introl: str) -> Tuple[int, int]:
        """修改所有会话的人格预设, 返回值为(成功数量，失败数量)"""
        success_cnt = fail_cnt = 0
        for chat in self._chat_dict.values():
            if(chat.update_preset(preset_key=preset_key, bot_self_introl=bot_self_introl)[0]):
                success_cnt += 1
            else:
                fail_cnt += 1
        return (success_cnt, fail_cnt)
    
    def reset_preset_for_all(self, preset_key:str) -> Tuple[int, int]:
        """重置所有会话的指定预设，返回值为(成功数量，失败数量)"""
        success_cnt = fail_cnt = 0
        for chat in self._chat_dict.values():
            if(chat.reset_preset(preset_key=preset_key)[0]):
                success_cnt += 1
            else:
                fail_cnt += 1
        return (success_cnt, fail_cnt)
    
    def reset_chat_for_all(self) -> Tuple[int, int]:
        """重置所有会话，返回值为(成功数量，失败数量)"""
        success_cnt = fail_cnt = 0
        for chat in self._chat_dict.values():
            if(chat.reset_chat()[0]):
                success_cnt += 1
            else:
                fail_cnt += 1
        return (success_cnt, fail_cnt)
    
    def clear_all_chat_summary(self):
        """清除所有的聊天摘要"""
        for chat in self._chat_dict.values():
            chat.chat_data.chat_summarized = ''
