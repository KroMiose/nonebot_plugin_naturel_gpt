from nonebot import get_driver
from nonebot import on_command, on_keyword, on_message
from nonebot.log import logger
from nonebot.params import Arg, ArgPlainText, CommandArg, Matcher, Event
from nonebot.adapters.onebot.v11 import Message, PrivateMessageEvent, GroupMessageEvent

import time
import random
import difflib
import os
from pathlib import Path
import pickle

from .config import *
global_config = get_driver().config
# logger.info(config) # 这里可以打印出配置文件的内容

from .openai_func import TextGenerator

global_data = {}  # 用于存储所有数据的字典
global_data_path = f"{config['NG_DATA_PATH']}naturel_gpt.pkl"


# 对话类
class Chat:
    chat_presets = {}   # 当前对话预设
    chat_preset_dicts = {}   # 预设字典

    def __init__(self, chat_key:str, preset_key:str = ''):
        self.chat_key = chat_key    # 对话标识
        if not preset_key:  # 如果没有预设，选择默认预设
            for pk in presets_dict:
                if presets_dict[pk]['is_default']:
                    preset_key = pk
                    break
            else:   # 如果没有默认预设，则选择第一个预设
                preset_key = list(presets_dict.keys())[0]
        self.change_presettings(preset_key)

    # 更新全局对话历史行
    def update_chat_history_row(self, sender:str, msg: str, require_summary:bool = False) -> None:
        messageunit = tg.generate_msg_template(sender=sender, msg=msg)
        self.chat_presets['chat_history'].append(messageunit)
        logger.info(f"添加对话历史行: {messageunit}  |  当前对话历史行数: {len(self.chat_presets['chat_history'])}")
        while len(self.chat_presets['chat_history']) > config['CHAT_MEMORY_MAX_LENGTH'] * 2:    # 保证对话历史不超过最大长度的两倍
            self.chat_presets['chat_history'].pop(0)
        # 保证对话历史不超过最大长度
        if len(self.chat_presets['chat_history']) > config['CHAT_MEMORY_MAX_LENGTH'] and require_summary: # 只有在需要时才进行总结 避免不必要的计算
            prev_summarized = f"上次的对话摘要:{self.chat_presets['chat_summarized']}\n\n" \
                if self.chat_presets.get('chat_summarized') else ''
            history_str = '\n'.join(self.chat_presets['chat_history'])
            prompt = (  # 以机器人的视角总结对话历史
                f"{prev_summarized}对话记录:\n"
                f"{history_str}"
                f"\n\n{self.chat_presets['bot_self_introl']}\n从{self.chat_presets['bot_name']}的视角用一段话总结以上聊天并尽可能多地记录下对话中的重要信息:"
            )
            if config.get('__DEBUG__'): logger.info(f"生成对话历史摘要prompt: {prompt}")
            self.chat_presets['chat_summarized'] = tg.get_response(prompt, type='summarize').strip()  # 生成新的对话历史摘要
            # logger.info(f"生成对话历史摘要: {self.chat_presets['chat_summarized']}")
            logger.info(f"摘要生成消耗token数: {tg.cal_token_count(prompt + self.chat_presets['chat_summarized'])}")
            self.chat_presets['chat_history'] = self.chat_presets['chat_history'][-config['CHAT_MEMORY_SHORT_LENGTH']:]

    # 更新对特定用户的对话历史行
    def update_chat_history_row_for_user(self, sender:str, msg: str, userid:str, username:str) -> None:
        if userid not in global_preset_userdata[self.preset_key]:
            global_preset_userdata[self.preset_key][userid] = {'chat_history': []}
        messageunit = tg.generate_msg_template(sender=sender, msg=msg)
        global_preset_userdata[self.preset_key][userid]['chat_history'].append(messageunit)
        logger.info(f"添加对话历史行: {messageunit}  |  当前对话历史行数: {len(global_preset_userdata[self.preset_key][userid]['chat_history'])}")
        # 保证对话历史不超过最大长度
        if len(global_preset_userdata[self.preset_key][userid]['chat_history']) > config['USER_MEMORY_SUMMARY_THRESHOLD']:
            prev_summarized = f"上次的对话摘要:{global_preset_userdata[self.preset_key][userid].get('chat_summarized')}\n\n" \
                if global_preset_userdata[self.preset_key][userid].get('chat_summarized') else ''
            history_str = '\n'.join(global_preset_userdata[self.preset_key][userid]['chat_history'])
            prompt = (   # 以机器人的视角总结对话
                f"{prev_summarized}对话记录:\n"
                f"{history_str}"
                f"\n\n{self.chat_presets['bot_self_introl']}\n从{self.chat_presets['bot_name']}的视角描述对{username}的印象:"
            )
            if config.get('__DEBUG__'): logger.info(f"生成对话历史摘要prompt: {prompt}")
            global_preset_userdata[self.preset_key][userid]['chat_impression'] = tg.get_response(prompt, type='summarize').strip()  # 生成新的对话历史摘要
            # logger.info(f"生成对话历史摘要: {global_preset_userdata[self.preset_key][userid]['chat_impression']}")
            logger.info(f"摘要生成消耗token数: {tg.cal_token_count(prompt + global_preset_userdata[self.preset_key][userid]['chat_impression'])}")
            global_preset_userdata[self.preset_key][userid]['chat_history'] = global_preset_userdata[self.preset_key][userid]['chat_history'][-config['CHAT_MEMORY_SHORT_LENGTH']:]

    # 修改对话预设
    def change_presettings(self, preset_key:str) -> None:
        if preset_key not in self.chat_preset_dicts:    # 如果聊天预设字典中没有该预设，则从全局预设字典中复制一个
            self.chat_preset_dicts[preset_key] = presets_dict[preset_key].copy()
        self.chat_presets = self.chat_preset_dicts[preset_key]
        if 'chat_history' not in self.chat_presets: # 如果预设中没有对话历史，则添加一个空的对话历史
            self.chat_presets['chat_history'] = []
        self.preset_key = preset_key

    # 从全局预设更新对话预设
    def update_presettings(self):
        try:
            self.chat_presets['bot_self_introl'] = presets_dict[self.preset_key]['bot_self_introl']
            self.chat_presets['bot_name'] = presets_dict[self.preset_key]['bot_name']
        except KeyError:
            logger.error(f"尝试更新预设 {self.preset_key} 时发生错误，预设可能被删除。")

    # 对话 prompt 模板生成
    def get_chat_prompt_template(self, userid: None) -> str:
        impression_text = f"[印象]{global_preset_userdata[self.preset_key][userid].get('chat_impression')}" \
            if global_preset_userdata[self.preset_key].get(userid, {}).get('chat_impression', None) else ''  # 用户印象描述

        offset = 0
        chat_history = '\n'.join(self.chat_presets['chat_history'][-(config['CHAT_MEMORY_SHORT_LENGTH'] + offset):])  # 从对话历史中截取短期对话
        while tg.cal_token_count(chat_history) > config['CHAT_HISTORY_MAX_TOKENS']:
            offset += 1 # 如果对话历史过长，则逐行删除对话历史
            chat_history = '\n'.join(self.chat_presets['chat_history'][-(config['CHAT_MEMORY_SHORT_LENGTH'] + offset):])

        summary = f"\n\n[历史聊天摘要]: {self.chat_presets['chat_summarized']}" if self.chat_presets.get('chat_summarized', None) else ''  # 如果有对话历史摘要，则添加摘要

        return (
            f"{self.chat_presets['bot_self_introl']}"
            f"\n{summary}\n{impression_text}\n"
            f"以下是与 \"{self.chat_presets['bot_name']}\" 的对话:"
            f"\n\n{chat_history}\n{self.chat_presets['bot_name']}:"
        )

    # 获取当前对话bot的名称
    def get_chat_bot_name(self) -> str:
        return self.chat_presets['bot_name']

    # 获取当前对话bot的预设键
    def get_chat_preset_key(self) -> str:
        return self.preset_key

# 检测历史数据pickle文件是否存在 不存在则初始化 存在则读取
if os.path.exists(global_data_path):
    with open(global_data_path, 'rb') as f:
        global_data = pickle.load(f)  # 读取历史数据pickle文件
        presets_dict:dict = global_data['PRESETS']  # 用于存储所有人格预设的字典
        global_preset_userdata:dict = global_data['PRESET_USERDATA']  # 用于存储所有人格预设的用户数据的字典
        chat_dict:dict = global_data['CHAT_DICT']  # 用于存储所有对话的字典
        logger.info("读取历史数据成功")
else:   # 如果不存在历史数据json文件，则初始化
    # 检测目录是否存在 不存在则创建
    if not os.path.exists(config['NG_DATA_PATH']):
        os.makedirs(config['NG_DATA_PATH'])

    # 创建用于存储所有人格预设的字典
    presets_dict:dict = config['PRESETS']
    for key in presets_dict:
        presets_dict[key]['to_impression'] = {} # 用于存储所有人格对聊天对象印象的字典

    # 创建用于存储所有人格预设的用户数据的字典
    global_preset_userdata:dict = {}
    for key in presets_dict:
        global_preset_userdata[key] = {}

    # 创建用于存储所有对话的字典
    chat_dict:dict = {}
    logger.info("找不到历史数据，初始化成功")

# 记录最后保存数据的时间
last_save_data_time = time.time()

# 读取ApiKeys
api_keys = config['OPENAI_API_KEYS']
logger.info(f"共读取到 {len(api_keys)} 个API Key")

# 初始化对话文本生成器
tg: TextGenerator = TextGenerator(api_keys, {
    'model': config['CHAT_MODEL'],
    'max_tokens': config['REPLY_MAX_TOKENS'],
    'temperature': config['CHAT_TEMPERATURE'],
    'top_p': config['CHAT_TOP_P'],
    'frequency_penalty': config['CHAT_FREQUENCY_PENALTY'],
    'presence_penalty': config['CHAT_PRESENCE_PENALTY'],
    'max_summary_tokens': config['CHAT_MAX_SUMMARY_TOKENS'],
})

# 注册消息响应器 收到任意消息时触发
matcher = on_message(priority=10, block=False)
@matcher.handle()
async def handler(event: Event) -> None:
    sender_name = event.dict().get('sender', {}).get('nickname', '未知')
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
        f"\nJSON: {event.json()}"
    )
    # logger.info(resTmplate)

    # 如果是忽略前缀 或者 消息为空，则跳过处理
    if event.get_plaintext().startswith(config['IGNORE_PREFIX']) or not event.get_plaintext():   
        logger.info("忽略前缀，跳过处理...")
        return

    # 判断群聊/私聊
    if isinstance(event, GroupMessageEvent):
        chat_key = 'group_' + event.get_session_id().split("_")[1]
    elif isinstance(event, PrivateMessageEvent):
        chat_key = 'private_' + event.get_user_id()
    else:
        logger.info("未知消息来源: " + event.get_session_id())
        return

    # 判断是否已经存在对话
    if chat_key in chat_dict:
        logger.info("已存在对话 - 继续对话")
        chat = chat_dict[chat_key]
    else:
        logger.info("不存在对话 - 创建新对话")
        # 创建新对话
        chat = Chat(chat_key)
        chat_dict[chat_key] = chat

    if not (    # 如果不是 bot 相关的信息，则直接返回
        (config['REPLY_ON_NAME_MENTION'] and (chat.get_chat_bot_name() in event.get_plaintext())) or \
        (config['REPLY_ON_AT'] and event.is_tome())\
    ):
        chat.update_chat_history_row(sender=sender_name, msg=event.get_plaintext(), require_summary=False)
        logger.info("不是 bot 相关的信息，记录但不进行回复")
        return
    else:
        # 更新全局对话历史记录
        chat.update_chat_history_row(sender=sender_name, msg=event.get_plaintext(), require_summary=True)
        logger.info("符合 bot 发言条件，进行回复...")

    # 记录对用户的对话信息
    chat.update_chat_history_row_for_user(sender=sender_name, msg=event.get_plaintext(), userid=event.get_user_id(), username=sender_name)

    # 潜在人格唤醒机制 *待实现
    # 通过对话历史中的关键词进行检测，如果检测到潜在人格，进行累计，达到一定阈值后，抢占当前生效的人格

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
    prompt_template = chat.get_chat_prompt_template(userid=event.get_user_id())
    logger.info("对话 prompt 模板: \n" + prompt_template)

    res = tg.get_response(prompt=prompt_template, type='chat', custom={'bot_name': chat.get_chat_bot_name(), 'sender_name': sender_name})  # 生成对话结果
    cost_token = tg.cal_token_count(prompt_template + res)      # 计算对话结果的 token 数量

    while time.time() - sta_time < 1.5:   # 限制对话响应时间
        time.sleep(0.1)

    # 发送对话结果
    await matcher.send(res)
    logger.info(f"token消耗: {cost_token} | 对话响应: \"{res}\"")
    chat.update_chat_history_row(sender=chat.get_chat_bot_name(), msg=res, require_summary=True)  # 更新全局对话历史记录
    # 更新对用户的对话信息
    chat.update_chat_history_row_for_user(sender=chat.get_chat_bot_name(), msg=res, userid=event.get_user_id(), username=sender_name)
    save_data()  # 保存数据

# 人格设定指令 用于设定人格的相关参数
identity:Matcher = on_command("identity", aliases={"人格设定", "人格", "rg"}, priority=2, block=True)
@identity.handle()
async def _(event: Event, arg: Message = CommandArg()):
    is_progress = False
    # 判断群聊/私聊
    if isinstance(event, GroupMessageEvent):
        chat_key = 'group_' + event.get_session_id().split("_")[1]
    elif isinstance(event, PrivateMessageEvent):
        chat_key = 'private_' + event.get_user_id()
    else:
        logger.info("未知消息来源: " + event.get_session_id())
        return

    cmd:str = arg.extract_plain_text()
    logger.info(f"接收到指令: {cmd} | 来源: {chat_key}")

    if not cmd:
        presets_show_text = '\n'.join([f'  -> {k + " (当前)" if k == chat_key else k}' for k in list(presets_dict.keys())])
        await identity.finish((
            f"当前可用人格预设有:\n"
            f"{presets_show_text}\n"
            f"=======================\n"
            f"+ 使用预设: rg 设定 <预设名>\n"
            f"+ 查询预设: rg 查询 <预设名>\n"
            f"+ 更新预设: rg 更新 <预设名> <人格信息>\n"
            f"+ 添加预设: rg 添加 <预设名> <人格信息>\n"
            f"Tip: <人格信息> 是一段第三人称的人设说明(不超过200字, 不包含空格)\n"
        ))

    elif (cmd.split(' ')[0] == "设定" or cmd.split(' ')[0] == "set") and len(cmd.split(' ')) == 2:
        target_preset_key = cmd.split(' ')[1]
        if target_preset_key not in presets_dict:
            # 如果预设不存在，进行逐一进行字符匹配，选择最相似的预设
            target_preset_key = difflib.get_close_matches(target_preset_key, presets_dict.keys(), n=1, cutoff=0.3)
            if len(target_preset_key) == 0:
                await identity.finish("找不到匹配的人格预设! 是不是手滑了呢？(；′⌒`)")
            else:
                target_preset_key = target_preset_key[0]
                await identity.send(f"预设不存在! 已为您匹配并应用最相似的预设: {target_preset_key} v(￣▽￣)v")

        if chat_key in chat_dict:
            chat = chat_dict[chat_key]
            chat.change_presettings(target_preset_key)
        else:
            chat = Chat(chat_key, target_preset_key)
            chat_dict[chat_key] = chat
        is_progress = True
        await identity.finish(f"应用预设: {target_preset_key} (￣▽￣)-ok!")

    elif (cmd.split(' ')[0] == "查询" or cmd.split(' ')[0] == "query") and len(cmd.split(' ')) == 2:
        target_preset_key = cmd.split(' ')[1]
        if target_preset_key not in presets_dict:
            # 如果预设不存在，进行逐一进行字符匹配，选择最相似的预设
            target_preset_key = difflib.get_close_matches(target_preset_key, presets_dict.keys(), n=1, cutoff=0.3)
            if len(target_preset_key) == 0:
                await identity.finish("找不到匹配的人格预设! 是不是手滑了呢？(；′⌒`)")
            else:
                target_preset_key = target_preset_key[0]
                await identity.send(f"预设不存在! 帮您匹配最相似的预设: {target_preset_key} v(￣▽￣)v")
        is_progress = True
        await identity.finish(f"预设: {target_preset_key} | 人设信息:\n    {presets_dict[target_preset_key]['bot_self_introl']}")

    elif (cmd.split(' ')[0] == "更新" or cmd.split(' ')[0] == "update") and len(cmd.split(' ')) >= 3:
        target_preset_key = cmd.split(' ')[1]
        if target_preset_key not in presets_dict:
            await identity.finish("找不到匹配的人格预设! 是不是手滑了呢？(；′⌒`)")
        if presets_dict[target_preset_key]['is_locked'] and (str(event.user_id) not in config['ADMIN_USERID']):
            await identity.finish("该预设被神秘力量锁定了! 不能编辑呢 (＠_＠;)")
        presets_dict[target_preset_key]['bot_self_introl'] = cmd.split(' ', 2)[2]
        is_progress = True
        await identity.send(f"更新预设: {target_preset_key} 成功! (￣▽￣)")

    elif (cmd.split(' ')[0] == "添加" or cmd.split(' ')[0] == "new") and len(cmd.split(' ')) >= 3:
        target_preset_key = cmd.split(' ')[1]
        introl = cmd.split(' ', 2)[2]
        if target_preset_key in presets_dict:
            await identity.finish("预设已存在! 请检查后重试!")
        presets_dict[target_preset_key] = {
            'bot_name': target_preset_key,
            'is_locked': False,
            'is_default': False,
            'bot_self_introl': introl,
        }
        is_progress = True
        await identity.send(f"添加预设: {target_preset_key} 成功! (￣▽￣)")

    elif cmd.split(' ')[0] == "删除" and len(cmd.split(' ')) == 2:
        target_preset_key = cmd.split(' ')[1]
        if str(event.user_id) not in config['ADMIN_USERID']:
            await identity.finish("对不起！你没有权限进行此操作 ＞﹏＜")
        if target_preset_key not in presets_dict:
            await identity.finish("找不到匹配的人格预设! 是不是手滑了呢？(；′⌒`)")
        del presets_dict[target_preset_key]
        is_progress = True
        await identity.send(f"删除预设: {target_preset_key} 成功! (￣▽￣)")

    else:
        await identity.finish("输入的命令好像有点问题呢... 请检查下再试试吧！ ╮(>_<)╭")

    if is_progress: # 如果有编辑进度，进行数据保存
        # 更新所有全局预设到会话预设中
        for chat in chat_dict.values():
            chat.update_presettings()
        # 更新全局预设数据
        for key in presets_dict:
            global_preset_userdata[key] = {}
        logger.info(f"用户: {event.get_user_id()} 进行了人格预设编辑: {cmd}")
        save_data()  # 保存数据


# 保存数据到本地
def save_data():
    global last_save_data_time
    if time.time() - last_save_data_time < 10:  # 如果距离上次保存时间不足300秒，则不保存
        return
    global_data['PRESETS'] = presets_dict
    global_data['PRESET_USERDATA'] = global_preset_userdata
    global_data['CHAT_DICT'] = chat_dict
    # 检测目录是否存在 不存在则创建
    if not os.path.exists(config['NG_DATA_PATH']):
        os.makedirs(config['NG_DATA_PATH'])
    # 保存到pickle文件
    with open(global_data_path, 'wb') as f:
        pickle.dump(global_data, f)
    last_save_data_time = time.time()
    logger.info("数据保存成功")