import re
import os
import httpx
from typing import Tuple, Dict, Optional
from .logger import logger
from nonebot.utils import run_sync
from tiktoken import Encoding, encoding_for_model

from openai import OpenAI
from .singleton import Singleton

enc_cache: Dict[str, Encoding] = {}
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class TextGenerator(Singleton["TextGenerator"]):
    def init(self, api_keys: list, config: dict, proxy: Optional[str] = None, base_url: str = ''):
        self.api_keys = api_keys
        self.key_index = 0
        self.config = config
        self.proxy = proxy
        if self.proxy and not self.proxy.startswith('http'):
            self.proxy = 'http://' + self.proxy
        self.base_url = base_url or 'https://api.openai.com/v1'

    def _get_client(self, api_key: str) -> OpenAI:
        if self.proxy:
            http_client = httpx.Client(proxies=self.proxy, timeout=httpx.Timeout(self.config.get('timeout', 30)))
            return OpenAI(api_key=api_key, base_url=self.base_url, http_client=http_client)
        return OpenAI(api_key=api_key, base_url=self.base_url)

    @run_sync
    def get_response(self, prompt, type: str = 'chat', custom: dict = {}) -> Tuple[str, bool]:
        """获取文本生成"""
        res, success = ('', False)
        for _ in range(len(self.api_keys)):
            client = self._get_client(self.api_keys[self.key_index])

            try:
                if type == 'chat':
                    res, success = self.get_chat_response(client, prompt, custom)
                elif type == 'summarize':
                    res, success = self.get_summarize_response(client, prompt, custom)
                elif type == 'impression':
                    res, success = self.get_impression_response(client, prompt, custom)
                else:
                    res, success = (f'未知类型:{type}', False)
            except Exception as e:
                res = f"请求 OpenAi Api 时发生错误: {e}"
                success = False

            if success:
                return res, True

            # 请求错误处理
            if "Rate limit" in res:
                res = '超过每分钟请求次数限制，喝杯茶休息一下吧 (´；ω`)'
                break
            elif "Error communicating" in res:
                res = '与 OpenAi 通信时发生错误 (´；ω`)'
            else:
                res = '哎呀，发生了未知错误 (´；ω`)'
            self.key_index = (self.key_index + 1) % len(self.api_keys)
            logger.warning(f"当前 Api Key({self.key_index}): [{self.api_keys[self.key_index][:4]}...{self.api_keys[self.key_index][-4:]}] 请求错误，尝试使用下一个...")
        logger.error("请求 OpenAi 发生错误，请检查 Api Key 是否正确或者查看控制台相关日志")
        return res, False

    def get_chat_response(self, client: OpenAI, prompt, custom: dict = {}) -> Tuple[str, bool]:
        """对话文本生成"""
        try:
            should_use_chat = self.config['model'].startswith('gpt-3.5-turbo') or self.config['model'].startswith('gpt-4')
            if should_use_chat:
                response = client.chat.completions.create(
                    model=self.config['model'],
                    messages=prompt if isinstance(prompt, list) else [
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
                res = ''
                for choice in response.choices:
                    res += choice.message.content or ''
            else:
                response = client.completions.create(
                    model=self.config['model'],
                    prompt=prompt,
                    temperature=self.config['temperature'],
                    max_tokens=self.config['max_tokens'],
                    top_p=self.config['top_p'],
                    frequency_penalty=self.config['frequency_penalty'],
                    presence_penalty=self.config['presence_penalty'],
                    stop=[f"\n{custom.get('bot_name', 'AI')}:", f"\n{custom.get('sender_name', 'Human')}:"]
                )
                res = response.choices[0].text.strip() if response.choices else ''
            res = res.strip()
            # 去掉头尾引号（如果有）
            if res.startswith('"') and res.endswith('"'):
                res = res[1:-1]
            if res.startswith("'") and res.endswith("'"):
                res = res[1:-1]
            # 去掉可能存在的开头起始标志
            bot_name = custom.get('bot_name', 'AI')
            if res.startswith(f"{bot_name}:") or res.startswith(f"{bot_name}："):
                res = res[len(bot_name) + 1:]
            # 替换多段回应中的回复起始标志
            res = res.replace(f"\n\n{bot_name}:", "*;")
            # 正则匹配去掉多余的诸如 "[hh:mm:ss aa] bot_name:" 的形式
            res = re.sub(r"\[\d{2}:\d{2}:\d{2} [AP]M\] ?" + bot_name + r":", "", res)
            return res, True
        except Exception as e:
            return f"请求 OpenAi Api 时发生错误: {e}", False

    def get_summarize_response(self, client: OpenAI, prompt: str, custom: dict = {}) -> Tuple[str, bool]:
        """总结文本生成"""
        try:
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'user', 'content': prompt},
                ],
                temperature=0.6,
                max_tokens=self.config.get('max_summary_tokens', 512),
                top_p=1,
                frequency_penalty=0.2,
                presence_penalty=0.2,
                timeout=self.config.get('timeout', 30),
            )
            res = ''
            for choice in response.choices:
                res += choice.message.content or ''
            res = res.strip()
            if res.startswith('"') and res.endswith('"'):
                res = res[1:-1]
            if res.startswith("'") and res.endswith("'"):
                res = res[1:-1]
            return res, True
        except Exception as e:
            return f"请求 OpenAi Api 时发生错误: {e}", False

    def get_impression_response(self, client: OpenAI, prompt: str, custom: dict = {}) -> Tuple[str, bool]:
        """印象文本生成"""
        try:
            response = client.chat.completions.create(
                model='gpt-3.5-turbo-0301',
                messages=[
                    {'role': 'user', 'content': prompt},
                ],
                temperature=0.6,
                max_tokens=self.config.get('max_summary_tokens', 512),
                top_p=1,
                frequency_penalty=0.2,
                presence_penalty=0.2,
                timeout=self.config.get('timeout', 30),
            )
            res = ''
            for choice in response.choices:
                res += choice.message.content or ''
            res = res.strip()
            if res.startswith('"') and res.endswith('"'):
                res = res[1:-1]
            if res.startswith("'") and res.endswith("'"):
                res = res[1:-1]
            return res, True
        except Exception as e:
            return f"请求 OpenAi Api 时发生错误: {e}", False

    @staticmethod
    def generate_msg_template(sender: str, msg: str, time_str: str = '') -> str:
        """生成对话模板"""
        return f"{time_str}{sender}: {msg}"

    @staticmethod
    def cal_token_count(text: str, model: str = "gpt-3.5-turbo"):
        """计算字节对编码后的token数量"""
        if model in enc_cache:
            enc = enc_cache[model]
        else:
            enc = encoding_for_model(model)
            enc_cache[model] = enc
        return len(enc.encode(text))
