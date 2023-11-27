<!-- markdownlint-disable MD024 MD031 MD033 MD036 -->

# 📋 扩展列表

> [!TIP]
> 点击扩展标题即可直接跳转到 GitHub
>
> 标题以 `[MC]` 开头的扩展仅限 Minecraft 服务器使用
>
> 配置项注释中标明 `[必填]` 的为必填项，其它皆为可选

## [随机数生成器](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_random.py)

> 仅供开发者了解扩展的运行机制，不建议日常开启

### 简介 <!-- {docsify-ignore} -->

一个示例扩展，用于引导 bot 调用并生成随机数

<hr />

## [Stable Diffusion 绘画扩展](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_stablediffusion.py)

### 简介 <!-- {docsify-ignore} -->

调用任意 Stable Diffusion 后端生成图片并发送

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# SD 后端 API 地址
sd_base_api: http://127.0.0.1:7860

# 生成图片时使用的对话模型
chat_model: gpt-3.5-turbo
```

<hr />

## [发送随机二次元图片 (ixiaowai)](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_random_pic.py)

!> 请勿与其它发图拓展一并启用

### 简介 <!-- {docsify-ignore} -->

调用 `api.ixiaowai.cn` 的接口获取一张二次元图片并发送

<hr />

## [发送指定二次元图片 (Lolicon API)](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_lolicon_pic.py)

!> 请勿与其它发图拓展一并启用

### 简介 <!-- {docsify-ignore} -->

作者：[CCYellowStar](https://github.com/CCYellowStar)

调用 [Lolicon API](https://api.lolicon.app/) 接口按指定 tag 获取一张二次元图片并发送

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# R18 图片获取设置
# 0 为不获取，1 为获取，2 为混合获取
r18: 0

# 请求 API 使用的代理
proxy: null
```

<hr />

## [发送指定二次元图片 (NyanCat 色图 API)](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_sexnyan_pic.py)

!> 请勿与其它发图拓展一并启用

### 简介 <!-- {docsify-ignore} -->

调用 [NyanCat 色图 API](https://sex.nyan.xyz/) 接口按指定关键字获取一张二次元图片并发送

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# 是否允许 R18 图片
r18: false
```

<hr />

## [更人性化的 Lolicon API 色图扩展](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_lolicon_search.py)

### 简介 <!-- {docsify-ignore} -->

作者：[student_2333](https://github.com/lgc2333)

此扩展与其它扩展不同的地方在于 Bot 可以知道他发送出去了什么图片，或者在发图的过程中遇到了什么错误

当开启回复转图时，可选让 Bot 在其回复图展示图片，~~有一定程度防止封号与风控~~

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# R18 图片获取设置
# 0 为不获取，1 为获取，2 为混合获取
r18: 0

# 是否在结果中排除 AI 图
exclude_ai: false

# 是否将图片的 Tag 提供给 Bot
# 禁用此项可能有助于提高 Bot 的发图意愿
provide_tags: true

# 是否直接使用扩展发送图片，而不是将图片地址传给 Bot 让其发送
# 适用于 Bot 死活不在回复中发图的情况
# 如果未开启回复转图，则此项保持开启
send_manually: false

# 请求 API 使用的代理
proxy: null

# 图片反代地址，非必要不需要修改
pic_proxy: null
```

<hr />

## [发送表情包](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_emoticon.py)

### 简介 <!-- {docsify-ignore} -->

调用 [ALAPI](https://www.alapi.cn/) 接口，搜索指定关键字 (由 Bot 自主决定) 的表情包并发送

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# [必填] 平台 token (需自行申请)
token: ''
```

<hr />

## [发送语音消息 - 极客版](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_voice.py)

### 简介 <!-- {docsify-ignore} -->

调用语音生成接口实现语音回复 (需自行准备语音合成 api 接口)

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# 是否启用腾讯翻译
ng_voice_translate_on: false

# 腾讯翻译 地区
tencentcloud_common_region: ap-shanghai

# 腾讯翻译 Secret ID
tencentcloud_common_secretid: ''

# 腾讯翻译 Secret Key
tencentcloud_common_secretkey: ''

# 翻译目标语言
g_voice_tar: ja

# 是否使用 base64 解码返回音频
is_base64: false
```

<hr />

## [发送语音消息 - VOX 版](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_voice.py)

### 简介 <!-- {docsify-ignore} -->

调用语音生成接口实现语音回复 (需自行准备语音合成 api 接口)

### [VOX](https://voicevox.hiroshiba.jp/) 部署指南 <!-- {docsify-ignore} -->

#### Windows <!-- {docsify-ignore} -->

从 [这里](https://voicevox.hiroshiba.jp/) 下载安装包直接安装打开即可使用

#### Linux (Docker) <!-- {docsify-ignore} -->

1. 拉取镜像

   ```bash
   docker pull voicevox/voicevox_engine:cpu-ubuntu20.04-latest
   ```

2. 运行镜像 (二选一执行)

   ```bash
   # 前台运行
   docker run --rm -it -p '50021:50021' voicevox/voicevox_engine:cpu-ubuntu20.04-latest

   # 后台运行
   docker run --rm -d -it -p '50021:50021' voicevox/voicevox_engine:cpu-ubuntu20.04-latest
   ```

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# 是否启用腾讯翻译
ng_voice_translate_on: false

# 腾讯翻译 地区
tencentcloud_common_region: ap-shanghai

# 腾讯翻译 Secret ID
tencentcloud_common_secretid: ''

# 腾讯翻译 Secret Key
tencentcloud_common_secretkey: ''

# 翻译目标语言
g_voice_tar: ja

# 是否使用 base64 解码返回音频
is_base64: false

# 语音角色
character: もち子さん

# 搭建 VOX 的服务器地址
api_url: 127.0.0.1:50021
```

<hr />

## [发送邮件](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_email.py)

### 简介 <!-- {docsify-ignore} -->

向指定邮箱地址发送邮件

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# [必填] 邮箱 SMTP 授权码
SMTP_CODE: ''

# [必填] 邮箱地址
SENDER_ADDR: ''

# SMTP 连接地址，默认 163 邮箱
SMTP_ADDR: 'smtp.163.com'

# SMTP 连接端口，没有特殊需求不要填写
SMTP_PORT: null

# SMTP 是否使用 TLS 连接，没有特殊需求不要填写
SMTP_USE_TLS: true
```

<hr />

## [谷歌搜索扩展模块](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_google_search.py)

!> 请勿与其它搜索拓展一并启用

### 简介 <!-- {docsify-ignore} -->

赋予 bot 使用谷歌搜索的能力

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# [必填] 谷歌搜索 api_key
# 申请地址：https://developers.google.com/custom-search/v1/introduction?hl=zh-cn
apiKey: ''

# [必填] 谷歌搜索 cx_key
# 申请地址：https://programmablesearchengine.google.com/controlpanel/all
cxKey: ''

# 代理服务器地址
proxy: null

# 搜索保留最大结果条数
max_results: 3
```

<hr />

## [主动搜索扩展模块](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_search.py)

!> 请勿与其它搜索拓展一并启用

### 简介 <!-- {docsify-ignore} -->

赋予 bot 主动获取互联网新信息的能力，实现类似 New Bing 的交互体验

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# 你的代理，不填国内无法访问
proxy: null

# 搜索保留最大结果条数
max_results: 3
```

<hr />

## [阅读链接内容扩展模块](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_readLink.py)

### 简介 <!-- {docsify-ignore} -->

赋予 bot 阅读链接内容的能力，貌似只能读取那种类似知乎的文字比较多的专栏类网址

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# 你的代理，不填国内无法访问
# 示例： 127.0.0.1:7890
proxy: null
```

<hr />

## [定时器模块](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_timer.py)

### 简介 <!-- {docsify-ignore} -->

赋予 bot 预定时间的能力，到时自动推送消息

<hr />

## [绘图模块](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_paint.py)

### 简介 <!-- {docsify-ignore} -->

作者：[OREOREO](https://github.com/OREOREO)

调用 OpenAI 绘图接口，实现自然语言调用绘画，接口共用本插件的 Api Key

<hr />

## [进化模块](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_evolution.py)

### 简介 <!-- {docsify-ignore} -->

赋予 bot 自主发展人格的能力，允许 bot 自主设定更新人设

!> bot 更新人格后会丢失原人格预设，如需保留请自行备份

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# 触发更新时通知类型
# - 0: 无通知
# - 1: 仅触发提示
# - 2: 新预设完整通知
notify_type: 1
```

<hr />

## [\[MC\] 执行服务器命令模块](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_mc_command.py)

### 简介 <!-- {docsify-ignore} -->

赋予 bot 执行 Minecraft 服务器命令的能力

鉴权基于字符串匹配，请谨慎使用过滤高危命令，黑白名单匹配的内容包括指令前缀 `/`

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# 匹配指令内容白名单列表
# 列表中至少一个字符串应被包含在命令中，为空则不限制
match_white_list: []

# 匹配指令内容黑名单列表
# 列表中所有字符串都不应被包含在命令中，为空则不限制，优先级高于白名单
match_black_list: []
```

<hr />

## [AI 作曲模块](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_makemidi.py)

### 简介 <!-- {docsify-ignore} -->

作者：[CCYellowStar](https://github.com/CCYellowStar)

借鉴~~抄袭~~ [nonebot_plugin_makemidi](https://github.com/RandomEnch/nonebot_plugin_makemidi) 插件让 ai 输入 midi 来生成 midi 音乐

### 扩展安装指南 <!-- {docsify-ignore} -->

请根据下方步骤安装你的扩展

1. 安装前置插件  
   在你的 NoneBot 环境中输入下方命令即可
   ```bash
   pip install nonebot_plugin_makemidi
   ```
2. 安装 fluidsynth  
   从 [这里](https://wwpr.lanzout.com/i1jLO0xgpi3g) 下载 fluidsynth 后解压到合适位置，将其 bin 文件夹的路径 [添加到环境变量](<https://learn.microsoft.com/zh-cn/previous-versions/office/developer/sharepoint-2010/ee537574(v=office.14)#%E5%B0%86%E8%B7%AF%E5%BE%84%E6%B7%BB%E5%8A%A0%E5%88%B0-path-%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F>) 中  
    为使 GoCQ 能发送语音，你还需要安装 ffmpeg（[下载地址](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z)），方法与 fluidsynth 相似（如果你能发语音就是已经安装了 ffmpeg）
3. 下载音源文件  
   从 [这里](https://wwpr.lanzout.com/iIpwl0xgpr5c) 下载 `gm.zip` 后解压，将里面的 `gm.sf2` 放到 NoneBot 工作目录的 `resources` 目录下

<hr />

## [启用回复转图后直接发送文本消息模块](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/extensions/ext_makemidi.py)

### 简介 <!-- {docsify-ignore} -->

_标题好长不要介意_

让回复转图的 Bot 拥有直接发送文本消息的能力

### 配置 <!-- {docsify-ignore} -->

请根据下方示例配置中的注释来编辑你的扩展配置

```yml
# 关键词黑名单，列表内包括的关键词 Bot 都无法通过本扩展发送
black_words: []
```

<hr />

## [已归档扩展（不推荐使用 / 已失效）](archived_extensions.md)
