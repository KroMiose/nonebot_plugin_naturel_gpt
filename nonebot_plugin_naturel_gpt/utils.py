from typing import Dict, List, Tuple

from nonebot.params import Matcher
from nonebot.adapters.onebot.v11 import Bot, MessageEvent

from .config import *

async def identity_mofify_check(matcher:Matcher, event: MessageEvent, bot:Bot, cmd:str, type:str = 'cmd') -> Tuple[bool, str]:
    """默认权限检查函数"""
    if cmd is None:
        return (True, None)
    
    if event.sender.user_id == int(bot.self_id):
        return (True, None)

    args:List[str] = cmd.split(' ')
    if(len(args) == 0):
        return (True, None)
    elif(len(args) >= 1):
        if args[0] in ['admin', '设定','set', '更新','update','edit','添加','new', '删除','del','delete',
                       '锁定','lock','解锁','unlock','开启','on', '关闭','off','重置','reset','debug','会话','chats',
                       '记忆','memory']:
            success = str(event.user_id) in config['ADMIN_USERID']
            return (success, None if success else '只有超级管理员才允许使用此指令')
        return (True, None)
    else:
        return (True, None)
    
