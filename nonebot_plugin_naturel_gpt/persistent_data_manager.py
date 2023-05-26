import os
import pickle
import time
import json
from nonebot import get_driver
from typing import Any, Optional, Set, Dict, List, Tuple, overload
from typing_extensions import Self, override
from dataclasses import dataclass, field

from .logger import logger

from .singleton import Singleton
from .config import config, PresetConfig
from .store import StoreSerializable, StoreEncoder


driver = get_driver()


@dataclass
class ImpressionData(StoreSerializable):
    """某个会话中对某个用户的印象"""
    user_id: str = field(default="")
    chat_history: List[str] = field(default_factory=list)
    """特定预设与特定用户的聊天记录，用于生成chat_impression"""
    chat_impression: str = field(default="")
    """特定预设对特定用户的印象"""


@dataclass
class PresetData(StoreSerializable):
    """特定chat_key的特定preset人格预设及其产生的聊天数据"""
    preset_key: str = field(default="")
    bot_self_introl: str = field(default="")
    is_locked: bool = field(default=False)
    """是否锁定人格，锁定后无法编辑人格"""
    is_default: bool = field(default=False)
    is_only_private: bool = field(default=False)
    """此预设是否仅限私聊"""

    # 以下为对话产生的数据
    chat_impressions: Dict[str, ImpressionData] = field(
        default_factory=dict)  # 对(群聊中)特定用户的印象
    chat_memory: Dict[str, str] = field(default_factory=dict)
    """当前预设的记忆"""

    @classmethod
    def create_from_config(cls, preset_config: PresetConfig):
        """从PresetConfig创建一个PresetData实例"""
        preset_data = PresetData(**preset_config.dict())
        return preset_data

    def reset_to_default(self, preset_config: Optional[PresetConfig]):
        """清空数据，并将人格设定为config_data中的值(如果存在的话)"""
        if preset_config is not None:
            if preset_config.preset_key != self.preset_key:
                raise Exception(
                    f"wrong preset key, expect `{self.preset_key}` but get `{preset_config.preset_key}`"
                )

            self.is_locked = preset_config.is_locked
            self.is_default = preset_config.is_default
            self.is_only_private = preset_config.is_only_private
        else:
            self.is_locked = False
            self.is_default = False
            self.is_only_private = False

        self.chat_impressions.clear()
        self.chat_memory.clear()

    @override
    def _init_from_dict(self, self_dict: Dict[str, Any]) -> Self:
        super()._init_from_dict(self_dict)

        # 实例化深层数据
        self.chat_impressions = {
            k: ImpressionData._load_from_dict(v)
            for k, v in self.chat_impressions.items()
        }
        return self


@dataclass
class ChatData(StoreSerializable):
    """用户聊天数据(群，私聊)"""
    chat_key: str = field(default="")
    """group_123456, private_123456"""
    is_enable: bool = field(default=True)
    """是否启用会话"""
    enable_auto_switch_identity: bool = field(
        default=config.NG_ENABLE_AWAKE_IDENTITIES)
    """是否允许自动切换人格"""
    active_preset: str = field(default="")
    """当前 preset_name"""
    preset_datas: Dict[str, PresetData] = field(default_factory=lambda: {})
    """[preset_name, data]"""

    # 以下为对话产生的数据
    chat_history: List[str] = field(default_factory=lambda: [])
    """当前会话的全局对话历史"""
    chat_summarized: str = field(default="")
    """总结"""

    def reset(self):
        """重置当前会话历史数据"""
        self.chat_history.clear()
        self.chat_summarized = ''

        for k, v in self.preset_datas.items():
            v.reset_to_default(preset_config=config.PRESETS.get(k, None))

    @override
    def _init_from_dict(self, self_dict: Dict[str, Any]) -> Self:
        super()._init_from_dict(self_dict)

        # 实例化深层数据
        self.preset_datas = {
            k: PresetData._load_from_dict(v)
            for k, v in self.preset_datas.items()
        }
        return self


class PersistentDataManager(Singleton["PersistentDataManager"]):
    """用户聊天(群，私聊)持久化数据管理器"""

    # chat相关数据和行为请通过调用Chat/ChatManager类相关函数实现，禁止直接操纵本类数据, 否则会丢失数据同步

    _datas: Dict[str, ChatData] = {}
    _last_save_data_time: float = 0
    _file_path: str
    _inited: bool
    _filename = "naturel_gpt"

    def backup_file(self, suffix: str):
        base_path = config.NG_DATA_PATH
        file_path = os.path.join(base_path, self._filename)
        if not os.path.isfile(f"{file_path}{suffix}"):
            return
        i = 0
        while os.path.exists(f"{file_path}.{suffix}.{i}.bak"):
            i += 1

        try:
            os.rename(f"{file_path}{suffix}", f"{file_path}.{suffix}.{i}.bak")
        except Exception as e:
            logger.warning(f"文件`{file_path}{suffix}`备份失败，可能导致数据异常或丢失！")

    def _compatibility_load(self) -> bool:
        """兼容性加载，用于支持NG_DATA_PICKLE随时切换，加载成功返回True"""
        base_path = config.NG_DATA_PATH
        file_path = os.path.join(base_path, f"{self._filename}")

        if os.path.exists(f"{file_path}.pkl") and os.path.exists(
                f"{file_path}.json"):
            logger.warning("警告，pkl文件与json同时存在，仅加载对应模式文件！")
            return False

        if config.NG_DATA_PICKLE:
            if not os.path.exists(file_path + ".json"):
                # 没有需要兼容性处理的文件
                return False
        else:
            if not os.path.exists(file_path + ".pkl"):
                # 没有需要兼容性处理的文件
                return False


        # 兼容性加载（含数据迁移与源文件备份）
        if not config.NG_DATA_PICKLE:
            self._load_from_file_pickle()
            self._file_path = file_path + ".json"
            self.save_to_file()
            self.backup_file(".pkl")
        else:
            self._load_from_file_json()
            self._file_path = file_path + ".pkl"
            self.save_to_file()
            self.backup_file(".json")

        return True

    def _load_from_file_pickle(self):
        base_path = config.NG_DATA_PATH

        file_path = os.path.join(base_path, f"{self._filename}.pkl")
        self._file_path = file_path

        if not os.path.exists(file_path):
            if not os.path.exists(config.NG_DATA_PATH):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            logger.info("找不到历史数据，初始化成功(pickle)")
            return

        with open(file_path, 'rb') as f:
            self._datas = pickle.load(f)  # 读取历史数据pickle文件
            logger.info("读取历史数据成功(pickle)")

    def _load_from_file_json(self):
        base_path = config.NG_DATA_PATH
        file_path = os.path.join(base_path, f"{self._filename}.json")
        self._file_path = file_path
        if not os.path.exists(file_path):
            if not os.path.exists(config.NG_DATA_PATH):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            return

        with open(file_path, 'r', encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise Exception(
                    f"File `{self._file_path}` load error! Data not dict!")

            self._datas = {
                k: ChatData._load_from_dict(v)
                for k, v in data.items()
            }
            logger.info("读取历史数据成功")

    def load_from_file(self):
        """使用json从文件中载入数据(兼容pickle)"""
        self._inited = False
        self._datas = {}
        if not self._compatibility_load():
            if config.NG_DATA_PICKLE:
                self._load_from_file_pickle()
            else:
                self._load_from_file_json()
        self._last_save_data_time = 0
        self._inited = True

    @property
    def is_inited(self) -> bool:
        return self._inited

    def _save_to_file_pickle(self):
        """保存到pickle文件"""
        with open(self._file_path, 'wb') as f:
            pickle.dump(self._datas, f)

    def _save_to_file_json(self):
        """保存到json文件"""
        with open(self._file_path, mode='w', encoding="utf-8") as fw:
            json.dump(self._datas,
                      fw,
                      ensure_ascii=False,
                      sort_keys=True,
                      indent=2,
                      cls=StoreEncoder)

    def save_to_file(self, must_save: bool = False):
        """使用pickle将用户数据保存到文件"""
        # 如果距离上次保存时间不足60秒则不保存
        if not must_save and time.time() - self._last_save_data_time < 60:
            return

        if config.NG_DATA_PICKLE:
            self._save_to_file_pickle()
        else:
            self._save_to_file_json()

        self._last_save_data_time = time.time()
        logger.info("数据保存成功")

    def get_all_chat_keys(self) -> List[str]:
        """获取所有的chat_key"""
        return list(self._datas.keys())

    def get_all_chat_datas(self) -> List[ChatData]:
        """获取所有的ChatData"""
        return list(self._datas.values())

    def get_preset_names(self, chat_key: str):
        """获取指定chat_key的人格名称列表"""
        return self._datas[chat_key].preset_datas.keys(
        ) if chat_key in self._datas else []

    def get_or_create_chat_data(self, chat_key: str) -> ChatData:
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


@driver.on_shutdown
async def _():
    # 保证正常结束时可以进行完整存档
    logger.info("正在保存数据，完成前请勿强制结束！")
    PersistentDataManager.instance.save_to_file(must_save=True)
    logger.info("保存完成！")
