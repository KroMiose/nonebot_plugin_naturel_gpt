from typing import Dict, List, Tuple

from nonebot.params import Matcher
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.rule import Rule
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER

from .config import *

def to_me():
    if config.NG_TO_ME:
        from nonebot.rule import to_me

        return to_me()

    async def _to_me() -> bool:
        return True

    return Rule(_to_me)

async def identity_mofify_check(matcher:Matcher, event: MessageEvent, bot:Bot, cmd:str, type:str = 'cmd') -> Tuple[bool, str]:
    """默认权限检查函数"""
    if cmd is None:
        return (True, None)
    
    if event.user_id == int(bot.self_id):
        return (True, None)

    args:List[str] = cmd.split(' ')
    if(len(args) == 0):
        return (True, None)
    elif(len(args) >= 1):
        is_super_user = str(event.user_id) in config.ADMIN_USERID
        is_admin = is_super_user or await (GROUP_ADMIN | GROUP_OWNER | SUPERUSER)(bot, event)

        common_cmd = ['', '查询', 'query', '设定', 'set', '更新', 'update', 'edit', '添加', 'new']
        super_cmd = ['admin', '删除', 'del', 'delete',
                       '锁定', 'lock', '解锁', 'unlock', '拓展', 'ext', '开启', 'on', '关闭', 'off', '重置', 'reset', 'debug', '会话', 'chats',
                       '记忆', 'memory']
        
        cmd = args[0]
        if cmd in common_cmd:
            return (is_admin, None if is_admin else '权限不足，只有管理员才允许使用此指令')
        elif cmd in super_cmd:
            return (is_super_user, None if is_super_user else '只有超级管理员才允许使用此指令')
        else:
            return (True, None)
    else:
        return (True, None)
    
