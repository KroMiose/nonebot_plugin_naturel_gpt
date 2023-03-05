from nonebot.log import logger
from nonebot.utils import run_sync

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import openai
from transformers import GPT2TokenizerFast

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

try:    # 检查openai版本是否高于0.27.0
    import pkg_resources
    openai_version = pkg_resources.get_distribution("openai").version
    if openai_version < '0.27.0':
        logger.warning(f"当前 openai 库版本为 {openai_version}，请更新至 0.27.0 版本以上，否则可能导致 gpt-3.5-turbo 模型无法使用")
except:
    logger.warning(f"无法获取 openai 库版本，请更新至 0.27.0 版本以上，否则 gpt-3.5-turbo 模型将无法使用")

class TextGenerator:
    def __init__(self, api_keys: list, config: dict, proxy = None):
        self.api_keys = api_keys
        self.key_index = 0
        self.config = config
        if proxy:
            if not proxy.startswith('http'):
                proxy = 'http://' + proxy
        openai.proxy = proxy

    # 获取文本生成
    @run_sync
    def get_response(self, prompt, type: str = 'chat', custom: dict = {}) -> str:
        # return 'testing...'
        for _ in range(len(self.api_keys)):
            if type == 'chat':
                res, success = self.get_chat_response(self.api_keys[self.key_index], prompt, custom)
            elif type == 'summarize':
                res, success = self.get_summarize_response(self.api_keys[self.key_index], prompt, custom)
            elif type == 'impression':
                res, success = self.get_impression_response(self.api_keys[self.key_index], prompt, custom)
            if success:
                return res, True

            # 请求错误处理
            if "Rate limit" in res:
                reason = res
                res = '超过每分钟请求次数限制，喝杯茶休息一下吧 (´；ω；`)'
                break
            elif "module 'openai' has no attribute 'ChatCompletion'" in res:
                reason = res
                res = '当前 openai 库版本过低，无法使用 gpt-3.5-turbo 模型 (´；ω；`)'
                break
            elif "Error communicating with OpenAI" in res:
                reason = res
                res = '与 OpenAi 通信时发生错误 (´；ω；`)'
            else:
                reason = res
                res = '哎呀，发生了未知错误 (´；ω；`)'
            self.key_index = (self.key_index + 1) % len(self.api_keys)
            logger.warning(f"当前 Api Key({self.key_index}): [{self.api_keys[self.key_index][:4]}...{self.api_keys[self.key_index][-4:]}] 请求错误，尝试使用下一个...")
            logger.error(f"错误原因: {res} => {reason}")
        logger.error("请求 OpenAi 发生错误，请检查 Api Key 是否正确或者查看控制台相关日志")
        return res, False

    # 对话文本生成
    def get_chat_response(self, key:str, prompt, custom:dict = {}):
        openai.api_key = key
        try:
            if self.config['model'].startswith('gpt-3.5-turbo'):
                response = openai.ChatCompletion.create(
                    model=self.config['model'],
                    messages=prompt if isinstance(prompt, list) else [  # 如果是列表则直接使用，否则按照以下格式转换
                        {'role': 'system', 'content': f"You must strictly follow the user's instructions to give {custom.get('bot_name', 'bot')}'s response."},
                        {'role': 'user', 'content': prompt},
                    ],
                    temperature=self.config['temperature'],
                    max_tokens=self.config['max_tokens'],
                    top_p=self.config['top_p'],
                    frequency_penalty=self.config['frequency_penalty'],
                    presence_penalty=self.config['presence_penalty'],
                    timeout=self.config.get('timeout', 30),
                    stop=[f"\n{custom.get('bot_name', 'AI')}:", f"\n{custom.get('sender_name', 'Human')}:"]
                )
                if self.config.get('__DEBUG__'): logger.info('openai 原始回应 ->',response)
                res = ''
                for choice in response.choices:
                    res += choice.message.content
                res = res.strip()
                # 去掉头尾引号（如果有）
                if res.startswith('"') and res.endswith('"'):
                    res = res[1:-1]
                if res.startswith("'") and res.endswith("'"):
                    res = res[1:-1]
                # 去掉可能存在的开头起始标志
                if res.startswith(f"{custom.get('bot_name', 'AI')}:"):
                    res = res[len(f"{custom.get('bot_name', 'AI')}:"):]
                # 替换多段回应中的回复起始标志
                res = res.replace(f"\n\n{custom.get('bot_name', 'AI')}:", "*;")
            else:
                response = openai.Completion.create(
                    model=self.config['model'],
                    prompt=prompt,
                    temperature=self.config['temperature'],
                    max_tokens=self.config['max_tokens'],
                    top_p=self.config['top_p'],
                    frequency_penalty=self.config['frequency_penalty'],
                    presence_penalty=self.config['presence_penalty'],
                    stop=[f"\n{custom.get('bot_name', 'AI')}:", f"\n{custom.get('sender_name', 'Human')}:"]
                )
                res = response['choices'][0]['text'].strip()
            return res, True
        except Exception as e:
            return f"请求 OpenAi Api 时发生错误: {e}", False

    # 总结文本生成
    def get_summarize_response(self, key:str, prompt:str, custom:dict = {}):
        openai.api_key = key
        try:
            if self.config['model'].startswith('gpt-3.5-turbo'):
                response = openai.ChatCompletion.create(
                    model=self.config['model'],
                    messages=[
                        {'role': 'user', 'content': prompt},
                    ],
                    temperature=0.6,
                    max_tokens=self.config.get('max_summary_tokens', 512),
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    timeout=self.config.get('timeout', 30),
                )
                if self.config.get('__DEBUG__'): logger.info('openai 原始回应 ->',response)
                res = ''
                for choice in response.choices:
                    res += choice.message.content
                res = res.strip()
                # 去掉头尾引号（如果有）
                if res.startswith('"') and res.endswith('"'):
                    res = res[1:-1]
                if res.startswith("'") and res.endswith("'"):
                    res = res[1:-1]
            else:
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt,
                    temperature=0.6,
                    max_tokens=self.config.get('max_summary_tokens', 512),
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                res = response['choices'][0]['text'].strip()
            return res, True
        except Exception as e:
            return f"请求 OpenAi Api 时发生错误: {e}", False

    # 印象文本生成
    def get_impression_response(self, key:str, prompt:str, custom:dict = {}):
        openai.api_key = key
        try:
            if self.config['model'].startswith('gpt-3.5-turbo'):
                response = openai.ChatCompletion.create(
                    model=self.config['model'],
                    messages=[
                        {'role': 'user', 'content': prompt},
                    ],
                    temperature=0.6,
                    max_tokens=self.config.get('max_summary_tokens', 512),
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    timeout=self.config.get('timeout', 30),
                )
                if self.config.get('__DEBUG__'): logger.info('openai 原始回应 ->',response)
                res = ''
                for choice in response.choices:
                    res += choice.message.content
                res = res.strip()
                # 去掉头尾引号（如果有）
                if res.startswith('"') and res.endswith('"'):
                    res = res[1:-1]
                if res.startswith("'") and res.endswith("'"):
                    res = res[1:-1]
            else:
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt,
                    temperature=0.6,
                    max_tokens=self.config.get('max_summary_tokens', 512),
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                res = response['choices'][0]['text'].strip()
            return res, True
        except Exception as e:
            return f"请求 OpenAi Api 时发生错误: {e}", False

    # 生成对话模板
    @staticmethod
    def generate_msg_template(sender:str, msg: str) -> str:
        return f"{sender}: {msg}\n"

    # 计算字符串的token数量
    @staticmethod
    def cal_token_count(msg: str) -> int:
        try:
            return len(tokenizer.encode(msg))
        except:
            return 2048