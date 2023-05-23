<!-- markdownlint-disable MD033 MD041 -->

# 🛠️ 安装与配置

## 📕 首次安装

1. 安装本插件并启用，详见 NoneBot 关于插件安装的说明
2. 加载插件并启动一次 NoneBot 服务
3. 查看自动生成的 `config/naturel_gpt_config.yml` ，并在 `OPENAI_API_KEYS` 下填入你的 API Key，在 `ADMIN_USERID` 下填写插件管理者的QQ号，在 `OPENAI_PROXY_SERVER` 下填写你的代理地址（有部分人的网络环境不填也可以直接使用代理，但最好填一下）
4. 在机器人所在的群组或者私聊窗口 `@TA` 或者 `提到 TA 当前的人格名` 即开始聊天
5. 使用命令 `rg / 人格设定 / 人格 / identity` 即可查看 bot 信息和相关指令
6. 启用后 bot 会开始监听所有消息并适时作出记录和回应，如果你不希望 bot 处理某条消息，请在消息前加上忽视符（默认为 `#` ，可在配置文件中修改）

## 🛠️ 配置说明

### 主配置

配置文件使用 YAML 格式，如果你不会甚至没了解过，请去 [这里（阮一峰）](https://www.ruanyifeng.com/blog/2016/07/yaml.html) 或者 [这里（菜鸟教程）](https://www.runoob.com/w3cnote/yaml-intro.html) 查看教程

插件的配置文件位于 `config/naturel_gpt_config.yml`  
请根据下面示例配置中的注释来编辑你的配置文件，**善用 Ctrl+F 全文搜索**

```yml
# OpenAI 的 API Key，以字符串列表方式填入
# 请自行替换为你的 Api_Key
OPENAI_API_KEYS:
  - 'sk-xxxxxxxxxxxxx'
  - 'sk-xxxxxxxxxxxxx'

# 请求 OpenAI 的超时时间，单位为秒
# 该选项修改不生效，原因未知
OPENAI_TIMEOUT: 60

# 消息响应节流时间（单位秒）
# 节流时间内有新消息只处理最后一条消息
REPLY_THROTTLE_TIME: 3.0

# 人格预设配置项
PRESETS:
  # 键名请和该预设的 preset_key 保持相同
  白羽:
    # 人格名
    preset_key: '白羽'

    # 初始状态是否锁定编辑
    is_locked: true

    # 是否为默认人格
    is_default: true

    # 此人格预设是否仅限私聊使用
    is_only_private: false

    # 人格的自我介绍，使用第三人称
    # Tip:
    # - 大多数请求都会携带人格信息，过长的人格信息，可能导致 token 消耗过多，从而额外占用上下文等信息的 token 使用量
    #   编写人设时可以尽量精简难以用文字呈现或者效果不明显的内容
    # - 同等信息量（通过翻译）下，英文文本的 token 消耗量仅为中文的 0.3 ~ 0.4 倍
    #   可以通过中英混合的方式编写人设以节省 token 消耗（例如用英文编写固定的人设信息，如年龄性别等）
    #   因为 GPT 实际上直接掌握了多种语言，即使在同一个句子中直接混合多种语言也是有效的表达（例如：You are 白羽, a digital life ...）
    # - 如果希望 bot 以特定的形式产生回复（例如“[动作][心情]语言”等），可以在人设中给出具体的示例
    # - token 计算工具：https://platform.openai.com/tokenizer
    bot_self_introl: '白羽是一名喜欢二次元的中二宅女，她机智、傲娇，对人类充满好奇，聊天时喜欢使用各种可爱的颜文字，如果冒犯到她会生气。'

# 忽略消息前缀
# 添加此前缀的聊天信息将被忽略
IGNORE_PREFIX: '#'

# 插件使用的语言模型
# 默认使用 GPT3.5 的模型（推荐）
CHAT_MODEL: gpt-3.5-turbo

# 聊天信息采样率
CHAT_TOP_P: 1

# 聊天生成温度
# 越高越随机
CHAT_TEMPERATURE: 0.4

# 回复主题重复惩罚
# 范围 -2 ~ 2，越高越倾向于产生新的话题
CHAT_PRESENCE_PENALTY: 0.4

# 回复内容复读惩罚
# 范围 -2 ~ 2，越高产生的回复内容越多样化
CHAT_FREQUENCY_PENALTY: 0.4

# 上下文聊天记录最大 token 数
CHAT_HISTORY_MAX_TOKENS: 2048

# 聊天记录总结最大 token 数
CHAT_MAX_SUMMARY_TOKENS: 512

# 生成回复的最大 token 数
REPLY_MAX_TOKENS: 1024

# 发起请求的最大 token 数（即 请求 + 回复）
REQ_MAX_TOKENS: 3072

# 在被 `提及` 时回复
# `提及` 即用户发言中含有当前 Bot 人格名
REPLY_ON_NAME_MENTION: true

# 在 `@Bot`（Bot 被 @）时回复
REPLY_ON_AT: true

# 在 `新成员加入` 时回复
REPLY_ON_WELCOME: true

# 用户聊天印象总结触发阈值
# 越小触发越频繁，推荐 10 - 20
USER_MEMORY_SUMMARY_THRESHOLD: 12

# 是否参考非 Bot 相关的上下文对话
# 开启后 Bot 回复会参考近几条非 Bot 相关信息
CHAT_ENABLE_RECORD_ORTHER: true

# 是否开启会话聊天记忆总结
# 开启后能够一定程度增强 Bot 对话记忆能力，但也会增加 token 消耗
CHAT_ENABLE_SUMMARY_CHAT: false

# 短期聊天记忆参考条数
CHAT_MEMORY_SHORT_LENGTH: 8

# 聊天记忆最大条数
# 超出此长度后会进行记忆总结并删除更早的记录
CHAT_MEMORY_MAX_LENGTH: 16

# 触发印象总结的对话间隔
CHAT_SUMMARY_INTERVAL: 10

# 是否使用 pickle（.pkl 文件）存储插件数据
NG_DATA_PICKLE: false

# 插件数据文件目录
NG_DATA_PATH: './data/naturel_gpt/'

# 扩展脚本文件目录（用于保存扩展脚本的路径）
NG_EXT_PATH: './data/naturel_gpt/extensions/'

# 插件日志保存目录
NG_LOG_PATH: './data/naturel_gpt/logs/'

# 管理员 QQ，以字符串列表方式填入
ADMIN_USERID:
  - '1145141919'
  - '9191415411'

# 黑名单 QQ，以字符串列表方式填入
# 黑名单中的用户消息不会被记录和响应
FORBIDDEN_USERS:
  - '1145141919'
  - '9191415411'

# 黑名单群号，以字符串列表方式填入
# Bot 不会响应黑名单群聊内的消息
FORBIDDEN_GROUPS:
  - '1145141919'
  - '9191415411'

# 自定义触发词，以字符串列表方式填入
# 消息中含有列表中的词将唤醒 Bot（触发回复）
WORD_FOR_WAKE_UP: []

# 自定义禁止触发词，以字符串列表方式填入
# 消息中含有列表中的词将拒绝唤醒 Bot（优先级高于触发词）
WORD_FOR_FORBIDDEN: []

# 随机触发聊天概率，设为 0 禁用
# 调整范围 0 ~ 1，设置过高回复频繁，会大量消耗 token
RANDOM_CHAT_PROBABILITY: 0.0

# 消息响应优先级
# 大于 1，数值越大优先级越低
NG_MSG_PRIORITY: 99

# 是否拦截其它插件的响应
# 开启后可能导致优先级低于本插件的其他插件不响应
NG_BLOCK_OTHERS: false

# 是否启用自定义扩展
# 开启后 Bot 可使用扩展功能，会额外消耗 token（取决于扩展描述，如未安装任何扩展务必关闭）
NG_ENABLE_EXT: true

# 响应命令是否需要 @Bot
NG_TO_ME: false

# 是否将 rg 相关指令返回结果通过图片输出
ENABLE_COMMAND_TO_IMG: true

# 是否将机器人回复通过图片输出
ENABLE_MSG_TO_IMG: false

# 是否开启主动记忆（需要同时启用记忆扩展）
# 开启后 Bot 会自行管理记忆
MEMORY_ACTIVE: true

# 主动记忆最大条数
MEMORY_MAX_LENGTH: 16

# 记忆强化阈值
# 范围 0 ~ 1，响应内容与记忆信息匹配达到阈值时会强化记忆
MEMORY_ENHANCE_THRESHOLD: 0.6

# 每条消息最大回复次数
# 限制 Bot 针对每条信息最大回复次数，避免封禁
NG_MAX_RESPONSE_PER_MSG: 5

# 是否允许消息分割发送
# 如果允许，Bot 有可能会在一次回复中发送多条消息
NG_ENABLE_MSG_SPLIT: true

# 是否允许自动唤醒其它人格
# 如果允许，Bot 在检测到未启用人格呼叫时会自动唤醒并切换人格
NG_ENABLE_AWAKE_IDENTITIES: true

# 请求 OpenAI 的代理服务器
# 填写示例 127.0.0.1:1234 或 username:password@127.0.0.1:1234
OPENAI_PROXY_SERVER: ''

# 是否解锁 AI 内容限制
# 可能导致 OpenAI 账号风险，请自行承担后果
# 可能需要人格简介引导才能起作用
UNLOCK_CONTENT_LIMIT: false

# 加载扩展列表
# 只有在此列表中的扩展会被 Bot 使用
NG_EXT_LOAD_LIST:
  - # 扩展文件名，不含 .py
    EXT_NAME: 'ext_random'

    # 是否启用该扩展
    IS_ACTIVE: false

    # 扩展配置
    EXT_CONFIG:
      arg: arg_value

# 是否优先使用群名片
# 如果关闭，Bot 将直接使用用户昵称
GROUP_CARD: true

# 是否检查用户名中的连字符
# 如果用户名中包含连字符，GPT 会将前半部分识别为名字，但一般情况下后半部分才是我们想被称呼的名字
# 例：策划-李华
NG_CHECK_USER_NAME_HYPHEN: false

# 是否启用连接 MC 服务器
ENABLE_MC_CONNECT: false

# MC 服务器人格指令前缀
MC_COMMAND_PREFIX:
  - '!'
  - '！'

# MC 服务器 RCON 地址
MC_RCON_HOST: 127.0.0.1

# MC 服务器 RCON 端口
MC_RCON_PORT: 25575

# MC服务器 RCON 密码
MC_RCON_PASSWORD: ''

# 配置文件版本信息，请勿手动更改
VERSION: '1.0'

# 日志等级
# 范围 0 ~ 4，0 为关闭，等级越高 Debug 日志越详细
DEBUG_LEVEL: 0
```

### `.env` 配置

所有配置项均为可选，一般情况下不需要填写

```properties
# 插件配置文件路径
NG_CONFIG_PATH=config/naturel_gpt_config.yml

# 是否启用开发模式（强制使用默认配置项）
NG_DEV_MODE=False
```
