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
    <a href="https://pypi.python.org/pypi/nonebot-plugin-naturel-gpt">
        <img src="https://img.shields.io/pypi/v/nonebot-plugin-naturel-gpt.svg" alt="pypi">
    </a>
    <img src="https://img.shields.io/badge/python-3.8+-6a9.svg" alt="python">
    <a href="https://jq.qq.com/?_wv=1027&k=71t9iCT7">
        <img src="https://img.shields.io/badge/加入交流群-636925153-c42.svg" alt="python">
    </a>
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

| 参数名                        | 类型  | 释义                                       | 默认值              | 编辑建议                                   |
| ----------------------------- | ----- | ------------------------------------------ | ------------------- | ------------------------------------------ |
| OPENAI_API_KEYS               | array | OpenAi的 `Api_Key，以字符串数组方式填入    | ['']                |                                            |
| CHAT_HISTORY_MAX_TOKENS       | int   | 聊天记录最大token数                        | 2048                |                                            |
| CHAT_MAX_SUMMARY_TOKENS       | int   | 聊天记录总结最大token数                    | 512                 |                                            |
| CHAT_MEMORY_MAX_LENGTH        | int   | 聊天记忆最大条数                           | 12                  | 超出此长度后会进行记忆总结并删除更早的记录 |
| CHAT_MEMORY_SHORT_LENGTH      | int   | 短期聊天记忆参考条数                       | 8                   |                                            |
| CHAT_MODEL                    | str   | 聊天生成的语言模型                         | text-davinci-003    |                                            |
| CHAT_FREQUENCY_PENALTY        | float | 聊天频率重复惩罚                           | 0.4                 |                                            |
| CHAT_PRESENCE_PENALTY         | float | 聊天主题重复惩罚                           | 0.6                 |                                            |
| CHAT_TEMPERATURE              | float | 聊天生成温度: 越高越随机                   | 0.6                 |                                            |
| CHAT_TOP_P                    | float | 聊天信息采样率                             | 1                   |                                            |
| IGNORE_PREFIX                 | str   | 忽略前置修饰：添加此修饰的聊天信息将被忽略 | #                   |                                            |
| REPLY_MAX_TOKENS              | int   | 生成回复的最大token数                      | 1024                |                                            |
| REQ_MAX_TOKENS                | int   | 发起请求的最大token数（即请求+回复）       | 2048                |                                            |
| USER_MEMORY_SUMMARY_THRESHOLD | int   | 用户聊天印象总结触发阈值                   | 12                  | 越小触发越频繁，推荐10-20                  |
| REPLY_ON_AT                   | bool  | 在被 `@TA` 时回复                        | True                |                                            |
| REPLY_ON_NAME_MENTION         | bool  | 在被 `提及` 时回复                       | True                | `提及` 即用户发言中含有当前bot人格名     |
| PRESETS                       | dict  | 人格预设集合                               |                     | 默认有四个预设，详见生成的配置文件         |
| NG_DATA_PATH                  | str   | 数据文件目录                               | ./data/naturel_gpt/ | 保存实现数据持久化                         |
| ADMIN_USERID                  | array | 管理员id，以字符串数组方式填入             | ['']                | 只有管理员可删除预设                       |
| \_\_DEBUG\_\_                 | bool  | 是否开启DEBUG输出                          | False               | 开启可查看prompt模板输出                   |

## 🤖行为逻辑QA

Q: 如何区分会话？

A: 根据群组(群聊场景)、私聊(个人)区分会话，即同一群组内共享一个会话，私聊窗口独占一个会话；不同人格的会话和记忆完全独立

---

Q: TA是如何产生回复的？

A: TA会根据 对话上下文(即最近几条聊天记录 不论是否与TA相关)、过往记忆(过去聊天记录的总结)、发起 `@`或 `提及`的用户印象(根据与该用户的聊天记录总结) 生成prompt模板，然后通过 OpenAi 的接口产生对应的回复发送，并且把产生的回复再填加入相应的聊天记录中

---

Q: TA如何记忆用户印象？

A: TA根据用户的id(通常是qq号)的 对TA发起 `@`或 `提及`的聊天记录、响应和历史印象 自动总结产生bot对每个用户的印象，该印象记录与会话无关(即多个会话共享)，但各个人格之间信息相互独立

---

Q: 如何实现记录持久化保存？

A: 由于本项目的记忆保存与人格预设存在一定耦合，故使用了pickle直接对程序中使用的数据信息进行序列化后保存为本地文件，然后在程序启动的时候使用pickle加载，这样做的好处是代码实现简便，但由于运行过程数据信息几乎都保存在内存中，如果您的bot活跃用户过多(>1k)、或者人格预设过多(>100)，可能会造成一定的性能负担，敬请见谅！

---

Q: 为什么我在编辑了配置文件中的人格预设信息后重载插件，编辑没有生效？

A: 由于用户数据信息与人格预设信息高度绑定，如果已经生成过pickle文件后程序不会再响应配置文件中人格预设的修改，而是会直接读取已有的pickle文件中的信息，您可以尝试使用 `!rg` 指令根据响应提示直接进行编辑，或者直接删除数据目录中的 `.pkl` 文件(注意：会造成bot记忆丢失)后重载程序重新生成

## 🎢更新日志

### [2023/2/5] v1.1.2

- 新增了人格预设的 锁定/解锁 功能，锁定后非管理员无法编辑该预设
- 更新README文档
- 优化rg命令显示格式
- 微调了 `config.py` 中的一些默认参数
- 修复本插件拦截其它插件响应的问题，降低了本插件的响应优先级
- 更新了交流群信息(见本文档开头)，欢迎各路大佬加入互相学习、一同探讨更新方向、分享更多玩法等

### [2023/2/2] v1.1.1

- 修复查询人格错误的问题

### [2023/2/2] v1.1.0

- 注意：v1.1.0以前的版本更新到此版本或以上需要删除原bot记忆文件重新生成(即./data/naturel_gpt文件夹)
- 新增了预设编辑功能
- 新增自定义管理员id功能，管理员可以删除预设 / 修改锁定的预设
- 增加debug开关控制生成文本时的控制台输出（默认关闭）
