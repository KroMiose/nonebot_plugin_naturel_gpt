import os
import sqlite3
import time
from nonebot import get_driver
from typing import Any, Optional, Dict, List
from typing_extensions import Self, override
from dataclasses import dataclass, field

from .logger import logger

from .singleton import Singleton
from .config import config, PresetConfig
from .store import StoreSerializable


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
        preset_data = PresetData(**preset_config.model_dump())
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
    tmp_multimodal_context: Dict[str, List[Dict[str, Any]]] = field(
        default_factory=lambda: {"images": [], "audios": []})
    """运行时多模态上下文缓存，不写入持久化存储"""

    def reset(self):
        """重置当前会话历史数据"""
        self.chat_history.clear()
        self.chat_summarized = ''
        self.tmp_multimodal_context = {"images": [], "audios": []}

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

    def _connect(self) -> sqlite3.Connection:
        """打开SQLite连接，并启用外键约束。"""
        conn = sqlite3.connect(self._file_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_database(self, conn: sqlite3.Connection):
        """初始化SQLite表结构。"""
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chats (
                chat_key TEXT PRIMARY KEY,
                is_enable INTEGER NOT NULL,
                enable_auto_switch_identity INTEGER NOT NULL,
                active_preset TEXT NOT NULL DEFAULT '',
                chat_summarized TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS chat_history (
                chat_key TEXT NOT NULL,
                position INTEGER NOT NULL,
                message TEXT NOT NULL,
                PRIMARY KEY (chat_key, position),
                FOREIGN KEY (chat_key)
                    REFERENCES chats(chat_key)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS presets (
                chat_key TEXT NOT NULL,
                preset_key TEXT NOT NULL,
                position INTEGER NOT NULL,
                bot_self_introl TEXT NOT NULL DEFAULT '',
                is_locked INTEGER NOT NULL,
                is_default INTEGER NOT NULL,
                is_only_private INTEGER NOT NULL,
                PRIMARY KEY (chat_key, preset_key),
                FOREIGN KEY (chat_key)
                    REFERENCES chats(chat_key)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS preset_memories (
                chat_key TEXT NOT NULL,
                preset_key TEXT NOT NULL,
                memory_key TEXT NOT NULL,
                memory_value TEXT NOT NULL,
                position INTEGER NOT NULL,
                PRIMARY KEY (chat_key, preset_key, memory_key),
                FOREIGN KEY (chat_key, preset_key)
                    REFERENCES presets(chat_key, preset_key)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS user_impressions (
                chat_key TEXT NOT NULL,
                preset_key TEXT NOT NULL,
                user_id TEXT NOT NULL,
                chat_impression TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (chat_key, preset_key, user_id),
                FOREIGN KEY (chat_key, preset_key)
                    REFERENCES presets(chat_key, preset_key)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS user_impression_history (
                chat_key TEXT NOT NULL,
                preset_key TEXT NOT NULL,
                user_id TEXT NOT NULL,
                position INTEGER NOT NULL,
                message TEXT NOT NULL,
                PRIMARY KEY (chat_key, preset_key, user_id, position),
                FOREIGN KEY (chat_key, preset_key, user_id)
                    REFERENCES user_impressions(chat_key, preset_key, user_id)
                    ON DELETE CASCADE
            );
        """)
        conn.execute(
            "INSERT OR IGNORE INTO meta(key, value) VALUES('schema_version', '1')"
        )

    def _load_from_sqlite(self):
        with self._connect() as conn:
            self._init_database(conn)

            for row in conn.execute("""
                SELECT chat_key,
                       is_enable,
                       enable_auto_switch_identity,
                       active_preset,
                       chat_summarized
                  FROM chats
                 ORDER BY chat_key
            """):
                chat_data = ChatData(
                    chat_key=row["chat_key"],
                    is_enable=bool(row["is_enable"]),
                    enable_auto_switch_identity=bool(
                        row["enable_auto_switch_identity"]),
                    active_preset=row["active_preset"],
                    chat_summarized=row["chat_summarized"],
                )
                self._datas[chat_data.chat_key] = chat_data

            for row in conn.execute("""
                SELECT chat_key, position, message
                  FROM chat_history
                 ORDER BY chat_key, position
            """):
                chat_data = self._datas.get(row["chat_key"])
                if chat_data:
                    chat_data.chat_history.append(row["message"])

            for row in conn.execute("""
                SELECT chat_key,
                       preset_key,
                       bot_self_introl,
                       is_locked,
                       is_default,
                       is_only_private
                  FROM presets
                 ORDER BY chat_key, position, preset_key
            """):
                chat_data = self._datas.get(row["chat_key"])
                if not chat_data:
                    continue
                preset_data = PresetData(
                    preset_key=row["preset_key"],
                    bot_self_introl=row["bot_self_introl"],
                    is_locked=bool(row["is_locked"]),
                    is_default=bool(row["is_default"]),
                    is_only_private=bool(row["is_only_private"]),
                )
                chat_data.preset_datas[preset_data.preset_key] = preset_data

            for row in conn.execute("""
                SELECT chat_key, preset_key, memory_key, memory_value
                  FROM preset_memories
                 ORDER BY chat_key, preset_key, position, memory_key
            """):
                chat_data = self._datas.get(row["chat_key"])
                if not chat_data:
                    continue
                preset_data = chat_data.preset_datas.get(row["preset_key"])
                if preset_data:
                    preset_data.chat_memory[row["memory_key"]] = row["memory_value"]

            for row in conn.execute("""
                SELECT chat_key, preset_key, user_id, chat_impression
                  FROM user_impressions
                 ORDER BY chat_key, preset_key, user_id
            """):
                chat_data = self._datas.get(row["chat_key"])
                if not chat_data:
                    continue
                preset_data = chat_data.preset_datas.get(row["preset_key"])
                if not preset_data:
                    continue
                impression_data = ImpressionData(
                    user_id=row["user_id"],
                    chat_impression=row["chat_impression"],
                )
                preset_data.chat_impressions[impression_data.user_id] = impression_data

            for row in conn.execute("""
                SELECT chat_key, preset_key, user_id, position, message
                  FROM user_impression_history
                 ORDER BY chat_key, preset_key, user_id, position
            """):
                chat_data = self._datas.get(row["chat_key"])
                if not chat_data:
                    continue
                preset_data = chat_data.preset_datas.get(row["preset_key"])
                if not preset_data:
                    continue
                impression_data = preset_data.chat_impressions.get(row["user_id"])
                if impression_data:
                    impression_data.chat_history.append(row["message"])

            logger.info("读取历史数据成功(sqlite)")

    def load_from_file(self):
        """从SQLite文件中载入数据。"""
        self._inited = False
        self._datas = {}
        if not os.path.exists(config.NG_DATA_PATH):
            os.makedirs(config.NG_DATA_PATH, exist_ok=True)
        self._file_path = os.path.join(config.NG_DATA_PATH, f"{self._filename}.sqlite3")
        self._load_from_sqlite()
        self._last_save_data_time = 0
        self._inited = True

    @property
    def is_inited(self) -> bool:
        return self._inited

    def _save_to_sqlite(self):
        """将当前内存快照保存到SQLite文件。"""
        with self._connect() as conn:
            self._init_database(conn)
            conn.execute("DELETE FROM chats")

            for chat_data in self._datas.values():
                conn.execute("""
                    INSERT INTO chats(
                        chat_key,
                        is_enable,
                        enable_auto_switch_identity,
                        active_preset,
                        chat_summarized
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    chat_data.chat_key,
                    int(chat_data.is_enable),
                    int(chat_data.enable_auto_switch_identity),
                    chat_data.active_preset or "",
                    chat_data.chat_summarized or "",
                ))

                conn.executemany("""
                    INSERT INTO chat_history(chat_key, position, message)
                    VALUES (?, ?, ?)
                """, [
                    (chat_data.chat_key, idx, message)
                    for idx, message in enumerate(chat_data.chat_history)
                ])

                for preset_idx, preset_data in enumerate(chat_data.preset_datas.values()):
                    conn.execute("""
                        INSERT INTO presets(
                            chat_key,
                            preset_key,
                            position,
                            bot_self_introl,
                            is_locked,
                            is_default,
                            is_only_private
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        chat_data.chat_key,
                        preset_data.preset_key,
                        preset_idx,
                        preset_data.bot_self_introl or "",
                        int(preset_data.is_locked),
                        int(preset_data.is_default),
                        int(preset_data.is_only_private),
                    ))

                    conn.executemany("""
                        INSERT INTO preset_memories(
                            chat_key,
                            preset_key,
                            memory_key,
                            memory_value,
                            position
                        ) VALUES (?, ?, ?, ?, ?)
                    """, [
                        (
                            chat_data.chat_key,
                            preset_data.preset_key,
                            memory_key,
                            memory_value,
                            idx,
                        )
                        for idx, (memory_key, memory_value)
                        in enumerate(preset_data.chat_memory.items())
                    ])

                    for impression_data in preset_data.chat_impressions.values():
                        conn.execute("""
                            INSERT INTO user_impressions(
                                chat_key,
                                preset_key,
                                user_id,
                                chat_impression
                            ) VALUES (?, ?, ?, ?)
                        """, (
                            chat_data.chat_key,
                            preset_data.preset_key,
                            impression_data.user_id,
                            impression_data.chat_impression or "",
                        ))

                        conn.executemany("""
                            INSERT INTO user_impression_history(
                                chat_key,
                                preset_key,
                                user_id,
                                position,
                                message
                            ) VALUES (?, ?, ?, ?, ?)
                        """, [
                            (
                                chat_data.chat_key,
                                preset_data.preset_key,
                                impression_data.user_id,
                                idx,
                                message,
                            )
                            for idx, message
                            in enumerate(impression_data.chat_history)
                        ])

    def save_to_file(self, must_save: bool = False):
        """将用户数据保存到SQLite文件。"""
        # 如果距离上次保存时间不足60秒则不保存
        if not must_save and time.time() - self._last_save_data_time < 60:
            return

        self._save_to_sqlite()

        self._last_save_data_time = time.time()
        logger.info("数据保存成功(sqlite)")

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
