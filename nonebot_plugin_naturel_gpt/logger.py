import nonebot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loguru import Record


def __path(record: "Record"):
    record["name"] = "NG聊天"


logger = nonebot.logger.bind()
logger = logger.patch(__path)
