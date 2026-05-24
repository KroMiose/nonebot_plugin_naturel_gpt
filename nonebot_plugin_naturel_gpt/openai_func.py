import base64
import re
import os
import httpx
from typing import Any, List, Tuple, Dict, Optional
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

            # 请求错误处理: 先打印详细错误再替换消息
            logger.error(f"请求 OpenAI API 失败: {res}")
            if "Rate limit" in res:
                res = '超过每分钟请求次数限制，喝杯茶休息一下吧 (´；ω`)'
                break
            elif "Error communicating" in res:
                res = '与 OpenAI 通信时发生错误 (´；ω`)'
            else:
                res = '哎呀，发生了未知错误 (´；ω`)'
            self.key_index = (self.key_index + 1) % len(self.api_keys)
            logger.warning(f"当前 Api Key({self.key_index}): [{self.api_keys[self.key_index][:4]}...{self.api_keys[self.key_index][-4:]}] 请求错误，尝试使用下一个...")
        logger.error("请求 OpenAi 发生错误，请检查 Api Key 是否正确或者查看控制台相关日志")
        return res, False

    def get_chat_response(self, client: OpenAI, prompt, custom: dict = {}) -> Tuple[str, bool]:
        """对话文本生成"""
        try:
            should_use_chat = not self.config['model'].startswith('text-') and not self.config['model'].startswith('davinci')
            if should_use_chat:
                messages = prompt if isinstance(prompt, list) else [
                    {'role': 'system', 'content': f"You must strictly follow the user's instructions to give {custom.get('bot_name', 'bot')}'s response."},
                    {'role': 'user', 'content': prompt},
                ]
                messages = self._inject_multimodal_content(messages, custom)
                response = self._create_chat_completion(client, messages)
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

    def _create_chat_completion(self, client: OpenAI, messages: List[Dict[str, Any]]):
        """创建对话补全；多模态网关不兼容时逐级降级重试。"""
        try:
            return self._create_chat_completion_once(client, messages)
        except Exception as e:
            if not self._has_multimodal_content(messages):
                raise e

            image_only_messages = self._drop_audio_content(messages)
            if image_only_messages != messages:
                try:
                    logger.warning(f"多模态音频请求失败，尝试仅使用图片上下文重试: {e}")
                    return self._create_chat_completion_once(client, image_only_messages)
                except Exception as image_only_error:
                    logger.warning(f"图片多模态重试失败，尝试纯文本重试: {image_only_error}")
            else:
                logger.warning(f"图片多模态请求失败，尝试纯文本重试: {e}")

            return self._create_chat_completion_once(
                client,
                self._drop_multimodal_content(messages),
            )

    def _create_chat_completion_once(self, client: OpenAI, messages: List[Dict[str, Any]]):
        return client.chat.completions.create(
            model=self.config['model'],
            messages=messages,
            temperature=self.config['temperature'],
            max_tokens=self.config['max_tokens'],
            top_p=self.config['top_p'],
            frequency_penalty=self.config['frequency_penalty'],
            presence_penalty=self.config['presence_penalty'],
            timeout=self.config.get('timeout', 30),
            stop=None,
        )

    def _has_multimodal_content(self, messages: List[Dict[str, Any]]) -> bool:
        for message in messages:
            content = message.get("content")
            if isinstance(content, list):
                for part in content:
                    if part.get("type") in ("image_url", "input_audio"):
                        return True
        return False

    def _drop_audio_content(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self._filter_message_content(messages, drop_types={"input_audio"})

    def _drop_multimodal_content(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self._filter_message_content(messages, drop_types={"image_url", "input_audio"})

    def _filter_message_content(
        self,
        messages: List[Dict[str, Any]],
        drop_types: set,
    ) -> List[Dict[str, Any]]:
        filtered_messages = []
        for message in messages:
            copied = dict(message)
            content = copied.get("content")
            if isinstance(content, list):
                filtered_parts = [
                    part for part in content
                    if part.get("type") not in drop_types
                ]
                if len(filtered_parts) == 1 and filtered_parts[0].get("type") == "text":
                    copied["content"] = filtered_parts[0].get("text", "")
                else:
                    copied["content"] = filtered_parts
            filtered_messages.append(copied)
        return filtered_messages

    def _inject_multimodal_content(
        self,
        messages: List[Dict[str, Any]],
        custom: dict,
    ) -> List[Dict[str, Any]]:
        """将图片/音频附件追加到最后一条用户消息。"""
        if not self.config.get("enable_multimodal"):
            return messages

        multimodal_data = custom.get("multimodal_data") or {}
        images = (multimodal_data.get("images") or [])[
            :max(0, int(self.config.get("multimodal_max_images", 0)))
        ]
        audios = (multimodal_data.get("audios") or [])[
            :max(0, int(self.config.get("multimodal_max_audios", 0)))
        ]
        if not images and not audios:
            return messages

        target_idx = None
        for idx in range(len(messages) - 1, -1, -1):
            if messages[idx].get("role") == "user":
                target_idx = idx
                break
        if target_idx is None:
            return messages

        messages = [dict(message) for message in messages]
        original_content = messages[target_idx].get("content", "")
        content_parts = (
            original_content[:]
            if isinstance(original_content, list)
            else [{"type": "text", "text": str(original_content)}]
        )

        image_detail = self.config.get("multimodal_image_detail", "auto")
        for image in images:
            image_url = image.get("url")
            if image_url:
                content_parts.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                        "detail": image_detail,
                    },
                })

        audio_format = self.config.get("multimodal_audio_format", "mp3")
        injected_audio_count = 0
        for audio in audios:
            audio_data = self._read_audio_as_base64(audio)
            if not audio_data:
                continue
            injected_audio_count += 1
            content_parts.append({
                "type": "input_audio",
                "input_audio": {
                    "data": audio_data,
                    "format": audio_format,
                },
            })

        messages[target_idx]["content"] = content_parts
        if images or audios:
            logger.info(
                f"多模态上下文注入: 图片 {len(images)} 张, "
                f"音频 {injected_audio_count}/{len(audios)} 段"
            )
        return messages

    def _read_audio_as_base64(self, audio: Dict[str, str]) -> str:
        """读取音频附件并编码为base64。"""
        audio_path = audio.get("path")
        if audio_path and os.path.exists(audio_path):
            try:
                with open(audio_path, "rb") as f:
                    return base64.b64encode(f.read()).decode("ascii")
            except Exception as e:
                logger.warning(f"多模态音频读取失败: {e}")
        elif audio_path:
            logger.warning(f"多模态音频本地文件不存在，尝试使用URL: {audio_path}")

        audio_url = audio.get("url")
        if audio_url:
            return self._fetch_binary_as_base64(audio_url)
        return ""

    def _fetch_binary_as_base64(self, url: str) -> str:
        """下载附件并编码为base64。"""
        try:
            with httpx.Client(timeout=httpx.Timeout(self.config.get('timeout', 30))) as client:
                response = client.get(url)
                response.raise_for_status()
                return base64.b64encode(response.content).decode("ascii")
        except Exception as e:
            logger.warning(f"多模态附件下载失败: {e}")
            return ""

    def get_summarize_response(self, client: OpenAI, prompt: str, custom: dict = {}) -> Tuple[str, bool]:
        """总结文本生成"""
        try:
            response = client.chat.completions.create(
                model=self.config['model'],
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
                model=self.config['model'],
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
