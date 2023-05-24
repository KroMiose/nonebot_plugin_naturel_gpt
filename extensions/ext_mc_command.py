from .Extension import Extension


# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config: dict = {
    "name": "RunCommand",  # 扩展名称，用于标识扩展
    "arguments": {
        "command": "str",  # 关键字
    },
    "description": "Using Rcon to execute Minecraft server commands. (usage in response: /#RunCommand&/tp Tom Alice#/ teleport Tom to Alice)",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 10,
    # 作者信息
    "author": "KroMiose",
    # 版本
    "version": "0.0.1",
    # 扩展简介
    "intro": "执行Minecraft服务器命令",
    # 可用会话类型 (server即MC服务器 | chat即QQ聊天)
    "available": ["server"],
}


class CustomExtension(Extension):
    async def call(self, arg_dict: dict, _: dict) -> dict:
        """当扩展被调用时执行的函数 *由扩展自行实现*

        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值(类型为str)}
        """
        custom_config: dict = self.get_custom_config()  # 获取yaml中的配置信息

        command = arg_dict.get("command", "")  # 命令

        white_list = custom_config.get("match_white_list", [])  # 白名单 留空则不限制
        black_list = custom_config.get("match_black_list", [])  # 黑名单 留空则不限制 优先级高于白名单

        if not command.startswith("/"):  # 补充命令前缀便于检查
            command = "/" + command

        # 将命令中所有的\\替换为\，以便于正常执行
        command = command.replace("\\\\", "\\")

        if command:  # 如果命令不为空
            # 检查命令是否在黑名单中
            if len(black_list) > 0:
                for black_command in black_list:
                    if black_command in command:
                        return {  # 拒绝执行
                            "text": f'[Rcon] 检测到禁止命令: "{black_command}" 拒绝执行',
                            "notify": {
                                "sender": "[Minecraft Server]",
                                "msg": f'Run command failed, command snippet: "{black_command}" in black list. You have no permission to run this command.',
                            },
                            "wake_up": True,
                        }
            # 检查命令是否在白名单中
            if len(white_list) > 0:
                for white_command in white_list:
                    if white_command in command:
                        break  # 命令在白名单中，跳出循环
                else:
                    return {  # 拒绝执行
                        "notify": {
                            "sender": "[Minecraft Server]",
                            "msg": f"Run command failed, command: {command} not in white list. You have no permission to run this command.",
                        },
                        "wake_up": True,
                    }
        else:
            raise Exception("命令为空")

        if command.startswith("/"):  # 去除命令前缀以便执行
            command = command[1:]

        return {  # 允许执行
            "rcon": command,
            "text": f"[Rcon] 正在执行命令: /{command}",
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
