<!-- markdownlint-disable MD028 -->

# 🧩 扩展指南

> [!TIP]
> 自定义扩展指的是本插件所提供的一个扩展接口，支持加载其它自定义脚本提供的功能，并且提供一套引导流程来 `教会` Bot 使用这个功能  
> 从而在 Bot 在与用户通过自然语言聊天时能够根据场景情况主动调用对应的扩展功能

> [!WARNING]
> 插件默认会在 Bot 根目录生成一个 `ext_cache` 文件夹用于存放扩展相关的临时文件  
> 该文件夹会在加载扩展的时候**删除其中的所有文件**  
> 请不要 修改本文件夹内的任何内容，造成数据丢失**后果自负**！

## 📖 使用指南

> [!WARNING]
> 你可以使用任意来源于本仓库 `/extensions/` 目录下的扩展，也可使用其它用户自行编写的扩展  
> 但是请注意**仅从你信任的来源获取**，否则可能包含**危险代码**！

### 1. 获取扩展

#### 指令安装 (仅支持 2.0.2 版本及以上)

使用 [添加扩展](commands.md#添加扩展) 指令安装即可

#### 手动安装 (适用于全版本)

1. 创建扩展模块存放目录 (启动一次插件即可自动创建)
2. 将你需要安装的扩展 (通常是 `ext_xxx.py`) 放入扩展模块存放目录 (默认路径为 `./data/naturel_gpt/extensions/`)

### 2. 进行扩展配置

在本插件的 [配置文件](configuation.md) 中正确填写以下内容

```yml
NG_EXT_LOAD_LIST:
  - ... # 其它扩展

  - # 扩展文件名，不含 .py
    EXT_NAME: ext_readLink

    # 是否启用扩展
    # 设为启用才会加载扩展，同时需要保证 NG_ENABLE_EXT 项开启
    IS_ACTIVE: true

    # 扩展配置 如该扩展插件无配置要求可不写此项
    EXT_CONFIG:
      # 填写示例 -> 参数名: 参数值 (注意缩进必须在EXT_CONFIG下一级)
      proxy: '127.0.0.1:7890'
```

### 3. 使用 [重新加载扩展](commands.md#重新加载扩展) 指令 或 重启 NoneBot 即可

## 👨‍💻 开发指南

> [!NOTE]
> 自行编写扩展需要具有一定的 Python 编程基础  
> 如果您有相关能力可直接参考本仓库 `/extensions/` 目录下的扩展进行编写(非常简单！)  
> 自行编写的扩展安装流程与上述相同
>
> **注意**：该功能尚处于早期阶段，扩展编写在未来版本有可能随时变化！

✨ 如果您想分享您自行开发的扩展，可向本仓库提交 pr，将您的扩展命名为 `ext_xxx.py`('xxx'部分可自行命名，请勿与已存在的扩展名冲突) 并上传至本仓库的 `/extensions/` 目录下  
欢迎您成为本项目的贡献者！

### 基本的扩展模块模板

```python
from .Extension import Extension

# 扩展的配置信息，用于 AI 理解扩展的功能
ext_config = {
    # 扩展名称，用于标识扩展，尽量简短
    "name": "ExtensionName",
    # 填写期望的参数类型，尽量使用简单类型，便于 AI 理解含义使用
    # 注意：实际接收到的参数类型为 str (由 AI 生成)，需要自行转换
    "arguments": {
        "arg1": "int",
        "arg2": "int",
    },
    # 扩展的描述信息，用于提示 AI 理解扩展的功能，尽量简短
    # 使用英文更节省 token，添加使用示例可提高 bot 调用的准确度
    "description": "send ... (use eg: /#Send&xxx#/)",
    # 参考词，用于上下文参考使用，为空则每次都会被参考 (消耗 token)
    "refer_word": ["use extension"],
    # 每次消息回复中最大调用次数，不填则默认为 99
    "max_call_times_per_msg": 99,
    # 作者信息
    "author": "",
    # 版本
    "version": "0.0.1",
    # 扩展简介
    "intro": "简介信息（查看扩展详情显示）",
    # 调用时是否打断响应 启用后将会在调用后截断后续响应内容
    "interrupt": True,
    # 可用会话类型 (`server` 即 MC服务器 | `chat` 即 QQ聊天)
    "available": ["server", "chat"],
}


class CustomExtension(Extension):
    def __init__(self, custom_config):
        super().__init__(ext_config.copy(), custom_config)

    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """当扩展被调用时执行的函数 *由扩展自行实现*

        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        config = self.get_custom_config()  # 获取yaml中的配置信息

        ### 在这里处理主要的自定义逻辑

        return {  # 返回的信息将会被发送到会话中
            "text": "[来自扩展的消息]...",  # 文字信息
            "image": "http://...",  # 图片url
            "voice": "http://...",  # 语音url
        }

```
