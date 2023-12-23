import difflib
import os
from typing import Optional, Dict

import requests

from .chat import Chat
from .chat_manager import ChatManager
from .config import *
from .Extension import global_extensions, load_extensions
from .logger import logger
from .persistent_data_manager import PersistentDataManager

from .preset_hub_funcs import upload_preset, get_preset, search_preset, delete_preset

# 选项类型  bool只要有就是True，str则需要跟上参数值
option_type = {
    'target': str,
    'global': bool,
    'admin': bool,
    'deep': bool,
    'to_default': bool,
    'default': str,
    'show': bool,
    'by': str,
    'desc': str,
    'n': str,
    'use': str,
    'p': str,
    'ps': str,
}

class CommandManager:
    def __init__(self):
        self.command_router = {}
        # 指令路由 通过指令路由来规范指令的参数格式
        # arg_list: [参数1, 参数2, ...] 多余的参数会被拼接到最后一个参数中
        # func: 指令执行函数
        # command_router = {
        #     'rg': {'arg_list': [], 'func': None},
        # }

    def register(self, route, params:list=[]):
        """注册指令修饰方法"""
        # print('register:', route, params)
        def wrapper(func):
            self.command_router[route] = {'arg_list': params, 'func': func}
            return func
        return wrapper

    def execute(self, chat:Chat, command:str, chat_presets_dict:dict) -> Optional[dict]:
        """执行指令"""
        option_dict, param_dict, target_route = self.resolve_command(command)
        logger.info(f'执行命令: "{command}";  指令匹配路由: {target_route}')
        if target_route:
            try:
                return self.command_router[target_route]['func'](option_dict, param_dict, chat, chat_presets_dict)
            except Exception as e:
                return {'error': e}
        return None

    def submit_commands(self):
        """提交指令注册 *在所有指令注册完成后调用*"""
        # 将指令路由字典根据键中包含的`/`数量进行降序排序 以便于匹配时优先匹配更长的指令
        self.command_router = dict(sorted(self.command_router.items(), key=lambda x: len(x[0].split('/')), reverse=True))
        # print('所有指令注册完成 共计:', len(self.command_router), '条指令')

    def resolve_command(self, command:str):
        """解析命令"""
        # 命令格式: 一级命令 二级命令 ... (选项1 选项2) ... 参数1 参数2 参数3
        # 命令名和参数之间必须有一个或多个空格
        # 命令名和参数之间可以有换行
        # 选项和参数顺序可以任意

        # 生成命令参数列表
        cmd_list = [c.strip() for c in command.split(' ') if c.strip()]

        # 生成命令选项字典 并去除已经解析的选项
        # 如果是以 - 开头的参数，根据参数类型进行解析
        # 格式: -参数名 参数值 (对于布尔值，参数值可以省略)
        option_dict = {}
        for i in range(len(cmd_list)):
            if cmd_list[i].startswith('-'):
                option = cmd_list[i][1:]
                cmd_list[i] = ''  # 去除已经解析的参数
                if option_type[option] == bool:
                    option_dict[option] = True
                elif option_type[option] == str:
                    option_dict[option] = cmd_list[i + 1]
                    cmd_list[i + 1] = ''  # 去除已经解析的参数
        cmd_list = [c.strip() for c in cmd_list if c.strip()]  # 去除已经解析的参数

        # 按照 一级命令/二级命令... 匹配命令路由 如果有多余的参数则以空格为间隔拼接后存放到最后一个参数中
        target_route = ''
        for route, params_list in self.command_router.items():
            params_list = params_list['arg_list']
            # print(f"command route matching: {route} => {params_list}")
            try:
                if '/'.join(cmd_list).startswith(route):
                    param_dict = {}
                    # 截去路由匹配的一级/二级...命令
                    if len(params_list) > 0:
                        cmd_list = cmd_list[len(route.split('/')):]
                        for i in range(len(params_list) - 1):
                            param_dict[params_list[i]] = cmd_list[i]
                        # 将剩余的内容以空格为间隔拼接后存放到最后一个参数中
                        param_dict[params_list[-1]] = ' '.join(cmd_list[len(params_list) - 1:])
                    target_route = route
                    break
            except Exception as e: # 解析出错跳过
                logger.error(f'解析指令出错: {command} => reason: {e}')
                continue
        else:
            param_dict = {}
        return option_dict, param_dict, target_route

cmd:CommandManager = CommandManager()

""" 注册指令 """
@cmd.register(route='rg')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    presets_show_text = '\n'.join([f'  -> {k + " (当前)" if k == chat.preset_key else k}' for k in chat_presets_dict.keys()])
    if option_dict.get('admin'):
        return {
            'msg': (
                f"当前可用人格预设有:\n"
                f"{presets_show_text}\n"
                f"=======================\n"
                f"+ 使用预设: rg set <预设名> <-global?>\n"
                f"+ 查询预设: rg query <预设名>\n"
                f"+ 编辑预设: rg edit <预设名> <人格信息> <-global?>\n"
                f"+ 添加预设: rg new <预设名> <人格信息> <-global?>\n"
                f"+ 删除预设: rg del <预设名> <-global?>\n"
                f"+ 改名预设: rg rename <原预设名> <新预设名> <-global?>\n"
                f"+ 开关会话: rg <on/off> <-global?>\n"
                f"+ 重置会话: rg reset <-global?>\n"
                f"+ 查询会话(超管): rg chats\n"
                f"+ 扩展信息(超管): rg ext\n"
                f"* -global 参数表示是否全局设置(仅超管可用)\n"
                f"* 改名/重命名预设将丢失所有会话历史！\n"
                f"* 更多帮助请访问: NG指令文档\n"
                f"Tip: <人格信息> 是一段第三人称的人设说明(建议不超过200字)\n"
            )
        }
    else:
        return {
            'msg': (
                f"会话: {chat.chat_key} [{'启用' if chat.is_enable else '禁用'}]\n"
                f"当前可用人格预设有:\n"
                f"{presets_show_text}\n"
                # f"=======================\n"
                # f"+ 使用预设: rg set <预设名>\n"
                # f"+ 查询预设: rg query <预设名>\n"
                # f"+ 编辑预设: rg edit <预设名> <人格信息>\n"
                # f"+ 添加预设: rg new <预设名> <人格信息>\n"
                # f"+ 删除预设: rg del <预设名>\n"
                # f"+ 改名预设: rg rename <原预设名> <新预设名>\n"
                # f"+ 重置会话: rg reset\n"
                # f"* 改名/重命名预设将丢失所有会话历史！\n"
                # f"Tip: <人格信息> 是一段第三人称的人设说明(建议不超过200字)\n"
            )
        }

@cmd.register(route='rg/set', params=['preset_key', 'preset_intro'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    target_preset_key = param_dict['preset_key']
    if target_preset_key not in chat_presets_dict:  # 如果预设不存在，匹配最相似的预设
        target_preset_key = difflib.get_close_matches(target_preset_key, chat_presets_dict.keys(), n=1, cutoff=0.3)
        if len(target_preset_key) == 0:
            return {'msg': "找不到匹配的人格预设! 是不是手滑了呢？(；′⌒`)"}
        else:
            target_preset_key = target_preset_key[0]
            # return {'msg': f"预设不存在! 已为您匹配最相似的预设: {target_preset_key} v(￣▽￣)v"}

    if option_dict.get('global'):   # 全局应用
        success_cnt, fail_cnt = ChatManager.instance.change_presettings_for_all(preset_key=target_preset_key)
        return {'msg': f"应用预设: {target_preset_key} (￣▽￣)-Completed! (所有会话) '成功:{success_cnt}, 失败:{fail_cnt}", 'is_progress': True}
    elif option_dict.get('target'): # 指定会话应用
        target_chat_key = option_dict.get('target')
        target_chat = ChatManager.instance.get_chat(chat_key=target_chat_key)
        if not target_chat:
            return {'msg': f"会话: {target_chat_key} 不存在! (；′⌒`)"}
        target_chat.change_presettings(target_preset_key)
        return {'msg': f"应用预设: {target_preset_key} (￣▽￣)-ok! (会话: {target_chat_key})", 'is_progress': True}
    else:   # 当前会话应用
        chat.change_presettings(target_preset_key)
        return {'msg': f"应用预设: {target_preset_key} (￣▽￣)-ok!", 'is_progress': True}

@cmd.register(route='rg/query', params=['preset_key'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    target_preset_key = param_dict['preset_key']
    if target_preset_key not in chat_presets_dict:
        # 如果预设不存在，进行逐一进行字符匹配，选择最相似的预设
        target_preset_key = difflib.get_close_matches(target_preset_key, chat_presets_dict.keys(), n=1, cutoff=0.3)
        if len(target_preset_key) == 0:
            return {'msg': "找不到匹配的人格预设! 是不是手滑了呢？(；′⌒`)"}
        else:
            target_preset_key = target_preset_key[0]
            # return {'msg': f"预设不存在! 已为您匹配最相似的预设: {target_preset_key} v(￣▽￣)v"}
    return {'msg': f"预设: {target_preset_key} |\n  {chat_presets_dict[target_preset_key].bot_self_introl}"}

@cmd.register(route='rg/new', params=['preset_key', 'preset_intro'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    target_preset_key = param_dict['preset_key']
    bot_self_introl = param_dict.get('preset_intro', '')
    
    if option_dict.get('global'):   # 全局应用
        success_cnt, fail_cnt = ChatManager.instance.add_preset_for_all(preset_key=target_preset_key, bot_self_introl=bot_self_introl)
        return {'msg': f"添加预设: {target_preset_key} (￣▽￣)-ok! (所有会话) 成功:{success_cnt}，失败:{fail_cnt}", 'is_progress': True}
    elif option_dict.get('target'): # 指定会话应用
        target_chat_key = option_dict.get('target')
        target_chat = ChatManager.instance.get_chat(chat_key=target_chat_key)
        if not target_chat:
            return {'msg': f"会话: {target_chat_key} 不存在! (；′⌒`)"}
        success, err_msg = target_chat.add_preset(preset_key=target_preset_key, bot_self_introl=bot_self_introl)
        if success:
            return {'msg': f"添加预设: {target_preset_key} (￣▽￣)-ok! (会话: {target_chat_key})", 'is_progress': True}
        else:
            return {'msg': f"添加预设: {target_preset_key} 失败! (会话: {target_chat_key}) (；′⌒`)\n{err_msg}", 'is_progress': True}
    else:   # 当前会话应用
        success, err_msg = chat.add_preset(preset_key=target_preset_key, bot_self_introl=bot_self_introl)
        if success:
            return {'msg': f"添加预设: {target_preset_key} (￣▽￣)-ok!", 'is_progress': True}
        else:
            return {'msg': f"添加预设: {target_preset_key} 失败! (；′⌒`)\n{err_msg}", 'is_progress': True}

@cmd.register(route='rg/edit', params=['preset_key', 'preset_intro'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    target_preset_key = param_dict['preset_key']
    bot_self_introl = param_dict.get('preset_intro', '')
    
    if option_dict.get('global'):   # 全局应用
        success_cnt, fail_cnt = ChatManager.instance.update_preset_for_all(preset_key=target_preset_key, bot_self_introl=bot_self_introl)
        return {'msg': f"编辑预设: {target_preset_key} (￣▽￣)-ok! (所有会话) 成功:{success_cnt}，失败:{fail_cnt}", 'is_progress': True}
    elif option_dict.get('target'): # 指定会话应用
        target_chat_key = option_dict.get('target')
        target_chat = ChatManager.instance.get_chat(chat_key=target_chat_key)
        if not target_chat:
            return {'msg': f"会话: {target_chat_key} 不存在! (；′⌒`)"}
        success, err_msg = target_chat.update_preset(preset_key=target_preset_key, bot_self_introl=bot_self_introl)
        if success:
            return {'msg': f"编辑预设: {target_preset_key} (￣▽￣)-ok! (会话: {target_chat_key})", 'is_progress': True}
        else:
            return {'msg': f"编辑预设: {target_preset_key} (会话: {target_chat_key}) 错误 ＞﹏＜!\n{err_msg}", 'is_progress': True}
    else:   # 当前会话应用
        success, err_msg = chat.update_preset(preset_key=target_preset_key, bot_self_introl=bot_self_introl)
        if success:
            return {'msg': f"编辑预设: {target_preset_key} (￣▽￣)-ok!", 'is_progress': True}
        else:
            return {'msg': f"编辑预设: {target_preset_key} 错误 ＞﹏＜!\n{err_msg}", 'is_progress': True}

@cmd.register(route='rg/del', params=['preset_key'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    target_preset_key = param_dict['preset_key']

    if option_dict.get('global'):   # 全局应用
        success_cnt, fail_cnt = ChatManager.instance.del_preset_for_all(preset_key=target_preset_key)
        return {'msg': f"删除预设: {target_preset_key} (￣▽￣)-ok! (所有会话) 成功:{success_cnt}，失败:{fail_cnt}", 'is_progress': True}
    elif option_dict.get('target'): # 指定会话应用
        target_chat_key = option_dict.get('target')
        target_chat = ChatManager.instance.get_chat(chat_key=target_chat_key)
        if not target_chat:
            return {'msg': f"会话: {target_chat_key} 不存在! (；′⌒`)"}
        success, err_msg = target_chat.del_preset(preset_key=target_preset_key)
        if success:
            return {'msg': f"删除预设: {target_preset_key} (￣▽￣)-ok! (会话: {target_chat_key})", 'is_progress': True}
        else:
            return {'msg': f"删除预设: {target_preset_key} (会话: {target_chat_key}) 错误 ＞﹏＜!\n{err_msg}", 'is_progress': True}
    else:   # 当前会话应用
        success, err_msg = chat.del_preset(preset_key=target_preset_key)
        if success:
            return {'msg': f"删除预设: {target_preset_key} (￣▽￣)-ok!", 'is_progress': True}
        else:
            return {'msg': f"删除预设: {target_preset_key} 错误 ＞﹏＜!\n{err_msg}", 'is_progress': True}
        
@cmd.register(route='rg/rename', params=['old_preset_key', 'new_preset_key'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    target_old_preset_key = param_dict['old_preset_key']
    target_new_preset_key = param_dict['new_preset_key']

    if option_dict.get('global'):   # 全局应用
        success_cnt, fail_cnt = ChatManager.instance.rename_preset_for_all(old_preset_key=target_old_preset_key, new_preset_key=target_new_preset_key)
        return {'msg': f"重命名预设: {target_old_preset_key} (￣▽￣)-ok! (所有会话) 成功:{success_cnt}，失败:{fail_cnt}", 'is_progress': True}
    elif option_dict.get('target'): # 指定会话应用
        target_chat_key = option_dict.get('target')
        target_chat = ChatManager.instance.get_chat(chat_key=target_chat_key)
        if not target_chat:
            return {'msg': f"会话: {target_chat_key} 不存在! (；′⌒`)"}
        success, err_msg = target_chat.rename_preset(old_preset_key=target_old_preset_key, new_preset_key=target_new_preset_key)
        if success:
            return {'msg': f"重命名预设: {target_old_preset_key} (￣▽￣)-ok! (会话: {target_chat_key})", 'is_progress': True}
        else:
            return {'msg': f"重命名预设: {target_old_preset_key} (会话: {target_chat_key}) 错误 ＞﹏＜!\n{err_msg}", 'is_progress': True}
    else:   # 当前会话应用
        success, err_msg = chat.rename_preset(old_preset_key=target_old_preset_key, new_preset_key=target_new_preset_key)
        if success:
            return {'msg': f"重命名预设: {target_old_preset_key} (￣▽￣)-ok!", 'is_progress': True}
        else:
            return {'msg': f"重命名预设: {target_old_preset_key} 错误 ＞﹏＜!\n{err_msg}", 'is_progress': True}

@cmd.register(route='rg/reset')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    if option_dict.get('global'):   # 全局应用
        success_cnt, fail_cnt = ChatManager.instance.reset_chat_for_all()
        return {'msg': f"重置会话(￣▽￣)-ok! (所有会话) 成功:{success_cnt}，失败:{fail_cnt}", 'is_progress': True}
    elif option_dict.get('target'): # 指定会话应用
        target_chat_key = option_dict.get('target')
        target_chat = ChatManager.instance.get_chat(chat_key=target_chat_key)
        if not target_chat:
            return {'msg': f"会话: {target_chat_key} 不存在! (；′⌒`)"}
        if target_chat.reset_chat():
            return {'msg': f"重置 (￣▽￣)-ok! (会话: {target_chat_key})", 'is_progress': True}
        else:
            return {'msg': f"重置 (会话: {target_chat_key}) 错误 ＞﹏＜!", 'is_progress': True}
    else:   # 当前会话应用
        if chat.reset_chat():
            return {'msg': f"重置 (￣▽￣)-ok!", 'is_progress': True}
        else:
            return {'msg': f"重置 错误 ＞﹏＜!", 'is_progress': True}

@cmd.register(route='rg/on')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    if option_dict.get('global'):
        ChatManager.instance.toggle_chat_for_all(enabled=True)
        return {'msg': f"启用所有会话 (￣▽￣)-ok!"}
    elif option_dict.get('target'):
        target_chat_key = option_dict.get('target')
        target_chat = ChatManager.instance.get_chat(chat_key=target_chat_key)
        if target_chat:
            target_chat.toggle_chat(enabled=True)
            return {'msg': f"启用会话: {target_chat_key} (￣▽￣)-ok!"}
        else:
            return {'error': f"找不到会话: {target_chat_key}"}
    else:
        chat.toggle_chat(enabled=True)
        return {'msg': f"启用当前会话 (￣▽￣)-ok!"}

@cmd.register(route='rg/off')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    if option_dict.get('global'):
        ChatManager.instance.toggle_chat_for_all(enabled=False)
        return {'msg': f"禁用所有会话 (￣▽￣)-ok!"}
    elif option_dict.get('target'):
        target_chat_key = option_dict.get('target')
        target_chat = ChatManager.instance.get_chat(chat_key=target_chat_key)
        if target_chat:
            target_chat.toggle_chat(enabled=False)
            return {'msg': f"禁用会话: {target_chat_key} (￣▽￣)-ok!"}
        else:
            return {'error': f"找不到会话: {target_chat_key}"}
    else:
        chat.toggle_chat(enabled=False)
        return {'msg': f"禁用当前会话 (￣▽￣)-ok!"}

@cmd.register(route='rg/lock')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    if option_dict.get('global'):
        ChatManager.instance.toggle_auto_switch_for_all(enabled=False)
        return {'msg': f"锁定所有会话人格 (￣▽￣)-ok!"}
    elif option_dict.get('target'):
        target_chat_key = option_dict.get('target')
        target_chat = ChatManager.instance.get_chat(chat_key=target_chat_key)
        if target_chat:
            target_chat.toggle_auto_switch(enabled=False)
            return {'msg': f"锁定会话人格: {target_chat_key} (￣▽￣)-ok!"}
        else:
            return {'error': f"找不到会话: {target_chat_key}"}
    else:
        chat.toggle_auto_switch(enabled=False)
        return {'msg': f"锁定当前会话人格 (￣▽￣)-ok!"}

@cmd.register(route='rg/unlock')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    if option_dict.get('global'):
        ChatManager.instance.toggle_auto_switch_for_all(enabled=True)
        return {'msg': f"解锁所有会话 (￣▽￣)-ok!"}
    elif option_dict.get('target'):
        target_chat_key = option_dict.get('target')
        target_chat = ChatManager.instance.get_chat(chat_key=target_chat_key)
        if target_chat:
            target_chat.toggle_auto_switch(enabled=True)
            return {'msg': f"解锁会话: {target_chat_key} (￣▽￣)-ok!"}
        else:
            return {'error': f"找不到会话: {target_chat_key}"}
    else:
        chat.toggle_auto_switch(enabled=True)
        return {'msg': f"解锁当前会话 (￣▽￣)-ok!"}

@cmd.register(route='rg/ext')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    ext_info:str = ''
    for ext in global_extensions.values():
        ext_info += f"  {ext.generate_short_description()}"
    return {'msg': (
            f"已加载的扩展:\n{ext_info}"
            f"=======================\n"
            f"+ 下载扩展: rg ext add <扩展名>\n"
            f"+ 删除扩展: rg ext del <扩展名>\n"
        )}

@cmd.register(route='rg/ext/add', params=['ext_name'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    ext_base_url = "https://raw.githubusercontent.com/KroMiose/nonebot_plugin_naturel_gpt/main/extensions"
    ext_name:str = param_dict.get('ext_name')
    if not ext_name:
        return {'msg': f"未指定扩展名!"}
    if not ext_name.startswith('ext_'): # 扩展名不以 ext_ 开头则自动补全
        ext_name = f"ext_{ext_name}"
    if not ext_name.endswith('.py'):    # 扩展名不以 .py 结尾则自动补全
        ext_name = f"{ext_name}.py"

    ext_file_path = f"{config.NG_EXT_PATH}{ext_name}"   # 扩展文件存储路径
    # 从 github 下载扩展
    try:
        with open(ext_file_path, 'w', encoding='utf-8') as f:
            code = requests.get(f"{ext_base_url}/{ext_name}", timeout=10)
            if code.text.startswith('404: Not Found'):
                return {'msg': f"下载扩展失败: 未找到扩展 {ext_name}"}
            f.write(code.text)
    except Exception as e:
        return {'msg': f"下载扩展失败: {e}"}
    return {'msg': f"下载扩展 {ext_name} 成功!"}

@cmd.register(route='rg/ext/del', params=['ext_name'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    ext_name = param_dict.get('ext_name')
    if not ext_name:
        return {'msg': f"未指定扩展名!"}
    if not ext_name.startswith('ext_'): # 扩展名不以 ext_ 开头则自动补全
        ext_name = f"ext_{ext_name}"
    if not ext_name.endswith('.py'):    # 扩展名不以 .py 结尾则自动补全
        ext_name = f"{ext_name}.py"

    ext_file_path = f"{config.NG_EXT_PATH}{ext_name}"   # 扩展文件存储路径
    # 从本地文件删除扩展
    try:
        os.remove(ext_file_path)
    except Exception as e:
        return {'msg': f"删除扩展失败: {e}"}
    return {'msg': f"删除扩展 {ext_name} 成功!"}

@cmd.register(route='rg/ext/reload', params=['ext_name'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    load_extensions(config.dict())
    return {'msg': f"重载扩展成功!"}

def find_ext(ext_name: str) -> Optional[ExtConfig]:
    ext_name = ext_name.lower()
    for ext in config.NG_EXT_LOAD_LIST:
        will_find = ext.EXT_NAME.lower()
        if will_find == ext_name or will_find == f"ext_{ext_name}":
            return ext
    return None

@cmd.register(route='rg/ext/on', params=['ext_name'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    ext_name: str = param_dict.get('ext_name')
    if not ext_name:
        return {'msg': "未指定扩展名!"}

    ext_name = ext_name.lower()
    ext = find_ext(ext_name)
    if not ext:
        ext_paths = [
            x for x in Path(config.NG_EXT_PATH).glob('ext_*.py')
            if (
                (will_find := x.stem.lower()) == ext_name
                or will_find == f"ext_{ext_name}"
            )
        ]
        if not ext_paths:
            return {'msg': "找不到此扩展或此扩展未加载"}

        ext_file_path = ext_paths[0]
        ext = ExtConfig(EXT_NAME=ext_file_path.stem, IS_ACTIVE=False, EXT_CONFIG={})
        config.NG_EXT_LOAD_LIST.append(ext)

    if ext.IS_ACTIVE:
        return {'msg': "该扩展已经被启用过了"}

    ext.IS_ACTIVE = True
    save_config()
    return {'msg': "已启用该扩展，请使用 `rg ext reload` 指令重载所有扩展"}

@cmd.register(route='rg/ext/off', params=['ext_name'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    ext_name: str = param_dict.get('ext_name')
    if not ext_name:
        return {'msg': "未指定扩展名!"}

    ext = find_ext(ext_name)
    if not ext:
        return {'msg': "找不到此扩展或此扩展未加载"}

    if ext.IS_ACTIVE:
        ext.IS_ACTIVE = False
        save_config()
        return {'msg': "已禁用该扩展，请使用 `rg ext reload` 指令重载所有扩展"}

    return {'msg': "该扩展已经被禁用过了"}

@cmd.register(route='rg/chats')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    chat_info:str = ''
    for chat in ChatManager.instance.get_all_chats():
        chat_info += f"+ {chat.generate_description(not option_dict.get('show'))}"
    return {'msg': f"当前已加载的会话:\n{chat_info}"}

@cmd.register(route='rg/reload_config')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    reload_config()
    PersistentDataManager.instance.load_from_file()
    return {'msg': f"配置文件重载成功! ver:{config.VERSION}"}

""" PresetHub 相关命令 """

@cmd.register(route='rg/search', params=["keyword"])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    keyword = param_dict.get('keyword')
    page = int(option_dict.get('p', '1'))
    page_size = int(option_dict.get('ps', '10'))

    def gen_preset_info(record: Dict):
        return (
            f"+ {record['preset_key']} - id: {record['id']}\n"
            f"    预设名: {record['name']} by: {record['uploader']}\n"
        )

    success, data = search_preset(keyword, page=page, page_size=page_size)
    if success:
        return {'msg': f"从 PresetHub 中搜索 \"{keyword}\" 结果:\n{''.join([gen_preset_info(r) for r in data['list']])}\n页码:{page}/{data['total']//page_size + 1} - 共 {data['total']} 条\n\ntips: 使用 `rg get <预设id> -u ~` 可应用预设"}
    else:
        return {'msg': f"检索预设库数据时出现错误: {data}"}


@cmd.register(route='rg/get', params=["preset_id"])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    preset_id = param_dict.get('preset_id')
    with_use = option_dict.get('use')

    if not preset_id:
        return {"msg": "未指定预设ID!"}

    success, data = get_preset(preset_id, bool(with_use))
    if success:
        if with_use:
            target_preset_key = data['preset_key'] if with_use == "~" else with_use

            if option_dict.get('global'):   # 全局应用
                success_cnt, fail_cnt = ChatManager.instance.add_preset_for_all(preset_key=target_preset_key, bot_self_introl=data['self_intro'])
                return {'msg': f"添加预设: {target_preset_key} (￣▽￣)-ok! (所有会话) 成功:{success_cnt}，失败:{fail_cnt}", 'is_progress': True}
            elif option_dict.get('target'): # 指定会话应用
                target_chat_key = option_dict.get('target')
                target_chat = ChatManager.instance.get_chat(chat_key=target_chat_key)
                if not target_chat:
                    return {'msg': f"会话: {target_chat_key} 不存在! (；′⌒`)"}
                success, err_msg = target_chat.add_preset(preset_key=target_preset_key, bot_self_introl=data['self_intro'])
                if success:
                    return {'msg': f"添加预设: {target_preset_key} (￣▽￣)-ok! (会话: {target_chat_key})", 'is_progress': True}
                else:
                    return {'msg': f"添加预设: {target_preset_key} 失败! (会话: {target_chat_key}) (；′⌒`)\n{err_msg}", 'is_progress': True}
            else:   # 当前会话应用
                success, err_msg = chat.add_preset(preset_key=target_preset_key, bot_self_introl=data['self_intro'])
                if success:
                    return {'msg': f"添加预设: {target_preset_key} (￣▽￣)-ok!", 'is_progress': True}
                else:
                    return {'msg': f"添加预设: {target_preset_key} 失败! (；′⌒`)\n{err_msg}", 'is_progress': True}

        else:
            return {"msg": f"查询到预设信息: {data['name']}\n  预设键: {data['preset_key']}\n  预设值: {data['self_intro']}{('  描述:' + data.get('description')) if data.get('description') else ''}\n  (id: {data['id']})"}
    else:
        return {"msg": f"获取预设时出现错误: {data}"}

@cmd.register(route='rg/upload', params=["preset_key", "preset_intro"])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    preset_key = param_dict['preset_key']
    self_intro = param_dict.get('preset_intro', '')
    name = option_dict.get('n', preset_key)
    uploader = option_dict.get('by', 'Unknown')
    description = option_dict.get('desc', '')

    if not (preset_key or self_intro):
        return {"msg": "未指定预设名或预设介绍!"}

    success, data = upload_preset(name, preset_key, self_intro, uploader, description)
    if success:
        return {"msg": f"上传预设成功! 预设名: {preset_key}\nid: {data['id']}"}
    else:
        return {"msg": f"上传预设时出现错误: {data}"}

@cmd.register(route='rg/ph/del', params=["preset_id"])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    preset_id = param_dict.get('preset_id')

    success, data = delete_preset(preset_id)
    if success:
        return {"msg": "从 PresetHub 中删除预设成功!"}
    else:
        return {"msg": f"删除预设时出现错误: {data}"}


# 提交指令注册
cmd.submit_commands()

# if __name__ == '__main__':
#     print(cmd.execute(
#         command='rg new -target group_123456 test test_intro 123',
#         chat=None,
#         chat_presets_dict={},
#     ))
