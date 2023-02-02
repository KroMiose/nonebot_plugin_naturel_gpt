<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="./image/README/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="./image/README/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">
    ✨ 更人性化(拟人)的GPT聊天Ai插件! ✨<br/>
    🧬 支持多个人格自定义 / 切换 | 尽情发挥你的想象力吧！ ⚙️<br/>
    <a href="./LICENSE">
        <img src="https://img.shields.io/badge/license-Apache 2.0-6cg.svg" alt="license">
    </a>
    <a href="https://pypi.python.org/pypi/nonebot-plugin-learning-chat">
        <img src="https://img.shields.io/pypi/v/nonebot-plugin-learning-chat.svg" alt="pypi">
    </a>
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
</div>

## 💡功能列表

* [X] 自动切换api_key: 支持同时使用多个openai_api_key，失效时自动切换
* [X] 自定义人格预设: 可自定义的人格预设，打造属于你的个性化的TA
* [X] 聊天基本上下文关联: 群聊场景短期记忆上下文关联，尽力避免聊天出戏
* [X] 聊天记录总结记忆: 自动总结聊天记忆，具有一定程度的长期记忆能力
* [X] 用户印象记忆: 每个人格对每个用户单独记忆印象，让TA能够记住你
* [X] 人格切换: 可随时切换不同人格
* [X] 数据持久化存储: 保存用户对话信息（使用pickle）
* [X] 新增/编辑人格: 使用指令进行人格预设的编辑
* [ ] 潜在人格唤醒机制: 一定条件下，潜在人格会被主动唤醒
* [ ] 主动聊天参与逻辑: 尽力模仿人类的聊天参与逻辑，目标是让TA能够真正融入你的群组

## 📕使用方式

1. 安装本插件并启用，详见NoneBot关于插件安装的说明
2. 加载插件并启动一次NoneBot服务
3. 查看自动生成的 `config/naturel_gpt.config.yml` ，并填入你的OpenAi_Api_key
4. 在机器人所在的群组或者私聊窗口@TA或者 `提到`TA当前的 `人格名` 即开始聊天
5. 使用命令 `rg / 人格设定 / 人格 / identity` 即可查看bot信息和相关指令
6. 启用后bot会开始监听所有消息并适时作出记录和回应，如果你不希望bot处理某条消息，请在消息前加上忽视符（默认为 `#` ，可在配置文件中修改）

## 🛠️参数说明 — `config/naturel_gpt.config.yml`

| 参数名                        | 类型  | 释义                                       |
| ----------------------------- | ----- | ------------------------------------------ |
| OPENAI_API_KEYS               | array | OpenAi的 `Api_Key，以字符串数组方式填入    |
| CHAT_HISTORY_MAX_TOKENS       | int   | 聊天记录最大token数                        |
| CHAT_MAX_SUMMARY_TOKENS       | int   | 聊天记录总结最大token数                    |
| CHAT_MEMORY_MAX_LENGTH        | int   | 聊天记忆最大条数                           |
| CHAT_MEMORY_SHORT_LENGTH      | int   | 短期聊天记忆参考条数                       |
| CHAT_MODEL                    | str   | 聊天生成的语言模型                         |
| CHAT_FREQUENCY_PENALTY        | float | 聊天频率重复惩罚                           |
| CHAT_PRESENCE_PENALTY         | float | 聊天主题重复惩罚                           |
| CHAT_TEMPERATURE              | float | 聊天生成温度: 越高越随机                   |
| CHAT_TOP_P                    | float | 聊天信息采样率                             |
| IGNORE_PREFIX                 | str   | 忽略前置修饰：添加此修饰的聊天信息将被忽略 |
| REPLY_MAX_TOKENS              | int   | 生成回复的最大token数                      |
| REQ_MAX_TOKENS                | int   | 发起请求的最大token数                      |
| USER_MEMORY_SUMMARY_THRESHOLD | int   | 用户聊天印象总结触发阈值                   |
| REPLY_ON_AT                   | bool  | 在被 `@TA` 时回复                        |
| REPLY_ON_NAME_MENTION         | bool  | 在被 `提及` 时回复                       |
| PRESETS                       | dict  | 人格预设集合                               |
| NG_DATA_PATH                  | str   | 数据文件目录                               |
| ADMIN_USERID                  | array | 管理员id，以字符串数组方式填入             |
| \_\_DEBUG\_\_                 | bool  | 是否开启DEBUG输出                          |

## 🎢更新日志

### [2023/2/2] v1.1.0

- 新增了预设编辑功能
- 新增自定义管理员id功能，管理员可以删除预设 / 修改锁定的预设
- 增加debug开关控制生成文本时的控制台输出（默认关闭）

### [2023/2/2] v1.1.1

- 修复查询人格错误的问题
