import asyncio
import random
import re
import time
import os
from typing import Awaitable, List, Dict, Callable, Optional, Set, Tuple, Type
from nonebot import on_command, on_message, on_notice
from .logger import logger
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import Message, MessageEvent, PrivateMessageEvent, GroupMessageEvent, MessageSegment, GroupIncreaseNoticeEvent

from .config import *
from .utils import *
from .chat import Chat
from .persistent_data_manager import PersistentDataManager
from .chat_manager import ChatManager
from .Extension import global_extensions
from .openai_func import TextGenerator
from .command_func import cmd
from .MCrcon.mcrcon import MCRcon   # fork from: https://github.com/Uncaught-Exceptions/MCRcon

try:
    from .text_to_image import md_to_img, text_to_img
except ImportError:
    logger.warning('未安装 nonebot_plugin_htmlrender 插件，无法使用 text_to_img')
    config.ENABLE_MSG_TO_IMG = False
    config.ENABLE_COMMAND_TO_IMG = False

permission_check_func:Callable[[Matcher, Event, Bot, Optional[str], str], Awaitable[Tuple[bool,Optional[str]]]]
is_progress:bool = False

msg_sent_set:Set[str] = set() # bot 自己发送的消息

"""消息发送钩子，用于记录自己发送的消息(默认不开启，只有在用户自定义了message_sent事件之后message_sent事件才会被发送到 on_message 回调)"""
# @Bot.on_called_api
async def handle_group_message_sent(bot: Bot, exception: Optional[Exception], api: str, data: Dict[str, Any], result: Any):
    global msg_sent_set
    if result and (api in ['send_msg', 'send_group_msg', 'send_private_msg']):
        msg_id = result.get('message_id', None)
        if msg_id:
            msg_sent_set.add(f"{bot.self_id}_{msg_id}")

""" ======== 注册消息响应器 ======== """
# 注册qq消息响应器 收到任意消息时触发
matcher:Type[Matcher] = on_message(priority=config.NG_MSG_PRIORITY, block=config.NG_BLOCK_OTHERS)
@matcher.handle()
async def handler(matcher_:Matcher, event: MessageEvent, bot:Bot) -> None:
    global msg_sent_set
    if event.post_type == 'message_sent': # 通过bot.send发送的消息不处理
        msg_key = f"{bot.self_id}_{event.message_id}"
        if msg_key in msg_sent_set:
            msg_sent_set.remove(msg_key)
            return
        
    if len(msg_sent_set) > 10:
        if config.DEBUG_LEVEL > 0: logger.warning(f"累积的待处理的自己发送消息数量为 {len(msg_sent_set)}, 请检查逻辑是否有错误")
        msg_sent_set.clear()
    
    # 处理消息前先检查权限
    (permit_success, _) = await permission_check_func(matcher_, event, bot, None, 'message')
    if not permit_success:
        return
    
    # 判断用户账号是否被屏蔽
    if event.get_user_id() in config.FORBIDDEN_USERS:
        if config.DEBUG_LEVEL > 0: logger.info(f"用户 {event.get_user_id()} 被屏蔽，拒绝处理消息")
        return
    # 判断群是否被屏蔽
    if isinstance(event, GroupMessageEvent) and str(event.group_id) in config.FORBIDDEN_GROUPS:
        if config.DEBUG_LEVEL > 0: logger.info(f"群 {event.group_id} 被屏蔽，拒绝处理消息")
        return

    sender_name = await get_user_name(event=event, bot=bot, user_id=event.user_id) or '未知'
    
    resTmplate = (  # 测试用，获取消息的相关信息
        f"收到消息: {event.get_message()}"
        f"\n消息名称: {event.get_event_name()}"
        f"\n消息描述: {event.get_event_description()}"
        f"\n消息来源: {event.get_session_id()}"
        f"\n消息文本: {event.get_plaintext()}"
        f"\n消息主体: {event.get_user_id()}"
        f"\n消息内容: {event.get_message()}"
        f"\n发送者: {sender_name}"
        f"\n是否to-me: {event.is_tome()}"
        # f"\nJSON: {event.json()}"
    )
    if config.DEBUG_LEVEL > 1: logger.info(resTmplate)

    # 如果是忽略前缀 或者 消息为空，则跳过处理
    if event.get_plaintext().strip().startswith(config.IGNORE_PREFIX) or not event.get_plaintext():   
        if config.DEBUG_LEVEL > 1: logger.info("忽略前缀或消息为空，跳过处理...") # 纯图片消息也会被判定为空消息
        return

    # 判断群聊/私聊
    if isinstance(event, GroupMessageEvent):
        chat_key = 'group_' + event.get_session_id().split("_")[1]
        chat_type = 'group'
    elif isinstance(event, PrivateMessageEvent):
        chat_key = 'private_' + event.get_user_id()
        chat_type = 'private'
    else:
        if config.DEBUG_LEVEL > 0: logger.info("未知消息来源: " + event.get_session_id())
        return
    
    chat_text, wake_up = await gen_chat_text(event=event, bot=bot)

    # 进行消息响应
    await do_msg_response(
        event.get_user_id(),
        chat_text,
        event.is_tome() or wake_up,
        matcher,
        chat_type,
        chat_key,
        sender_name,
        bot=bot,
    )

""" ======== 注册通知响应器 ======== """
# 欢迎新成员通知响应器
welcome:Type[Matcher] = on_notice(priority=20, block=False)
@welcome.handle()  # 监听 welcom
async def _(matcher_:Matcher, event: GroupIncreaseNoticeEvent, bot:Bot):  # event: GroupIncreaseNoticeEvent  群成员增加事件
    if config.DEBUG_LEVEL > 0: logger.info(f"收到通知: {event}")

    if not config.REPLY_ON_WELCOME:  # 如果不回复欢迎消息，则跳过处理
        return
    
    # 处理通知前先检查权限
    (permit_success, _) = await permission_check_func(matcher_, event, bot,None,'notice')
    if not permit_success:
        return

    if isinstance(event, GroupIncreaseNoticeEvent): # 群成员增加通知
        chat_key = 'group_' + event.get_session_id().split("_")[1]
        chat_type = 'group'
    else:
        if config.DEBUG_LEVEL > 0: logger.info(f"未知通知来源: {event.get_session_id()} 跳过处理...")
        return

    resTmplate = (  # 测试用，获取消息的相关信息
        f"会话: {chat_key}"
        f"\n通知来源: {event.get_user_id()}"
        f"\n是否to-me: {event.is_tome()}"
        f"\nDict: {event.dict()}"
        f"\nJSON: {event.json()}"
    )
    if config.DEBUG_LEVEL > 0: logger.info(resTmplate)

    user_name = await get_user_name(event=event, bot=bot, user_id=int(event.get_user_id())) or f'qq:{event.get_user_id()}'

    # 进行消息响应
    await do_msg_response(
        event.get_user_id(),
        f'{user_name} has joined the group, welcome!',
        event.is_tome(),
        welcome,
        chat_type,
        chat_key,
        '[System]',
        True,
        bot=bot,
    )

""" ======== 注册指令响应器 ======== """
# QQ:人格设定指令 用于设定人格的相关参数
identity:Type[Matcher] = on_command("identity", aliases={"人格设定", "人格", "rg"}, rule=to_me(), priority=config.NG_MSG_PRIORITY - 1, block=True)
@identity.handle()
async def _(matcher_:Matcher, event: MessageEvent, bot:Bot, arg: Message = CommandArg()):
    global is_progress  # 是否产生编辑进度
    is_progress = False
    # 判断是否是禁止使用的用户
    if event.get_user_id() in config.FORBIDDEN_USERS:
        await identity.finish(f"您的账号({event.get_user_id()})已被禁用，请联系管理员。")

    # 判断群聊/私聊
    if isinstance(event, GroupMessageEvent):
        chat_key = 'group_' + event.get_session_id().split("_")[1]
    elif isinstance(event, PrivateMessageEvent):
        chat_key = 'private_' + event.get_user_id()
    else:
        if config.DEBUG_LEVEL > 0: logger.info("未知消息来源: " + event.get_session_id())
        return

    chat:Chat = ChatManager.instance.get_or_create_chat(chat_key=chat_key)
    chat_presets_dict = chat.chat_data.preset_datas

    raw_cmd:str = arg.extract_plain_text()
    if config.DEBUG_LEVEL > 0: logger.info(f"接收到指令: {raw_cmd} | 来源: {chat_key}")
    
    '\n'.join([f'  -> {k + " (当前)" if k == chat.preset_key else k}' for k in chat_presets_dict.keys()])

    # 执行命令前先检查权限
    (permit_success, permit_msg) = await permission_check_func(matcher_, event,bot,raw_cmd,'cmd')
    if not permit_success:
        await identity.finish(permit_msg if permit_msg else "对不起！你没有权限进行此操作 ＞﹏＜")

    # 执行命令 *取消注释下列行以启用新的命令执行器*
    res = cmd.execute(
        chat=chat,
        command='rg '+ raw_cmd,
        chat_presets_dict=chat_presets_dict,
    )

    if res:
        if res.get('msg'):     # 如果有返回消息则发送
            if config.ENABLE_COMMAND_TO_IMG:
                img = await text_to_img(res.get('msg')) # type: ignore
                await identity.send(MessageSegment.image(img))
            else:
                await identity.send(str(res.get('msg')))
        elif res.get('error'):
            await identity.finish(f"执行命令时出现错误: {res.get('error')}")  # 如果有返回错误则发送s

    else:
        await identity.finish("输入的命令好像有点问题呢... 请检查下再试试吧！ ╮(>_<)╭")

    if res.get('is_progress'): # 如果有编辑进度，进行数据保存
        # 更新所有全局预设到会话预设中
        if config.DEBUG_LEVEL > 0: logger.info(f"用户: {event.get_user_id()} 进行了人格预设编辑: {cmd}")
        PersistentDataManager.instance.save_to_file()  # 保存数据
    return


""" ======== 消息响应方法 ======== """
async def do_msg_response(trigger_userid:str, trigger_text:str, is_tome:bool, matcher: Type[Matcher], chat_type: str, chat_key: str, sender_name: Optional[str] = None, wake_up: bool = False, loop_times=0, loop_data={}, bot:Bot = None): # type: ignore
    """消息响应方法"""

    sender_name = sender_name or 'anonymous'
    chat:Chat = ChatManager.instance.get_or_create_chat(chat_key=chat_key)

    # 判断对话是否被禁用
    if not chat.is_enable:
        if config.DEBUG_LEVEL > 1: logger.info("对话已被禁用，跳过处理...")
        return

    # 检测是否包含违禁词
    for w in config.WORD_FOR_FORBIDDEN:
        if str(w).lower() in trigger_text.lower():
            if config.DEBUG_LEVEL > 0: logger.info(f"检测到违禁词 {w}，拒绝处理...")
            return

    # 唤醒词检测
    for w in config.WORD_FOR_WAKE_UP:
        if str(w).lower() in trigger_text.lower():
            wake_up = True
            break

    # 随机回复判断
    if random.random() < config.RANDOM_CHAT_PROBABILITY:
        wake_up = True

    # 其它人格唤醒判断
    if chat.preset_key.lower() not in trigger_text.lower() and chat.enable_auto_switch_identity:
        for preset_key in chat.preset_keys:
            if preset_key.lower() in trigger_text.lower():
                chat.change_presettings(preset_key)
                logger.info(f"检测到 {preset_key} 的唤醒词，切换到 {preset_key} 的人格")
                if chat_type != 'server':
                    await matcher.send(f'[NG] 已切换到 {preset_key} (￣▽￣)-ok !')
                wake_up = True
                break

    current_preset_key = chat.preset_key

    # 判断是否需要回复
    if (    # 如果不是 bot 相关的信息，则直接返回
        wake_up or \
        (config.REPLY_ON_NAME_MENTION and (chat.preset_key.lower() in trigger_text.lower())) or \
        (config.REPLY_ON_AT and is_tome)
    ):
        # 更新全局对话历史记录
        # chat.update_chat_history_row(sender=sender_name, msg=trigger_text, require_summary=True)
        await chat.update_chat_history_row(sender=sender_name,
                                    msg=f"@{chat.preset_key} {trigger_text}" if is_tome and chat_type=='group' else trigger_text,
                                    require_summary=False, record_time=True)    # 只有在需要回复时才记录时间，用于节流
        logger.info("符合 bot 发言条件，进行回复...")
    else:
        if config.CHAT_ENABLE_RECORD_ORTHER:
            await chat.update_chat_history_row(sender=sender_name, msg=trigger_text, require_summary=False, record_time=False)
            if config.DEBUG_LEVEL > 1: logger.info("不是 bot 相关的信息，记录但不进行回复")
        else:
            if config.DEBUG_LEVEL > 1: logger.info("不是 bot 相关的信息，不进行回复")
        return
    
    wake_up = False # 进入对话流程，重置唤醒状态

    # 记录对用户的对话信息
    await chat.update_chat_history_row_for_user(sender=sender_name, msg=trigger_text, userid=trigger_userid, username=sender_name, require_summary=False)

    if chat.preset_key != current_preset_key:
        if config.DEBUG_LEVEL > 0: logger.warning(f'等待OpenAI请求返回的过程中人格预设由[{current_preset_key}]切换为[{chat.preset_key}],当前消息不再继续响应.1')
        return
    
    # 节流判断 接收到消息后等待一段时间，如果在这段时间内再次收到消息，则跳过响应处理
    # 效果表现为：如果在一段时间内连续收到消息，则只响应最后一条消息
    last_recv_time = chat.last_msg_time
    await asyncio.sleep(config.REPLY_THROTTLE_TIME)
    if last_recv_time != chat.last_msg_time: # 如果最后一条消息时间不一致，说明在节流时间内收到了新消息，跳过处理
        if config.DEBUG_LEVEL > 0: logger.info('节流时间内收到新消息，跳过处理...')
        return
    
    # 主动聊天参与逻辑 *待定方案
    # 达到一定兴趣阈值后，开始进行一次启动发言准备 收集特定条数的对话历史作为发言参考
    # 启动发言后，一段时间内兴趣值逐渐下降，如果随后被呼叫，则兴趣值提升
    # 监测对话历史中是否有足够的话题参与度，如果有，则继续提高话题参与度，否则，降低话题参与度
    # 兴趣值影响发言频率，兴趣值越高，发言频率越高
    # 如果监测到对话记录中有不满情绪(如: 闭嘴、滚、不理你、安静等)，则大幅降低兴趣值并且降低发言频率，同时进入一段时间的沉默期(0-120分钟)
    # 沉默期中降低响应"提及"的概率，沉默期中被直接at，则恢复一定兴趣值提升兴趣值并取消沉默期
    # 兴趣值会影响回复的速度，兴趣值越高，回复速度越快
    # 发言概率贡献比例 = (随机值: 10% + 话题参与度: 50% + 兴趣值: 40%) * 发言几率基数(0.01~1.0)

    sta_time:float = time.time()

    # 生成对话 prompt 模板
    prompt_template = chat.get_chat_prompt_template(userid=trigger_userid, chat_type=chat_type)
    # 生成 log 输出用的 prompt 模板
    log_prompt_template = '\n'.join([f"[{m['role']}]\n{m['content']}\n" for m in prompt_template]) if isinstance(prompt_template, list) else prompt_template
    if config.DEBUG_LEVEL > 0:
        # logger.info("对话 prompt 模板: \n" + str(log_prompt_template))
        # 保存 prompt 模板到日志文件
        with open(os.path.join(config.NG_LOG_PATH, f"{chat_key}.{time.strftime('%Y-%m-%d %H-%M-%S')}.prompt.log"), 'a', encoding='utf-8') as f:
            f.write(f"prompt 模板: \n{log_prompt_template}\n")
        logger.info(f"对话 prompt 模板已保存到日志文件: {chat_key}.{time.strftime('%Y-%m-%d %H-%M-%S')}.prompt.log")

    chat.update_gen_time()  # 更新上次生成时间
    time_before_request = time.time()
    tg = TextGenerator.instance
    raw_res, success = await tg.get_response(prompt=prompt_template, type='chat', custom={'bot_name': chat.preset_key, 'sender_name': sender_name})  # 生成对话结果
    if not success:  # 如果生成对话结果失败，则直接返回
        logger.warning("生成对话结果失败，跳过处理...")
        await matcher.finish(raw_res)

    # 如果生成对话结果过程中启动了新的消息生成，则放弃本次生成结果
    if chat.last_gen_time > time_before_request:
        logger.warning("生成对话结果过程中启动了新的消息生成，放弃本次生成结果...")
        return

    # 输出对话原始响应结果
    if config.DEBUG_LEVEL > 0: logger.info(f"原始回应: {raw_res}")

    if time.time() - time_before_request > config.OPENAI_TIMEOUT:
        logger.warning(f'OpenAI响应超过timeout值[{config.OPENAI_TIMEOUT}]，停止处理')
        return

    if chat.preset_key != current_preset_key:
        if config.DEBUG_LEVEL > 0: logger.warning(f'等待OpenAI响应返回的过程中人格预设由[{current_preset_key}]切换为[{chat.preset_key}],当前消息不再继续处理.2')
        return

    # 用于存储最终回复顺序内容的列表
    reply_list:List[Union[str, dict]] = []

    # 预检一次响应内容，如果响应内容中包含了需要打断的扩展调用指令，则直接截断原始响应中该扩展调用指令后的内容
    pre_check_calls = re.findall(r"/#(.+?)#/", raw_res, re.S)
    if pre_check_calls:
        for call_str in pre_check_calls:
            ext_name, *ext_args = call_str.split('&')
            ext_name = ext_name.strip().lower()
            if ext_name in global_extensions and global_extensions[ext_name].get_config().get('interrupt', False):
                # 获取该扩展调用指令结束在原始响应中的位置
                call_end_pos = raw_res.find(f"/#{call_str}#/") + len(f"/#{call_str}#/")
                # 截断原始响应内容
                raw_res = raw_res[:call_end_pos]
                if config.DEBUG_LEVEL > 0: logger.warning(f"检测到需要打断的扩展调用指令: {call_str}, 已截断原始响应内容")
                break

    # 提取markdown格式的代码块
    re.findall(r"```(.+?)```", raw_res, re.S)
    # 提取后去除所有markdown格式的代码块，剩余部分为对话结果
    talk_res = re.sub(r"```(.+?)```", '', raw_res)

    # 分割对话结果提取出所有 "/#扩展名&参数1&参数2#/" 格式的扩展调用指令 参数之间用&分隔 多行匹配
    ext_calls = re.findall(r"/.?#(.+?)#.?/", talk_res, re.S)

    # 对分割后的对话根据 '*;' 进行分割，表示对话结果中的分句，处理结果为列表，其中每个元素为一句话
    if config.NG_ENABLE_MSG_SPLIT:
        # 提取后去除所有扩展调用指令并切分信息，剩余部分为对话结果 多行匹配
        talk_res = re.sub(r"/.?#(.+?)#.?/", '*;', talk_res)
        reply_list.extend(talk_res.split('*;'))
    else:
        # 提取后去除所有扩展调用指令，剩余部分为对话结果 多行匹配
        talk_res = re.sub(r"/.?#(.+?)#.?/", '', talk_res)
        reply_list.append(talk_res)

    # if config.DEBUG_LEVEL > 0: logger.info("分割响应结果: " + str(reply_list))

    # 重置所有扩展调用次数
    for ext_name in global_extensions.keys():
        global_extensions[ext_name].reset_call_times()

    # 遍历所有扩展调用指令
    for ext_call_str in ext_calls:  
        ext_name, *ext_args = ext_call_str.split('&')
        ext_name = ext_name.strip().lower()
        if ext_name in global_extensions.keys():
            # 提取出扩展调用指令中的参数为字典
            ext_args_dict:dict = {}
            # 按照参数顺序依次提取参数值
            arguments = global_extensions[ext_name].get_config().get('arguments')
            if arguments and isinstance(arguments, dict):
                for arg_name in arguments.keys():
                    if len(ext_args) > 0:
                        ext_args_dict[arg_name] = ext_args.pop(0)
                    else:
                        ext_args_dict[arg_name] = None

            logger.info(f"检测到扩展调用指令: {ext_name} {ext_args_dict} | 正在调用扩展模块...")
            try:    # 调用扩展的call方法
                ext_res = await global_extensions[ext_name].call(ext_args_dict, {
                    'bot_name': chat.preset_key,
                    'user_send_raw_text': trigger_text,
                    'bot_send_raw_text': raw_res
                })
                if config.DEBUG_LEVEL > 1: logger.info(f"扩展 {ext_name} 返回结果: {ext_res}")
                if ext_res is not None:
                    # 将扩展返回的结果插入到回复列表的最后
                    reply_list.append(ext_res)
            except Exception as e:
                logger.error(f"调用扩展 {ext_name} 时发生错误: {e!r}")
                if config.DEBUG_LEVEL > 0: logger.opt(exception=e).exception(f"[扩展 {ext_name}] 错误详情:")
                ext_res = {}
                # 将错误的调用指令从原始回复中去除，避免bot从上下文中学习到错误的指令用法
                raw_res = re.sub(r"/.?#(.+?)#.?/", '', raw_res)
        else:
            logger.error(f"未找到扩展 {ext_name}，跳过调用...")
            # 将错误的调用指令从原始回复中去除，避免bot从上下文中学习到错误的指令用法
            raw_res = re.sub(r"/.?#(.+?)#.?/", '', raw_res)

    # # 代码块插入到回复列表的最后
    # for code_block in code_blocks:
    #     reply_list.append({'code_block': code_block})

    if config.DEBUG_LEVEL > 1: logger.info(f"回复序列内容: {reply_list}")

    # 回复前缀
    reply_prefix = f'<{chat.preset_key}> ' if (chat_type == 'server') else ''

    res_times = config.NG_MAX_RESPONSE_PER_MSG  # 获取每条消息最大回复次数
    # 根据回复内容列表逐条发送回复
    for idx, reply in enumerate(reply_list):
        # 判断回复内容是否为str
        if isinstance(reply, str):
            # 判断文本内容是否为纯符号(包括空格，换行、英文标点、中文标点)并且长度小于3
            reply_text = str(reply).strip()
            if re.match(r'^[^\u4e00-\u9fa5\w]{1}$', reply_text) or len(reply_text) < 1:
                if config.DEBUG_LEVEL > 0: logger.info(f"检测到纯符号或空文本: {reply_text}，跳过发送...")
                continue
            if config.ENABLE_MSG_TO_IMG:
                img = await md_to_img(reply_text)
                await matcher.send(MessageSegment.image(img))
            else:
                await matcher.send(f"{reply_prefix}{reply_text}")
        elif isinstance(reply, dict):
            for key in reply:   # 遍历回复内容类型字典
                if not reply.get(key):
                    continue
                
                reply_content = reply.get(key)
                reply_text = str(reply_content).strip() if isinstance(reply_content, str) else ''
                if key == 'text': # 发送普通文本
                    # 判断文本内容是否为纯符号(包括空格，换行、英文标点、中文标点)并且长度为1
                    if re.match(r'^[^\u4e00-\u9fa5\w]{1}$', reply_text):
                        if config.DEBUG_LEVEL > 1: logger.info(f"检测到纯符号文本: {reply_text}，跳过发送...")
                        continue
                    if not reply_text.strip():
                        continue
                    await matcher.send(f"{reply_prefix}{reply_text}")

                elif key == 'image': # 发送图片
                    await matcher.send(MessageSegment.image(file=reply_content or ''))
                    logger.info(f"回复图片消息: {reply_content}")

                elif key == 'file':  # 发送文件
                    # await matcher.send(MessageSegment.file(file=reply_content or ''))
                    try:
                        await bot.call_api('upload_group_file', group_id=chat.chat_key.split('_')[1], file=reply_content, name=reply_content.split('/')[-1])    # type: ignore
                    except Exception as e:
                        logger.error(f"尝试上传文件失败: {e}")
                    logger.info(f"回复文件消息: {reply_content}")

                elif key == 'voice': # 发送语音
                    logger.info(f"回复语音消息: {reply_content}")
                    await matcher.send(Message(MessageSegment.record(file=reply_content, cache=False))) # type: ignore

                elif key == 'code_block':  # 发送代码块
                    await matcher.send(Message(reply_text))

                elif key == 'memory':  # 记忆存储
                    logger.info(f"存储记忆: {reply_content}")
                    if isinstance(reply_content, dict):
                        memory:Dict[str, str] = reply_content
                        chat.set_memory(memory.get('key', ''), memory.get('value', ''))
                        if config.DEBUG_LEVEL > 0:
                            if memory.get('key') and memory.get('value'):
                                await matcher.send(f"[debug]: 记住了 {memory.get('key')} = {memory.get('value')}")
                            elif memory.get('key') and memory.get('value') is None:
                                await matcher.send(f"[debug]: 忘记了 {memory.get('key')}")

                elif key == 'notify':  # 通知消息
                    if isinstance(reply_content, dict):
                        if 'sender' in reply_content and 'msg' in reply_content:
                            loop_data['notify'] = reply_content
                        else:
                            logger.warning(f"通知消息格式错误: {reply_content}")

                elif key == 'wake_up':  # 重新调用对话
                    logger.info(f"重新调用对话: {reply_content}")
                    wake_up = bool(reply_content)

                elif key == 'timer':  # 定时器
                    logger.info(f"设置定时器: {reply_content}")
                    loop_data['timer'] = reply_content

                elif key == 'preset':  # 更新对话预设
                    original_preset = chat.active_preset.bot_self_introl[:]
                    origin_snippet = reply_content.get('origin') # type: ignore
                    new_snippet = reply_content.get('new') # type: ignore
                    if origin_snippet == '[empty]': # 如果原始内容为空，则直接追加新内容
                        new_bot_self_introl = f"{original_preset}; {new_snippet}"
                    else:   # 否则替换原始内容
                        new_bot_self_introl = original_preset.replace(origin_snippet, new_snippet)
                    if chat.update_preset(preset_key=chat.preset_key, bot_self_introl=new_bot_self_introl):
                        logger.info(f"更新对话预设: {chat.preset_key} 成功")
                    else:
                        logger.warning(f"更新对话预设: {chat.preset_key} 失败")

                elif key == 'rcon':  # RCON指令
                    try:
                        with MCRcon(config.MC_RCON_HOST, config.MC_RCON_PASSWORD, int(config.MC_RCON_PORT), timeout=10) as mcr:
                            resp = mcr.command(reply_content)
                            resp = resp if resp else '无'
                            loop_data['end_notify'] = {'sender': '[Minecraft Rcon]', 'msg': f"执行 \"{reply_content}\" | 结果: {resp}"}
                            if config.DEBUG_LEVEL > 0:  logger.info(f"发送MC-RCON指令: {reply_content} | 响应: {resp}")
                    except:
                        logger.warning(f"发送MC-RCON指令: {reply_content} 失败")

                res_times -= 1
                if res_times < 1:  # 如果回复次数超过限制，则跳出循环
                    break
        else:
            logger.error(f'unknown reply type:{type(reply)}, content:{reply}')
        await asyncio.sleep(1)  # 每条回复之间间隔1秒

    cost_token = tg.cal_token_count(str(prompt_template) + raw_res)  # 计算对话结果的 token 数量

    # while time.time() - sta_time < 1.5:   # 限制对话响应最短时间
    #     time.sleep(0.1)

    if config.DEBUG_LEVEL > 0: logger.info(f"token消耗: {cost_token} | 对话响应: \"{raw_res}\"")
    await chat.update_chat_history_row(sender=chat.preset_key, msg=raw_res, require_summary=True, record_time=False)  # 更新全局对话历史记录
    chat.update_send_time() # 更新对话发送时间
    # 更新对用户的对话信息
    await chat.update_chat_history_row_for_user(sender=chat.preset_key, msg=raw_res, userid=trigger_userid, username=sender_name, require_summary=True)
    PersistentDataManager.instance.save_to_file()  # 保存数据

    # 如果存在响应结束通知消息，则发送通知
    if 'end_notify' in loop_data:
        await chat.update_chat_history_row(sender=loop_data['end_notify'].get('sender', 'System'), msg=loop_data['end_notify'].get('msg'), require_summary=False)  # 更新全局对话历史记录
        loop_data.pop('end_notify')  # 移除end_notify

    if config.DEBUG_LEVEL > 0: logger.info(f"对话响应完成 | 耗时: {time.time() - sta_time}s")
    
    # 检查是否再次触发对话
    if wake_up and loop_times < 5:
        if 'timer' in loop_data and 'notify' in loop_data:  # 如果存在定时器和通知消息，将其作为触发消息再次调用对话
            time_diff = loop_data['timer']
            loop_data.pop('timer')  # 移除timer
            if time_diff > 0:
                if config.DEBUG_LEVEL > 0: logger.info(f"等待 {time_diff}s 后再次调用对话...")
                await asyncio.sleep(time_diff)
            if config.DEBUG_LEVEL > 0: logger.info("再次调用对话...")
            await do_msg_response(
                matcher=matcher,
                trigger_text=loop_data.get('notify', {}).get('msg', ''),
                trigger_userid=trigger_userid,
                sender_name=loop_data.get('notify', {}).get('sender', '[system]'),
                wake_up=wake_up,
                loop_times=loop_times + 1,
                chat_type=chat_type,
                is_tome=is_tome,
                chat_key=chat_key,
                bot=bot,
            )
        elif 'notify' in loop_data:   # 如果存在通知消息，将其作为触发消息再次调用对话
            await do_msg_response(
                matcher=matcher,
                trigger_text=loop_data.get('notify', {}).get('msg', ''),
                trigger_userid=trigger_userid,
                sender_name=loop_data.get('notify', {}).get('sender', '[system]'),
                wake_up=wake_up,
                loop_times=loop_times + 1,
                chat_type=chat_type,
                is_tome=is_tome,
                chat_key=chat_key,
                bot=bot,
            )
