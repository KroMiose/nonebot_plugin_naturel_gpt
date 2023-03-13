from typing import Callable, Dict, List, Tuple, Union

# 选项类型  bool只要有就是True，str则需要跟上参数值
option_type = {
    'target': str,
    'global': bool,
    'admin': bool,
    'deep': bool,
    'to_default': bool,
    'default': str,
}

# 指令路由 通过指令路由来规范指令的参数格式
# 指令路由: [参数1, 参数2, ...] 多余的参数会被拼接到最后一个参数中
command_router = {
    'rg': {'arg_list': [], 'func': None},
    # 'rg/help': [],
    # 'rg/on': [],
    # 'rg/off': [],
    # 'rg/set': ['preset_key'],
    # 'rg/new': ['preset_key', 'preset_intro'],
    # 'rg/del': ['preset_key'],
    # 'rg/edit': ['preset_key', 'preset_intro'],
    # 'rg/reset': ['preset_key'],
    # # 待补充...
}

class CommandManager:
    def __init__(self):
        self.command_router = {}

    # def register_command(self, route:str, func:Callable, params:list=[]):
    #     """注册指令修饰方法"""
    #     command_router[route] = {'arg_list': params, 'func': func}

    def register_command(self, route, params:list=[]):
        """注册指令修饰方法"""
        print('register_command:', route, params)
        def wrapper(func):
            self.command_router[route] = {'arg_list': params, 'func': func}
            return func
        return wrapper

    def execute(self, cmd:str):
        """执行指令"""
        option_dict, param_dict, target_route = self.resolve_command(cmd)
        if target_route:
            return self.command_router[target_route]['func'](option_dict, param_dict)
        else:
            return '指令解析失败'

    def submit_commands(self):
        """提交指令注册 *在所有指令注册完成后调用*"""
        # 将指令路由字典根据键中包含的`/`数量进行降序排序 以便于匹配时优先匹配更长的指令
        self.command_router = dict(sorted(self.command_router.items(), key=lambda x: len(x[0].split('/')), reverse=True))
        print('所有指令注册完成 共计:', len(self.command_router), '条指令')

    def resolve_command(self, command):
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
                    cmd_list = cmd_list[len(route.split('/')):]
                    for i in range(len(params_list) - 1):
                        param_dict[params_list[i]] = cmd_list[i]
                    # 将剩余的内容以空格为间隔拼接后存放到最后一个参数中
                    param_dict[params_list[-1]] = ' '.join(cmd_list[len(params_list) - 1:])
                    target_route = route
                    break
            except: # 解析出错跳过
                continue
        else:
            param_dict = {}
        return option_dict, param_dict, target_route

cm = CommandManager()

# 注册指令
@cm.register_command(route='rg')
def _(option_dict, param_dict):
    print('rg')
    print('options:', option_dict)
    print('param:', param_dict)

@cm.register_command(route='rg/new', params=['preset_key', 'preset_intro'])
def _(option_dict, param_dict):
    print('rg/new')
    print('options:', option_dict)
    print('param:', param_dict)

@cm.register_command(route='rg/edit', params=['preset_key', 'preset_intro'])
def _(option_dict, param_dict):
    print('rg/edit')
    print('options:', option_dict)
    print('param:', param_dict)

@cm.register_command(route='rg/del', params=['preset_key'])
def _(option_dict, param_dict):
    print('rg/del')
    print('options:', option_dict)
    print('param:', param_dict)

@cm.register_command(route='rg/reset', params=['preset_key'])
def _(option_dict, param_dict):
    print('rg/reset')
    print('options:', option_dict)
    print('param:', param_dict)

# 提交指令注册
cm.submit_commands()

if __name__ == '__main__':
    print(cm.execute('rg new -target group_123456 test test_intro 123'))

