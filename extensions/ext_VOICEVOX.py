"""
启用tecent翻译 可以在YAML 中填入下面的参数
ng_voice_translate_on : True
tencentcloud_common_region : "ap-shanghai"
tencentcloud_common_secretid : "xxxxx"
tencentcloud_common_secretkey : "xxxxx"
ng_voice_tar : 'ja'
"""

import asyncio
import base64
import os
import random
import uuid
from binascii import b2a_base64
from hashlib import sha1
from hmac import new
from sys import maxsize, version_info
from time import time
from urllib.parse import urlencode

import anyio
from aiohttp import request
from httpx import AsyncClient
from loguru import logger
from nonebot.exception import ActionFailed

from .Extension import Extension

try:
    from ujson import loads as loadJsonS
except:
    from json import loads as loadJsonS


# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config: dict = {
    "name": "voice",  # 扩展名称，用于标识扩展
    "arguments": {
        "sentence": "str",  # 需要转换的文本
        "emotion": "str",  # 情感
    },
    # 扩展的描述信息，用于提示ai理解扩展的功能 *必填* 尽量简短 使用英文更节省token
    "description": 'Send a voice sentence. The emotional parameter must be one of "normal,sweet,tsundere,sexy,whisper,murmur" (usage in response: /#voice&hello&sweet#/) ',
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 作者信息
    "author": "恋如雨止",
    # 版本
    "version": "0.0.2",
    # 扩展简介
    "intro": "发送语音消息(支持翻译)",
    # 可用会话类型 (server即MC服务器 | chat即QQ聊天)
    "available": ["chat"],
}

# 情感参数表
emotion_rate_dict = {
    "normal": {
        "custom_attributes": {
            "speed_scale": 1,
            "volume_scale": 1,
            "intonation_scale": 1,
            "pre_phoneme_length": 0.1,
            "post_phoneme_length": 0.1,
        },
        "name": "ノーマル",
    },
    "sweet": {
        "custom_attributes": {
            "speed_scale": 1.1,
            "volume_scale": 0.9,
            "intonation_scale": 1.3,
            "pre_phoneme_length": 0.2,
            "post_phoneme_length": 0.2,
        },
        "name": "あまあま",
    },
    "tsundere": {
        "custom_attributes": {
            "speed_scale": 1.0,
            "volume_scale": 1.1,
            "intonation_scale": 1.2,
            "pre_phoneme_length": 0.3,
            "post_phoneme_length": 0.3,
        },
        "name": "ツンツン",
    },
    "sexy": {
        "custom_attributes": {
            "speed_scale": 0.9,
            "volume_scale": 1.2,
            "intonation_scale": 1.1,
            "pre_phoneme_length": 0.4,
            "post_phoneme_length": 0.4,
        },
        "name": "セクシー",
    },
    "whisper": {
        "custom_attributes": {
            "speed_scale": 0.8,
            "volume_scale": 1.3,
            "intonation_scale": 1.0,
            "pre_phoneme_length": 0.5,
            "post_phoneme_length": 0.5,
        },
        "name": "ささやき",
    },
    "murmur": {
        "custom_attributes": {
            "speed_scale": 0.7,
            "volume_scale": 1.4,
            "intonation_scale": 0.9,
            "pre_phoneme_length": 0.6,
            "post_phoneme_length": 0.6,
        },
        "name": "ヒソヒソ",
    },
}

# 情感翻译映射表
emotion_translate_jp2en = {
    "ノーマル": "normal",
    "あまあま": "sweet",
    "ツンツン": "tsundere",
    "セクシー": "sexy",
    "ささやき": "whisper",
    "ヒソヒソ": "murmur",
}
emotion_translate_en2jp = {f: t for t, f in emotion_translate_jp2en.items()}


class CustomExtension(Extension):
    async def call(self, arg_dict: dict, _: dict) -> dict:
        """当扩展被调用时执行的函数 *由扩展自行实现*

        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        custom_config: dict = self.get_custom_config()  # 获取yaml中的配置信息

        ng_voice_translate_on = custom_config.get(
            "ng_voice_translate_on", False
        )  # 是否启用翻译
        tencentcloud_common_region = custom_config.get(
            "tencentcloud_common_region", "ap-shanghai"
        )  # 腾讯翻译-地区
        tencentcloud_common_secretid = custom_config.get(
            "tencentcloud_common_secretid", "xxxxx"
        )  # 腾讯翻译-密钥id
        tencentcloud_common_secretkey = custom_config.get(
            "tencentcloud_common_secretkey", "xxxxx"
        )  # 腾讯翻译-密钥
        ng_voice_tar = custom_config.get("g_voice_tar", "ja")  # 翻译目标语言
        is_base64 = custom_config.get("is_base64", False)  # 是否使用base64编码

        character = custom_config.get("character", "もち子さん")  # 人物
        url = custom_config.get("api_url", "127.0.0.1:50021")

        if not url:  # 如果没有配置语音服务器url则返回错误信息
            return {"text": "[ext_VOICEVOX] 未配置语音服务器url"}
        if not url.startswith("http"):  # 如果不是http开头则添加
            url = f"http://{url}"
        if not url.endswith("/"):  # 如果不是/结尾则添加
            url = f"{url}/"

        # 音频缓存文件夹
        voice_path = "voice_cache/"
        if not os.path.exists(voice_path):
            os.mkdir(voice_path)

        # 获取参数
        raw_text = arg_dict.get("sentence", None)
        emotion_key = arg_dict.get("emotion", "normal")
        # 判断情感索引是否存在 如果不存在则使用默认情感
        if emotion_key not in self.character_emotion_dict[character]:
            emotion_key = "normal"

        """ 腾讯翻译 """
        # 腾讯翻译-签名
        # config = get_driver().config

        async def getReqSign(params: dict) -> str:
            common = {
                "Action": "TextTranslate",
                "Region": f"{tencentcloud_common_region}",
                "Timestamp": int(time()),
                "Nonce": random.randint(1, maxsize),
                "SecretId": f"{tencentcloud_common_secretid}",
                "Version": "2018-03-21",
            }
            params.update(common)
            sign_str = "POSTtmt.tencentcloudapi.com/?"
            sign_str += "&".join("%s=%s" % (k, params[k]) for k in sorted(params))
            secret_key = tencentcloud_common_secretkey
            if version_info[0] > 2:
                sign_str = bytes(sign_str, "utf-8")
                secret_key = bytes(secret_key, "utf-8")
            hashed = new(secret_key, sign_str, sha1)
            signature = b2a_base64(hashed.digest())[:-1]
            if version_info[0] > 2:
                signature = signature.decode()
            return signature

        async def q_translate(message) -> str:
            _source_text = message
            _source = "auto"
            _target = ng_voice_tar
            try:
                endpoint = "https://tmt.tencentcloudapi.com"
                params = {
                    "Source": _source,
                    "SourceText": _source_text,
                    "Target": _target,
                    "ProjectId": 0,
                }
                params["Signature"] = await getReqSign(params)
                # 加上超时参数
                async with request("POST", endpoint, data=params) as resp:
                    data = loadJsonS(await asyncio.wait_for(resp.read(), timeout=30))[
                        "Response"
                    ]
                    message = data["TargetText"]
            except ActionFailed as e:
                logger.warning(
                    f"ActionFailed {e.info['retcode']} {e.info['msg'].lower()} {e.info['wording']}"
                )
            except TimeoutError as e:
                logger.warning(f"TimeoutError {e}")
            return message

        """ 腾讯翻译结束 """

        if ng_voice_translate_on is True:
            t_result = await q_translate(raw_text)
        else:
            t_result = raw_text
        text = t_result + "~"  # 加上一个字符，避免合成语音丢失结尾

        # 从self.character_emotion_dict中获取角色，如果emotion_key不存在则使用第一个
        speaker = (
            self.character_emotion_dict[character][
                emotion_translate_en2jp[emotion_key]
            ]["speaker"]
            if emotion_translate_en2jp[emotion_key]
            in self.character_emotion_dict[character]
            else self.character_emotion_dict[character][0]["speaker"]
        )
        # 根据emotion_key获取从emotion_rate_dict获取自定义属性
        custom_attributes = emotion_rate_dict[emotion_key]["custom_attributes"]

        # 发送查询请求并保存结果
        params = {
            "text": text,
            "speaker": speaker,
        }
        params_encoded = urlencode(params)
        async with AsyncClient() as cli:
            res = await cli.post(url + "audio_query?" + params_encoded)
        query_json = res.json()

        # 更新voicevox_query属性
        query_json["speedScale"] = custom_attributes["speed_scale"]
        query_json["volumeScale"] = custom_attributes["volume_scale"]
        query_json["intonationScale"] = custom_attributes["intonation_scale"]
        query_json["prePhonemeLength"] = custom_attributes["pre_phoneme_length"]
        query_json["postPhonemeLength"] = custom_attributes["post_phoneme_length"]

        # 发送语音合成请求并保存结果
        synthesis_params = {"speaker": speaker}
        params_encoded = urlencode(synthesis_params)
        async with AsyncClient() as cli:
            res = await cli.post(
                f"{url}synthesis?{params_encoded}", json=query_json, timeout=120
            )
        audio_data = res.content

        file_name = f"{voice_path}{uuid.uuid1()}.wav"

        if is_base64:
            audio_data = base64.b64decode(audio_data)

        file_path = await (anyio.Path(file_name)).resolve()
        await file_path.write_bytes(audio_data)
        local_url = file_path.as_uri()

        if text is not None:
            return {
                "voice": local_url,  # 语音url
                "text": f"[语音] {raw_text}",  # 文本
            }
        return {}

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)

        url = custom_config.get("api_url", "127.0.0.1:50021")

        if not url:  # 如果没有配置语音服务器url则返回错误信息
            raise Exception("未配置语音服务器url")
        if not url.startswith("http"):  # 如果不是http开头则添加
            url = f"http://{url}"
        if not url.endswith("/"):  # 如果不是/结尾则添加
            url = f"{url}/"

        # 从api获取可用角色json
        import requests

        err = None
        for _ in range(3):
            try:
                res = requests.get(url + "speakers", timeout=10)
                break
            except requests.exceptions.RequestException as e:
                err = e
                continue
        else:
            raise Exception("获取语音服务器角色列表失败") from err

        speaker_json = res.json()

        self.character_emotion_dict = {}

        # 遍历角色json，获取角色列表，保存到 character_emotion_dict 中
        for character in speaker_json:
            character_name = character["name"]
            styles = character["styles"]
            em_dict = {}
            for style in styles:
                em_dict[style["name"]] = {
                    "speaker": style["id"],
                    "name": style["name"],
                }
            self.character_emotion_dict[character_name] = em_dict

        print(f"[ext_VOICEVOX] 共加载了 {len(self.character_emotion_dict)} 个角色")
