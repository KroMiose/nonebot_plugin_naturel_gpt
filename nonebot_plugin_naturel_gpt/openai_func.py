from nonebot.log import logger

import openai

from transformers import GPT2TokenizerFast
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

start_sequence = "\nAI:"
restart_sequence = "\nHuman: "


class TextGenerator:
    def __init__(self, api_keys: list, config: dict):
        self.api_keys = api_keys
        self.key_index = 0
        self.config = config

    # 获取文本生成
    def get_response(self, prompt: str, type: str = 'chat', custom: dict = {}) -> str:
        # if True:
        #     return '测试中...'
        for i in range(len(self.api_keys)):
            if type == 'chat':
                res, success = self.get_chat_response(self.api_keys[self.key_index], prompt, custom)
            elif type == 'summarize':
                res, success = self.get_summarize_response(self.api_keys[self.key_index], prompt, custom)
            elif type == 'impression':
                res, success = self.get_impression_response(self.api_keys[self.key_index], prompt, custom)
            if success:
                return res
            self.key_index = (self.key_index + 1) % len(self.api_keys)
            logger.warning(f"当前 Api Key 失效，正在尝试使用下一个 Api Key")
        logger.error("无法连接到 OpenAi 或者当前所有 Api Key 失效")
        return "哎呀，OpenAi Api 好像挂了呢 (´；ω；`)"

    # 对话文本生成
    def get_chat_response(self, key:str, prompt:str, custom:dict = {}) -> str:
        openai.api_key = key
        try:
            response = openai.Completion.create(
                model=self.config['model'],
                prompt=prompt,
                temperature=self.config['temperature'],
                max_tokens=self.config['max_tokens'],
                top_p=self.config['top_p'],
                frequency_penalty=self.config['frequency_penalty'],
                presence_penalty=self.config['presence_penalty'],
                stop=[f"\n{custom.get('bot_name', 'AI')}:", f"\n{custom.get('sender_name', 'Human')}:", '\n\n']
            )
            res = response['choices'][0]['text'].strip()
            if start_sequence[1:] in res:
                res = res.split(start_sequence[1:])[1]
            return res, True
        except Exception as e:
            return f"请求 OpenAi Api 时发生错误: {e}", False

    # 总结文本生成
    def get_summarize_response(self, key:str, prompt:str, custom:dict = {}) -> str:
        openai.api_key = key
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0.7,
                max_tokens=512,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            res = response['choices'][0]['text'].strip()
            return res, True
        except Exception as e:
            return f"请求 OpenAi Api 时发生错误: {e}", False

    # 印象文本生成
    def get_impression_response(self, key:str, prompt:str, custom:dict = {}) -> str:
        openai.api_key = key
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0.7,
                max_tokens=512,
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
        return len(tokenizer.encode(msg))