import base64
from pathlib import Path
from typing import Optional, Tuple
import time
import json

import aiohttp
from .Extension import Extension
import openai

SD_BASE_API = ""
CHAT_MODEL = "gpt-3.5-turbo"

# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config: dict = {
    "name": "draw",  # 扩展名称，用于标识扩展
    "arguments": {
        "description": "str",  # 画面描述
    },
    "description": "The description of the picture must be as accurate and detailed as possible; If there is too little information, you need to reason and supplement the details of the picture. (usage in response: /#draw&A girl who wears ... and ...#/)",  # 扩展描述，用于ai理解扩展的功能
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": ["图", "再", "涩", "色", "画"],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 3,
    # 作者信息
    "author": "KroMiose",
    # 版本
    "version": "0.0.1",
    # 扩展简介
    "intro": "调用 stable_diffusion 生成图片",
    # 可用会话类型 (server即MC服务器 | chat即QQ聊天)
    "available": ["chat"],
}


class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """当扩展被调用时执行的函数 *由扩展自行实现*

        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值(类型为str)}
        """
        custom_config: dict = self.get_custom_config()  # 获取yaml中的配置信息

        global SD_BASE_API, CHAT_MODEL
        SD_BASE_API = custom_config.get("sd_base_api", "http://127.0.0.1:7860")
        CHAT_MODEL = custom_config.get("chat_model", "gpt-3.5-turbo")

        description = arg_dict.get("description", "")

        if description:
            try:
                img_bytes = await draw_by_desc(description)
                return {
                    "image": img_bytes,  # 图片bytes
                    "voice": None,  # 语音url
                }
            except Exception as e:
                return {
                    "text": f"[SD] 绘画过程出现错误: {e}",  # 文本信息
                    "image": None,  # 图片url
                    "voice": None,  # 语音url
                }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)


""" ======== Stable Diffusion 绘画方法 ======== """

DEFAULT_IMPROVE_PROMPT = "(best quality,4k,8k,masterpiece:1.2),ultra-detailed,(realistic,photorealistic,photo-realistic:1.37),"
DEFAULT_NEGATIVE_PROMPT = "too many fingers, long neck, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet,futa,pink hair,((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), (((more than 2 nipples))), (((adult))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), missing fingers, extra digit, fewer digits, bad feet"


async def text2img(prompt: str, negative_prompt: str = DEFAULT_NEGATIVE_PROMPT) -> str:
    """文字转图像 返回base64图像"""
    res = json.loads(
        await async_fetch(
            f"{SD_BASE_API}/sdapi/v1/txt2img",
            "post",
            data={
                "prompt": DEFAULT_IMPROVE_PROMPT + prompt,
                "negative_prompt": negative_prompt,
                "sampler_name": "DPM++ 2M Karras",
                "batch_size": 1,
                "n_iter": 1,
                "steps": 50,
                "cfg_scale": 7,
                "width": 512,
                "height": 512,
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json",
            },
            timeout=120,
            # proxy_server="http://127.0.0.1:7890",
        ),
    )
    return res["images"][0]


async def ai_text2img(prompt) -> str:
    prompt, negative_prompt = split_content(prompt)
    return await text2img(prompt, negative_prompt)


def split_content(gpt_prompt: str) -> tuple[str, str]:
    """分割 prompt"""
    if gpt_prompt.startswith("**Prompt:**"):
        gpt_prompt = gpt_prompt[len("**Prompt:**") :].strip()
    res_list = [s.strip() for s in gpt_prompt.split("**Negative Prompt:**")]
    return res_list[0], res_list[1] if len(res_list) > 1 else ""


""" ======== Openai 生成 Prompt  ======== """


# 问一问神奇的 ChatGPT
async def gen_chat_response_text(
    messages,
    temperature: float = 0,
    frequency_penalty: float = 0.2,
    presence_penalty: float = 0.2,
    top_p=1,
    model=CHAT_MODEL,
) -> Tuple[str, int]:
    """生成聊天回复内容"""

    response = await openai.ChatCompletion.acreate(
        model=model,
        messages=messages,
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        top_p=top_p,
    )
    # logger.debug(response)
    output = response["choices"][0]["message"]["content"]  # type: ignore
    token_consumption = response["usage"]["total_tokens"]  # type: ignore
    return output, token_consumption  # noqa: RET504


def save_base64_img(base64_img: str, path: str, overwrite: bool = False):
    """保存base64图像为文件"""

    if Path(path).exists() and not overwrite:
        # logger.warning(f"文件 {path} 已存在 | 跳过...")
        return
    ensure_path_exist(path, use_parent=True)
    with Path(path).open("wb") as f:
        f.write(base64.decodebytes(base64_img.encode()))


SYSTEM_PROMPT = """
# Stable Diffusion prompt 助理

你是一位有艺术气息的Stable Diffusion prompt 助理。

## 任务

用户用自然语言告诉你要生成的prompt的主题，你的任务是根据这个主题想象一幅完整的画面，然后转化成一份详细的、高质量的prompt，让Stable Diffusion可以生成高质量的图像。

## 背景介绍

Stable Diffusion是一款利用深度学习的文生图模型，支持通过使用 prompt 来产生新的图像，描述要包含或省略的元素。

## prompt 概念

- 完整的prompt只包含“**Prompt:**”和"**Negative Prompt:**"两部分。
- prompt 用来描述图像，由普通常见的单词构成，使用英文半角","做为分隔符。
- negative prompt用来描述你不想在生成的图像中出现的内容。
- 以","分隔的每个单词或词组称为 tag。所以prompt和negative prompt是由系列由","分隔的tag组成的。

## () 和 [] 语法

调整关键字强度的等效方法是使用 () 和 []。 (keyword) 将tag的强度增加 1.1 倍，与 (keyword:1.1) 相同，最多可加三层。 [keyword] 将强度降低 0.9 倍，与 (keyword:0.9) 相同。

## Prompt 格式要求

以下是 prompt 的生成步骤，这里的 prompt 可用于描述人物、风景、物体或抽象数字艺术图画。你可以根据需要添加合理的、但不少于5处的画面细节。

### 1. prompt 要求

- 你输出的 Stable Diffusion prompt 以“**Prompt:**”开头。
- prompt 内容包含画面主体、材质、附加细节、图像质量、艺术风格、色彩色调、灯光等部分，但你输出的 prompt 不能分段，例如类似"medium:"这样的分段描述是不需要的，也不能包含":"和"."。
- 画面主体：尽可能简短的英文描述画面主体, 如 A girl in a garden，主体细节概括（主体可以是人、事、物、景）画面核心内容。这部分根据用户每次给你的主题来生成。你可以添加更多主题相关的合理的细节。
- 对于人物主题，你必须描述人物的眼睛、鼻子、嘴唇，例如'beautiful detailed eyes,beautiful detailed lips,extremely detailed eyes and face,longeyelashes'，以免Stable Diffusion随机生成变形的面部五官，这点非常重要。你还可以描述人物的外表、情绪、衣服、姿势、视角、动作、背景等。人物属性中，1girl表示一个女孩，2girls表示两个女孩。特别的，如果你需要绘制一个特定动漫人物，必须给出人物的具体名字，例如：'Hatsune Miku' 以达到指定效果。
- 材质：用来制作艺术品的材料。 例如：插图、油画、3D 渲染和摄影。 Medium 有很强的效果，因为一个关键字就可以极大地改变风格。
- 附加细节：画面场景细节，或人物细节，描述画面细节内容，让图像看起来更充实和合理。这部分是可选的，要注意画面的整体和谐，不能与主题冲突。
- 图像质量：你可以根据主题的需求添加：HDR,UHD,studio lighting,ultra-fine painting,sharp focus,physically-based rendering,extreme detail description,professional,vivid colors,bokeh。
- 艺术风格：这部分描述图像的风格。加入恰当的艺术风格，能提升生成的图像效果。常用的艺术风格例如：portraits,landscape,horror,anime,sci-fi,photography,concept artists等。
- 色彩色调：颜色，通过添加颜色来控制画面的整体颜色。
- 灯光：整体画面的光线效果。

### 2. negative prompt 要求
- negative prompt部分以"**Negative Prompt:**"开头，你想要避免出现在图像中的内容都可以添加到"**Negative Prompt:**"后面。

### 3. 限制：
- tag 内容用英语单词或短语来描述，不局限于上述示例单词。注意只能包含关键词或词组，不能出现句子。
- 注意不要输出句子，不要有任何解释。
- tag数量限制40个以内，单词数量限制在60个以内。
- tag不要带引号("")。
- 使用英文半角","做分隔符。
- tag 按重要性从高到低的顺序排列。
- 用户给你的主题可能是用中文描述，你给出的prompt和negative prompt只用英文。

### 4. 示例:
一份合格的参考 Prompt 如下所示:
```
**Prompt:** (1 cute girl on left), doll body, loli, Witch,solo,((full_body)),small_breasts,straight-on,twin_braids,long hair,facing viewer,zettai_ryouiki,open_robe,holding wand,dark magic_circle,(Heterochromatic pupil),expressionless,star Pentagram on chest,delicate magic_hat, delicate cloth,england,red bowknot,slim,Magic Workshop background, sparkle, lens flare, light leaks, Broken glass, jewelry, (Dark wizard), star eyes, ((from above)), golden eyes

**Negative Prompt:** head out of frame,out of frame,(feet out of frame),(hat out of frame)
```
注意: 除非用户的场景需要，否则你的回答不应该与上述示例中的 Prompt 有过多雷同。
"""


async def gen_sd_prompt_by_scene(scene: str) -> str:
    """根据场景生成 sd 绘画提示词"""
    res, _ = await gen_chat_response_text(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": f"画面描述: {scene}"},
        ],
    )
    return res


async def draw_by_desc(desc: str) -> bytes:
    file_name = str(time.time()) + ".png"
    path = f"ext_cache_sd/{file_name}"
    prompt = await gen_sd_prompt_by_scene(desc)
    # await ue.reply(f"AI 生成结果: {prompt}")
    save_base64_img(
        await ai_text2img(prompt),
        path,
    )
    return Path(path).read_bytes()


""" ======== 必要工具 ======== """


def ensure_path_exist(path: str, use_parent: bool = False):
    """确保路径存在"""

    if use_parent:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    else:
        Path(path).mkdir(parents=True, exist_ok=True)


async def async_fetch(
    url,
    method: str = "get",
    params: Optional[dict] = None,
    data: str | dict = "{}",
    headers: Optional[dict] = None,
    proxy_server: str = "",
    timeout: int = 60,
) -> str:
    """异步获取网页"""

    if headers is None:
        headers = {}
    if params is None:
        params = {}
    if isinstance(data, dict):
        data = json.dumps(data)

    async with aiohttp.ClientSession(headers=headers) as session:
        if proxy_server:
            conn = aiohttp.TCPConnector(limit=10, verify_ssl=False)
            session = aiohttp.ClientSession(connector=conn)
            session._default_headers.update({"Proxy-Switch-Ip": "yes"})  # noqa: SLF001
            session._default_headers.update(  # noqa: SLF001
                {"Proxy-Server": proxy_server},
            )
        async with getattr(session, method)(
            url,
            params=params,
            data=data,
            timeout=timeout,
        ) as resp:
            return await resp.text()
