from typing import Dict, List, Tuple, Union
import asyncio, requests

from nonebot.params import Matcher
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.rule import Rule
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, PrivateMessageEvent, GroupMessageEvent, MessageSegment, GroupIncreaseNoticeEvent

from .config import *

def to_me():
    if config.NG_TO_ME:
        from nonebot.rule import to_me

        return to_me()

    async def _to_me() -> bool:
        return True

    return Rule(_to_me)

async def default_permission_check_func(matcher:Matcher, event: MessageEvent, bot:Bot, cmd:str, type:str = 'cmd') -> Tuple[bool, str]:
    """默认权限检查函数"""
    if cmd is None: # 非命令调用
        return (True, None)
    
    if event.user_id == int(bot.self_id): # bot 在控制自己，永远有权限
        return (True, None)
    
    cmd_list = [c.strip() for c in cmd.split(' ') if c.strip()]
    if(len(cmd_list) == 0): # rg
        return (True, None)
    
    is_super_user = str(event.user_id) in config.ADMIN_USERID or await (SUPERUSER)(bot, event)
    is_admin = is_super_user or isinstance(event, PrivateMessageEvent) or await (GROUP_ADMIN | GROUP_OWNER)(bot, event) # 超级管理员，私聊，群主，群管理，均视为admin

    common_cmd = ['', '查询', 'query', '设定', 'set', '更新', 'update', 'edit', '添加', 'new', '开启', 'on', '关闭', 'off', '重置', 'reset']
    super_cmd = ['admin', '删除', 'del', 'delete', '锁定', 'lock', '解锁', 'unlock', '扩展', 'ext',  'debug', '会话', 'chats', '记忆', 'memory']
    
    cmd_0 = cmd_list[0]
    if cmd_0 in super_cmd or '-global' in cmd_list: # 超级命令或者命令中包含 `-global` 选项需要超级管理员权限
        return (is_super_user, None if is_super_user else '权限不足，只有超级管理员才允许使用此指令')
    elif cmd_0 in common_cmd:
        return (is_admin, None if is_admin else '权限不足，只有管理员才允许使用此指令')
    else:
        return (True, None)
    
async def gen_chat_text(event: MessageEvent, bot:Bot) -> str:
    """生成合适的会话消息内容(eg. 将cq at 解析为真实的名字)"""
    if not isinstance(event, GroupMessageEvent):
        return event.get_plaintext(), False
    else:
        wake_up = False
        msg = ''
        for seg in event.message:
            if seg.is_text():
                msg += seg.data.get('text', '')
            elif seg.type == 'at':
                qq = seg.data.get('qq', None)
                if qq:
                    if qq == 'all':
                        msg += '@全体成员'
                        wake_up = True
                    else:
                        user_name = await get_user_name(event=event, bot=bot,user_id=int(qq))
                        if user_name:
                            msg += f'@{user_name}' # 保持给bot看到的内容与真实用户看到的一致
        return msg, wake_up
    
async def get_user_name(event: Union[MessageEvent, GroupIncreaseNoticeEvent], bot:Bot, user_id:int) -> str:
    """获取QQ用户名，优先群名片"""
    if (isinstance(event, GroupMessageEvent) or isinstance(event, GroupIncreaseNoticeEvent)) and config.GROUP_CARD:
        user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=user_id, no_cache=False)
        user_name = user_info.get('card', None) or user_info.get('nickname', None)
    else:
        user_name = event.sender.nickname

    if user_name and config.NG_CHECK_USER_NAME_HYPHEN and ('-' in user_name): # 检查用户名中的连字符, 去掉第一个连字符之前的部分
        user_name = user_name.split('-', 1)[1].replace('-', '').strip()
        
    return user_name

async def translate(text:str, from_:str="auto", to_:str="en") -> str:
    """翻译"""
    loop = asyncio.get_event_loop()
    try:
        r = await loop.run_in_executor(None, requests.post, "https://hf.space/embed/mikeee/gradio-gtr/+/api/predict", {"data": [text, from_, to_]})
        return r.json()["data"][0]
    except:
        raise Exception("翻译 API 请求失败")