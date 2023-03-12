# 选项类型  bool只要有就是True，str则需要参数值
option_type = {
    'target': str,
    'global': bool,
    'admin': bool,
    'deep': bool,
    'to_default': bool,
    'default': str,
}

# 指令路由 通过指令路由来规范指令的参数格式 指令路由: [参数1, 参数2, ...]
command_router = {
    'rg': [],
    'rg/help': [],
    'rg/on': [],
    'rg/off': [],
    'rg/set': ['preset_key'],
    'rg/new': ['preset_key', 'preset_intro'],
    'rg/del': ['preset_key'],
    'rg/edit': ['preset_key', 'preset_intro'],
    'rg/reset': ['preset_key'],
    # 待补充...
}


def resolve_command(command):
    """解析命令"""
    # 命令格式: 一级命令 二级命令 ... 选项1 选项2 ... 参数1 参数2 参数3
    # 命令名和参数之间必须有一个或多个空格
    # 命令名和参数之间可以有换行

    # 生成命令参数列表
    cmd_list = [c.strip() for c in command.split(' ') if c.strip()]

    # print(cmd_list)

    # 如果是以 - 开头的参数，根据参数类型进行解析
    # 格式: -参数名 参数值 (对于布尔值，参数值可以省略)
    # 生成命令参数字典 并去除已经解析的参数
    option_dict = {}
    for i in range(len(cmd_list)):
        print(cmd_list[i])
        if cmd_list[i].startswith('-'):
            option = cmd_list[i][1:]
            cmd_list[i] = None  # 去除已经解析的参数
            if isinstance(option, bool):
                option_dict[option] = True
            elif isinstance(option, str):
                option_dict[option] = cmd_list[i + 1]
                cmd_list[i + 1] = None  # 去除已经解析的参数

    cmd_list = [c for c in cmd_list if c]  # 去除已经解析的参数

    # 按照 一级命令/二级命令... 匹配命令路由 如果有多余的参数则以空格为间隔拼接后存放到最后一个参数中
    cmd_dict = {}
    for i in range(len(cmd_list)):
        cmd = '/'.join(cmd_list[:i + 1])
        if cmd in command_router:
            cmd_dict[cmd] = cmd_list[i + 1:]
            break

    return cmd_dict, option_dict

if __name__ == '__main__':
    test_command = 'rg new -target group_123456 test test_intro 123'
    cmd_dict, option_dict = resolve_command(test_command)
    print(cmd_dict)
    print(option_dict)
