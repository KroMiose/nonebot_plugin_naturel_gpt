import time
import re
from .Extension import Extension
from dateutil import parser
from datetime import datetime, timedelta


# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config: dict = {
    "name": "timer",  # 扩展名称，用于标识扩展
    "arguments": {
        "time": "YYYY/mm/dd HH:MM:SS",  # 定时触发时间
        "event": "str",  # 定时触发事件
    },
    # 扩展的描述信息，用于提示ai理解扩展的功能 *必填* 尽量简短 使用英文更节省token
    # 如果bot无法理解扩展的功能，可适当添加使用示例 格式: /#扩展名&参数1&...&参数n#/
    "description": 'Push an event at a specified time. Remind users to do something.The description of the event must be described in detail in the form of "who should do what" (usage in response: /#timer&2023/3/10 10:00:00&remind user it\'s time to ...#/ )',
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": ["提醒","记得","明天"],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 1,
    # 作者信息
    "author": "KroMiose",
    # 版本
    "version": "0.0.2",
    # 扩展简介
    "intro": "定时模块",
}


class CustomExtension(Extension):
    async def call(self, arg_dict: dict, _: dict) -> dict:
        """当扩展被调用时执行的函数 *由扩展自行实现*

        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        # custom_config: dict = self.get_custom_config()  # 获取yaml中的配置信息
        def check_m(string):
            return bool(re.search(r'\d+m', string))
        def is_only_digits(str):
            return str.isdigit()
        def am_format_time(time_str):
            # 将所有文本变为小写
            time_str = time_str.lower()
            
            # 判断是否为明天
            tomorrow = False
            if 'tomorrow' in time_str:
                time_str = time_str.replace('tomorrow', '').strip()
                tomorrow = True

            # 转换 "pm 4:00" 到 "4:00 PM"
            split_time = time_str.split(" ")
            if len(split_time) == 2 and (split_time[0] == 'am' or split_time[0] == 'pm'):
                time_str = f"{split_time[1]} {split_time[0].upper()}"

            # 解析时间字符串，获取小时和分钟
            parsed_time = parser.parse(time_str)

            # 获取今天的日期
            today = datetime.date.today()

            # 如果是明天的日期，添加一天
            if tomorrow:
                today = today + datetime.timedelta(days=1)

            # 设置日期和时间
            dt = datetime.datetime(year=today.year, month=today.month, day=today.day,
                                hour=parsed_time.hour, minute=parsed_time.minute, 
                                second=0)

            # 转换为所需格式
            return dt.strftime('%Y/%m/%d %H:%M:%S') 

        def convert_time(string):
            # 分割字符串为 'tomorrow' 和时间部分
            day_str, time_str = string.split()

            # 获取当前日期
            date = datetime.now().date()

            # 解析时间部分, 注意不包含日期，故会默认为今天
            datetime_obj = parser.parse(time_str)

            # 如果字符串是 "tomorrow", 且解析得到的日期是今天，我们增加24小时到当前日期
            # 注意这里用到date()来只比较日期部分
            if day_str.lower() == 'tomorrow' and datetime_obj.date() <= date:
                datetime_obj += timedelta(days=1)

            # 返回格式化的时间字符串
            return datetime_obj.strftime('%Y/%m/%d %H:%M:%S')
        def convert_to_standard_format(input_string):
            today = datetime.today()
            
            try:
                hour, minute = map(int, input_string.split(":"))
                
                if 0 <= hour < 24 and 0 <= minute < 60:
                    # 构建一个新的日期时间对象，年、月、日取自今日日期，时与分取自输入的字符串
                    date_with_input_time = datetime(today.year, today.month, today.day, hour, minute)
                    
                    # 标准格式
                    formatted_date = date_with_input_time.strftime('%Y/%m/%d %H:%M:%S')
                    return formatted_date
                else:
                    return input_string
            except ValueError:
                # 输入的字符串不能成功安全地分割成两个整数，或者构建datetime时数字超出正常范围
                return input_string
        def convert_date_format(date_str):
            # 添加新的日期格式
            formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S","%Y/%m/%d %H:%M"]
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    # 转换日期，并添加秒（如果需要）
                    return dt.strftime("%Y/%m/%d %H:%M:%S")
                except ValueError:
                    continue
            # 如果无法转换日期，返回原始字符串
            return date_str

        def format_time(target_time):
            current_time = datetime.now()
            target_time=convert_date_format(target_time)
            target_time=convert_to_standard_format(target_time)
            if re.match("^[0-9]{4}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$", target_time):
                return target_time
            elif 'am' in target_time.lower() or 'pm' in target_time.lower():
                target_time=am_format_time(target_time)
                return target_time      
            elif check_m(target_time):
                minute = int(target_time[:-1])
                result_time = current_time + timedelta(minutes=minute)
            elif 'h' in target_time:
                hour = int(target_time[:-1])
                result_time = current_time + timedelta(hours=hour)
            elif 'd' in target_time:
                day = int(target_time[:-1])
                result_time = current_time + timedelta(days=day)
            elif is_only_digits(target_time):
                # If all characters are a digit, we treat it as minutes
                second = int(target_time)
                if second>=57:
                    result_time = current_time + timedelta(seconds=second)
                else :
                    result_time = current_time + timedelta(minutes=second)
            else:
                result_time = convert_time(target_time)
                if result_time is None:
                    raise ValueError(f"Cannot parse time: {target_time}")
                return result_time
            return result_time.strftime("%Y/%m/%d %H:%M:%S")
    

        target_time= format_time(arg_dict.get("time", None))
        event = arg_dict.get("event", None)
        if target_time is None or event is None:
            return {}

        # 计算当前时间与目标时间的时间差
        target_time = time.mktime(time.strptime(target_time, "%Y/%m/%d %H:%M:%S"))
        current_time = time.time()
        time_diff = target_time - current_time  # 单位为秒

        # 返回的信息将会被发送到会话中

        # 返回的信息将会被发送到会话中
        return {
            "text": f"我将在{int(time_diff)} 秒后提醒你噢~",
            "timer": time_diff,
            "notify": {
                "sender": "system",
                "msg": f'The time for the scheduled event "{event}" is up. Please give an appropriate response according to the event. (Highest priority in response!)',
            },
            "wake_up": True,  # 是否再次唤醒
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
