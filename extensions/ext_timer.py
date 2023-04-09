from .Extension import Extension
import time

# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config:dict = {
    "name": "timer",   # 扩展名称，用于标识扩展
    "arguments": {      
        "time": "YYYY/mm/dd HH:MM:SS",  # 定时触发时间
        "event": "str",         # 定时触发事件
    },
    # 扩展的描述信息，用于提示ai理解扩展的功能 *必填* 尽量简短 使用英文更节省token
    # 如果bot无法理解扩展的功能，可适当添加使用示例 格式: /#扩展名&参数1&...&参数n#/
    "description": "Push an event at a specified time. The description of the event must be described in detail in the form of \"who should do what\" (usage in response: /#timer&2023/3/10 10:00:00&it's time to ...#/ )",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 5,
    # 作者信息
    "author": "KroMiose",
    # 版本
    "version": "0.0.1",
    # 扩展简介
    "intro": "定时模块",
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """ 当扩展被调用时执行的函数 *由扩展自行实现*
        
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息

        target_time = arg_dict.get("time", None)
        event = arg_dict.get("event", None)

        if target_time is None or event is None:
            return {}

        # 计算当前时间与目标时间的时间差
        target_time = time.mktime(time.strptime(target_time, "%Y/%m/%d %H:%M:%S"))
        current_time = time.time()
        time_diff = target_time - current_time  # 单位为秒

        # 返回的信息将会被发送到会话中
        return {
            'text': f"[ext_timer] 已设置定时器，将在 {int(time_diff)} 秒后触发",
            'timer': time_diff,
            'notify': {
                'sender': '[system timer]',
                'msg': f" The time for the scheduled event \"{event}\" is up. Please give an appropriate response according to the event. (Highest priority in response!)"
            },
            'wake_up': True,  # 是否再次唤醒
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)