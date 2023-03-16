from nonebot.log import logger
from .chat import Chat, global_chat_dict
from .persistent_data_manager import PersistentDataManager
from .Extension import Extension, global_extensions

import difflib

# 选项类型  bool只要有就是True，str则需要跟上参数值
option_type = {
    'target': str,
    'global': bool,
    'admin': bool,
    'deep': bool,
    'to_default': bool,
    'default': str,
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

    def execute(self, chat:Chat, command:str, chat_presets_dict:dict) -> dict:
        """执行指令"""
        logger.info('执行指令:' + command)
        option_dict, param_dict, target_route = self.resolve_command(command)
        logger.info(f'指令匹配路由: {target_route}')
        if target_route:
            try:
                return self.command_router[target_route]['func'](option_dict, param_dict, chat, chat_presets_dict)
            except Exception as e:
                return {'error': e}
        return False

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
    presets_show_text = '\n'.join([f'  -> {k + " (当前)" if k == chat.get_chat_preset_key() else k}' for k in chat_presets_dict.keys()])
    if option_dict.get('admin'):
        return {
            'msg': (
                f"当前可用人格预设有:\n"
                f"{presets_show_text}\n"
                f"=======================\n"
                f"+ 使用预设: rg set <预设名> <-global?>\n"
                f"+ 查询预设: rg query <预设名>\n"
                f"+ 编辑预设: rg update <预设名> <人格信息> <-global?>\n"
                f"+ 添加预设: rg new <预设名> <人格信息> <-global?>\n"
                f"+ 删除预设(管理): rg del <预设名> <-global?>\n"
                f"+ 开关会话(管理): rg <on/off> <-global?>\n"
                f"+ 重置会话(管理): rg <重置/reset> <-global?>\n"
                f"+ 查询会话(管理): rg <会话/chats>\n"
                f"+ 拓展信息(管理): rg <拓展/ext>\n"
                f"Tip: <人格信息> 是一段第三人称的人设说明(建议不超过200字)\n"
            )
        }
    else:
        return {
            'msg': (
                f"会话: {chat.get_chat_key()} [{'启用' if chat.is_enable else '禁用'}]\n"
                f"当前可用人格预设有:\n"
                f"{presets_show_text}\n"
                f"=======================\n"
                f"+ 使用预设: rg set <预设名>\n"
                f"+ 查询预设: rg query <预设名>\n"
                f"+ 编辑预设: rg edit <预设名> <人格信息>\n"
                f"+ 添加预设: rg new <预设名> <人格信息>\n"
                f"Tip: <人格信息> 是一段第三人称的人设说明(不超过200字, 不包含空格)\n"
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
        err_cnt = 0
        for chat_key in global_chat_dict.keys():
            if not global_chat_dict[chat_key].change_presettings(target_preset_key):
                err_cnt += 1
        return {'msg': f"应用预设: {target_preset_key} (￣▽￣)-Completed! (所有会话) {f'错误计数:{err_cnt}' if err_cnt else ''}", 'is_progress': True}
    elif option_dict.get('target'): # 指定会话应用
        target_chat_key = option_dict.get('target')
        if target_chat_key not in global_chat_dict:
            return {'msg': f"会话: {target_chat_key} 不存在! (；′⌒`)"}
        global_chat_dict[target_chat_key].change_presettings(target_preset_key)
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
        err_cnt = 0
        for chat_key in global_chat_dict.keys():
            if not PersistentDataManager.instance.add_preset(chat_key=chat_key, preset_key=target_preset_key, bot_self_introl=bot_self_introl):
                err_cnt += 1
        return {'msg': f"添加预设: {target_preset_key} (￣▽￣)-ok! (所有会话) {f'错误:{err_cnt}' if err_cnt else ''}", 'is_progress': True}
    elif option_dict.get('target'): # 指定会话应用
        target_chat_key = option_dict.get('target')
        if target_chat_key not in global_chat_dict:
            return {'msg': f"会话: {target_chat_key} 不存在! (；′⌒`)"}
        if PersistentDataManager.instance.add_preset(chat_key=target_chat_key, preset_key=target_preset_key, bot_self_introl=bot_self_introl):
            return {'msg': f"添加预设: {target_preset_key} (￣▽￣)-ok! (会话: {target_chat_key})", 'is_progress': True}
        else:
            return {'msg': f"添加预设: {target_preset_key} 失败! (会话: {target_chat_key}) (；′⌒`)", 'is_progress': True}
    else:   # 当前会话应用
        if PersistentDataManager.instance.add_preset(chat_key=chat.get_chat_key(), preset_key=target_preset_key, bot_self_introl=bot_self_introl):
            return {'msg': f"添加预设: {target_preset_key} (￣▽￣)-ok!", 'is_progress': True}
        else:
            return {'msg': f"添加预设: {target_preset_key} 失败! (；′⌒`)", 'is_progress': True}

@cmd.register(route='rg/edit', params=['preset_key', 'preset_intro'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    target_preset_key = param_dict['preset_key']
    bot_self_introl = param_dict.get('preset_intro', '')
    
    if option_dict.get('global'):   # 全局应用
        err_cnt = 0
        for chat_key in global_chat_dict.keys():
            if not PersistentDataManager.instance.update_preset(chat_key=chat_key, preset_key=target_preset_key, bot_self_introl=bot_self_introl):
                err_cnt += 1
        return {'msg': f"编辑预设: {target_preset_key} (￣▽￣)-ok! (所有会话) {f'错误:{err_cnt}' if err_cnt else ''}", 'is_progress': True}
    elif option_dict.get('target'): # 指定会话应用
        target_chat_key = option_dict.get('target')
        if target_chat_key not in global_chat_dict:
            return {'msg': f"会话: {target_chat_key} 不存在! (；′⌒`)"}
        if PersistentDataManager.instance.update_preset(chat_key=target_chat_key, preset_key=target_preset_key, bot_self_introl=bot_self_introl):
            return {'msg': f"编辑预设: {target_preset_key} (￣▽￣)-ok! (会话: {target_chat_key})", 'is_progress': True}
        else:
            return {'msg': f"编辑预设: {target_preset_key} (会话: {target_chat_key}) 错误 ＞﹏＜!", 'is_progress': True}
    else:   # 当前会话应用
        if PersistentDataManager.instance.update_preset(chat_key=chat.get_chat_key(), preset_key=target_preset_key, bot_self_introl=bot_self_introl):
            return {'msg': f"编辑预设: {target_preset_key} (￣▽￣)-ok!", 'is_progress': True}
        else:
            return {'msg': f"编辑预设: {target_preset_key} 错误 ＞﹏＜!", 'is_progress': True}

@cmd.register(route='rg/del', params=['preset_key'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    target_preset_key = param_dict['preset_key']

    if option_dict.get('global'):   # 全局应用
        err_cnt = 0
        for chat_key in global_chat_dict.keys():
            if not PersistentDataManager.instance.del_preset(chat_key=chat_key, preset_key=target_preset_key):
                err_cnt += 1
        return {'msg': f"删除预设: {target_preset_key} (￣▽￣)-ok! (所有会话) {f'错误:{err_cnt}' if err_cnt else ''}", 'is_progress': True}
    elif option_dict.get('target'): # 指定会话应用
        target_chat_key = option_dict.get('target')
        if target_chat_key not in global_chat_dict:
            return {'msg': f"会话: {target_chat_key} 不存在! (；′⌒`)"}
        if PersistentDataManager.instance.del_preset(chat_key=target_chat_key, preset_key=target_preset_key):
            return {'msg': f"删除预设: {target_preset_key} (￣▽￣)-ok! (会话: {target_chat_key})", 'is_progress': True}
        else:
            return {'msg': f"删除预设: {target_preset_key} (会话: {target_chat_key}) 错误 ＞﹏＜!", 'is_progress': True}
    else:   # 当前会话应用
        if PersistentDataManager.instance.del_preset(chat_key=chat.get_chat_key(), preset_key=target_preset_key):
            return {'msg': f"删除预设: {target_preset_key} (￣▽￣)-ok!", 'is_progress': True}
        else:
            return {'msg': f"删除预设: {target_preset_key} 错误 ＞﹏＜!", 'is_progress': True}

@cmd.register(route='rg/reset', params=['preset_key'])
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    target_preset_key = param_dict['preset_key']

    if option_dict.get('global'):   # 全局应用
        err_cnt = 0
        for chat_key in global_chat_dict.keys():
            if not PersistentDataManager.instance.reset_preset(chat_key=chat_key, preset_key=target_preset_key):
                err_cnt += 1
        return {'msg': f"重置预设: {target_preset_key} (￣▽￣)-ok! (所有会话) {f'错误:{err_cnt}' if err_cnt else ''}", 'is_progress': True}
    elif option_dict.get('target'): # 指定会话应用
        target_chat_key = option_dict.get('target')
        if target_chat_key not in global_chat_dict:
            return {'msg': f"会话: {target_chat_key} 不存在! (；′⌒`)"}
        if PersistentDataManager.instance.reset_preset(chat_key=target_chat_key, preset_key=target_preset_key):
            return {'msg': f"重置预设: {target_preset_key} (￣▽￣)-ok! (会话: {target_chat_key})", 'is_progress': True}
        else:
            return {'msg': f"重置预设: {target_preset_key} (会话: {target_chat_key}) 错误 ＞﹏＜!", 'is_progress': True}
    else:   # 当前会话应用
        if PersistentDataManager.instance.reset_preset(chat_key=chat.get_chat_key(), preset_key=target_preset_key):
            return {'msg': f"重置预设: {target_preset_key} (￣▽￣)-ok!", 'is_progress': True}
        else:
            return {'msg': f"重置预设: {target_preset_key} 错误 ＞﹏＜!", 'is_progress': True}

@cmd.register(route='rg/on')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    if option_dict.get('global'):
        for chat in global_chat_dict.values():
            chat.toggle_chat(enabled=True)
        return {'msg': f"启用所有会话 (￣▽￣)-ok!"}
    elif option_dict.get('target'):
        global_chat_dict[option_dict.get('target')].toggle_chat(enabled=True)
        return {'msg': f"启用会话: {option_dict.get('target')} (￣▽￣)-ok!"}
    else:
        chat.toggle_chat(enabled=True)
        return {'msg': f"启用当前会话 (￣▽￣)-ok!"}

@cmd.register(route='rg/off')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    if option_dict.get('global'):
        for chat in global_chat_dict.values():
            chat.toggle_chat(enabled=False)
        return {'msg': f"禁用所有会话 (￣▽￣)-ok!"}
    elif option_dict.get('target'):
        global_chat_dict[option_dict.get('target')].toggle_chat(enabled=False)
        return {'msg': f"禁用会话: {option_dict.get('target')} (￣▽￣)-ok!"}
    else:
        chat.toggle_chat(enabled=False)
        return {'msg': f"禁用当前会话 (￣▽￣)-ok!"}

@cmd.register(route='rg/lock')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    if option_dict.get('global'):
        for chat in global_chat_dict.values():
            chat.toggle_auto_switch(enabled=False)
        return {'msg': f"锁定所有会话 (￣▽￣)-ok!"}
    elif option_dict.get('target'):
        global_chat_dict[option_dict.get('target')].toggle_auto_switch(enabled=False)
        return {'msg': f"锁定会话: {option_dict.get('target')} (￣▽￣)-ok!"}
    else:
        chat.toggle_auto_switch(enabled=False)
        return {'msg': f"锁定当前会话 (￣▽￣)-ok!"}

@cmd.register(route='rg/unlock')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    if option_dict.get('global'):
        for chat in global_chat_dict.values():
            chat.toggle_auto_switch(enabled=True)
        return {'msg': f"解锁所有会话 (￣▽￣)-ok!"}
    elif option_dict.get('target'):
        global_chat_dict[option_dict.get('target')].toggle_auto_switch(enabled=True)
        return {'msg': f"解锁会话: {option_dict.get('target')} (￣▽￣)-ok!"}
    else:
        chat.toggle_auto_switch(enabled=True)
        return {'msg': f"解锁当前会话 (￣▽￣)-ok!"}

@cmd.register(route='rg/ext')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    ext_info:str = ''
    for ext in global_extensions.values():
        ext_info += f"  {ext.generate_short_description()}"
    return {'msg': f"已加载的扩展:\n{ext_info}"}

@cmd.register(route='rg/chats')
def _(option_dict, param_dict, chat:Chat, chat_presets_dict:dict):
    chat_info:str = ''
    for chat in global_chat_dict.values():
        chat_info += f"+ {chat.generate_description()}"
    return {'msg': f"当前已加载的会话:\n{chat_info}"}



# 提交指令注册
cmd.submit_commands()

# if __name__ == '__main__':
#     print(cmd.execute(
#         command='rg new -target group_123456 test test_intro 123',
#         chat=None,
#         chat_presets_dict={},
#     ))