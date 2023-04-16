import json
import re
from typing import Type
from nonebot import on_message, on_notice
from .logger import logger
from nonebot.matcher import Matcher

from .config import *
from .utils import *
from .chat import Chat
from .persistent_data_manager import PersistentDataManager
from .chat_manager import ChatManager
from .command_func import cmd
from .matcher import *


permission_check_func:Callable[[Matcher, Event, Bot, Optional[str], str], Awaitable[Tuple[bool,Optional[str]]]]

if config.ENABLE_MC_CONNECT:
    try:
        from nonebot.adapters.spigot.bot import Bot as SpigotBot
        from nonebot.adapters.spigot.event import Event as SpigotEvent
    except:
        logger.warning('未安装 nonebot_plugin_spigot 适配器，无法使用 SpigotBot')
        config.ENABLE_MC_CONNECT = False

if config.ENABLE_MC_CONNECT:
    from nonebot.adapters.spigot.bot import Bot as SpigotBot
    from nonebot.adapters.spigot.event import Event as SpigotEvent
    
    # 注册MC消息响应器
    mc_matcher:Type[Matcher] = on_message(priority=config.NG_MSG_PRIORITY-2, block=False)
    @mc_matcher.handle()
    async def _(matcher_:Matcher, event: SpigotEvent, bot:SpigotBot) -> None:
        server_from = event.server_name
        try:
            ejson_dict = json.loads(event.json())
            sender_name = ejson_dict['player']['nickname']
            chat_text = str(event.get_message())
        except Exception as e:
            logger.warning(f"[MC: {server_from}] 获取消息发送者信息失败: {e} 跳过处理...")
            return

        # 判断用户账号是否被屏蔽
        if sender_name in config.FORBIDDEN_USERS:
            if config.DEBUG_LEVEL > 0: logger.info(f"用户 {sender_name} 被屏蔽，拒绝处理消息")
            return

        resTmplate = (  # 测试用，获取消息的相关信息
            f"收到消息: {chat_text}"
            f"\n消息描述: {event.get_event_description()}"
            f"\n发送者: {sender_name}"
            f"\n消息来源: {server_from}"
            f"\nJSON: {event.json()}"
        )
        if config.DEBUG_LEVEL > 1: logger.info(resTmplate)

        # 如果是忽略前缀 或者 消息为空，则跳过处理
        if chat_text.strip().startswith(config.IGNORE_PREFIX) or not chat_text:   
            if config.DEBUG_LEVEL > 1: logger.info("忽略前缀或消息为空，跳过处理...") # 纯图片消息也会被判定为空消息
            return

        # 判断消息来源
        if isinstance(event, SpigotEvent):
            chat_key = 'MC_Server_' + server_from
            chat_type = 'server'
        else:
            if config.DEBUG_LEVEL > 0: logger.info("未知消息来源: " + event.get_session_id())
            return

        #region 指令处理分支 (由于Spigot适配器似乎不支持指令，所以整合进消息响应流)
        command_prefix_check = False
        raw_cmd = ''
        for prefix in config.MC_COMMAND_PREFIX:
            if chat_text.startswith(prefix):
                command_prefix_check = True
                raw_cmd = chat_text[len(prefix):].strip()
                break

        if command_prefix_check:
            if config.DEBUG_LEVEL > 0: logger.info(f"接收到指令: {raw_cmd} | 来源: {chat_key} (MC) | 发送者: {sender_name})")
            # 判断是否是禁止使用的用户
            if sender_name in config.FORBIDDEN_USERS:
                await mc_matcher.finish(f"您的账号({sender_name})已被禁用，请联系管理员。")

            chat:Chat = ChatManager.instance.get_or_create_chat(chat_key=chat_key)
            chat_presets_dict = chat.chat_data.preset_datas

            # 执行命令前先检查权限
            if sender_name not in config.ADMIN_USERID:
                await mc_matcher.finish("对不起！你没有权限进行此操作 ＞﹏＜")

            # 执行命令
            res = cmd.execute(
                chat=chat,
                command=raw_cmd,
                chat_presets_dict=chat_presets_dict,
            )

            if res:
                if res.get('msg'):     # 如果有返回消息则发送
                    await mc_matcher.send(str(res.get('msg')))  
                elif res.get('error'):
                    await mc_matcher.finish(f"执行命令时出现错误: {res.get('error')}")  # 如果有返回错误则发送s

            else:
                await mc_matcher.finish("输入的命令好像有点问题呢... 请检查下再试试吧！ ╮(>_<)╭")

            if res.get('is_progress'): # 如果有编辑进度，进行数据保存
                # 更新所有全局预设到会话预设中
                if config.DEBUG_LEVEL > 0: logger.info(f"用户: {sender_name} 进行了人格预设编辑: {cmd}")
                PersistentDataManager.instance.save_to_file()  # 保存数据
            return
        #endregion

        # 进行消息响应
        await do_msg_response(
            sender_name,
            chat_text,
            event.is_tome(),
            mc_matcher,
            chat_type,
            chat_key,
            sender_name,
        )


    # 注册MC通知响应器
    mc_notice_matcher:Type[Matcher] = on_notice(priority=20, block=False)
    @mc_notice_matcher.handle()
    async def _(matcher_:Matcher, event: SpigotEvent, bot:SpigotBot) -> None:
        server_from = event.server_name
        try:
            event_description = event.get_event_description()
        except Exception as e:
            logger.warning(f"[MC: {server_from}] 获取消息发送者信息失败: {e} 跳过处理...")
            return

        # 判断消息来源
        if isinstance(event, SpigotEvent):
            chat_key = 'MC_Server_' + server_from
            chat_type = 'server'
        else:
            if config.DEBUG_LEVEL > 0: logger.info("未知消息来源: " + event.get_session_id())
            return
        
        # 使用正则从消息："Notice {event_name} from {user_name}@[Server:{self.server_name}]: {event_name}" 中提取出玩家名和事件名(Join/Leave)
        try:
            event_name = event_description.split(']:')[1].strip()
            user_name = re.search(r'from (.+?)@', event_description).group(1) # type: ignore
        except Exception as e:
            logger.warning(f"[MC: {server_from}] 正则提取消息内容失败: {e} 跳过处理...")
            return
        
        wake_up = False

        if event_name == 'Join':
            notice_text = f'玩家: "{user_name}" 加入了服务器!'
            wake_up = True
        elif event_name == 'Quit':
            notice_text = f'玩家: "{user_name}" 离开了服务器!'
        elif event_name == 'Death':
            notice_text = f'玩家: "{user_name}" 死于意外!'
            wake_up = True
        else:
            notice_text = ''

        # 进行消息响应
        await do_msg_response(
            user_name,
            notice_text,
            False,
            mc_notice_matcher,
            chat_type,
            chat_key,
            '[Minecraft Server]',
            wake_up
        )
