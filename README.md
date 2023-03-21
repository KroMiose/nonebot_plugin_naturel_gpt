<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="./image/README/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="./image/README/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">
    ✨ 更人性化(拟人)的GPT聊天Ai插件! ✨<br/>
    🧬 支持多个人格自定义 / 切换 | 尽情发挥你的想象力吧！ ⚙️<br/>
    🧬 <a href="https://docs.google.com/spreadsheets/d/1JQNmVH-vlDn2uEPwkjv3iN-zn0PHpQ7RGbgA5T3fxOA/edit?usp=sharing">预设收集共享表(欢迎分享各种自定义人设)</a> 🧬 <br/>
    🎆 如果喜欢请点个⭐吧！您的支持就是我持续更新的动力 🎉<br/>
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
    <h2>🎉 [2023/3/16] 项目重构 🎉</h2>
    <p>项目重构整理基本完成，敬请期待重构后更多功能性更新<br/>
    感谢<a href="https://github.com/Misaka-Mikoto-Tech">@Misaka-Mikoto-Tech</a>大佬对项目重构提供的大力支持</p>
    <h2>✏️ [2023/3/2] v1.4 更新: 支持ChatGPT模型 ✏️</h2>
    <p>本次更新后插件开始支持官方ChatGPT模型接口，token定价仅为GPT3的 1/10, 回复质量更高 响应速度更快</p>
    <h2>🧩 [2023/2/18] v1.3 更新: 自定义扩展支持 🧩</h2>
    <p>本次更新后插件开始支持自定义扩展，您可以直接通过自然语言直接调用多种扩展功能，包括 文本/图片/语音/邮件...</p>
    <p>提供了一些<a href="#%E5%AE%98%E6%96%B9%E6%8B%93%E5%B1%95%E5%88%97%E8%A1%A8">样例扩展(点击前往)</a>，支持仅使用少量的代码就能实现各种自定义功能</p>
    <p>!  <strong><a href="#%E6%8B%93%E5%B1%95%E5%88%97%E8%A1%A8"> 点击前往 -> 扩展列表 </a></strong> !</p>
</div>

## 💡 功能列表

> 以下未勾选功能仅表示未来可能开发的方向，不代表实际规划进度，具体开发事项可能随时变动
> 勾选: 已实现功能；未勾选: 正在开发 / 计划开发 / 待定设计

* [X] 自动切换api_key: 支持同时使用多个openai_api_key，失效时自动切换
* [X] 自定义人格预设: 可自定义的人格预设，打造属于你的个性化的TA
* [X] 聊天基本上下文关联: 群聊场景短期记忆上下文关联，尽力避免聊天出戏
* [X] 聊天记录总结记忆: 自动总结聊天记忆，具有一定程度的长期记忆能力
* [X] 用户印象记忆: 每个人格对每个用户单独记忆印象，让TA能够记住你
* [X] 数据持久化存储: 重启后TA也不会忘记你（使用pickle保存文件）
* [X] 人格切换: 可随时切换不同人格，更多不一样的TA
* [X] 新增/编辑人格: 使用指令随时编辑TA的性格
* [X] 自定义触发词: 希望TA更主动一点？或者更有目标一点？
* [X] 自定义屏蔽词: 不想让TA学坏？需要更安全一点？
* [X] 随机参与聊天: 希望TA主动一些？TA会偶然在你的群组中冒泡……
* [X] 异步支持：赋予TA更强大的消息处理能力！
* [X] 可扩展功能: 厌倦了单调的问答AI？为TA解锁超能力吧！TA能够根据你的语言主动调用扩展模块 (如:发送图片、语音、邮件等) TA的上限取决于你的想象
* [X] 多段回复能力: 厌倦了传统一问一答的问答式聊天？TA能够做得更好！
* [X] 主动欢迎新群友: 24小时工作的全自动欢迎姬(?)
* [X] TTS文字转语音: 让TA开口说话！(通过扩展模块实现)
* [X] 潜在人格唤醒机制: 当用户呼叫未启用的人格时，可自动切换人格 (可选开关)
* [X] 定时任务: 可以用自然语言直接定时，让TA提醒你该吃饭了！
* [X] 在线搜索: GPT3.5的数据库过时了？通过主动搜索扩展让TA可以实时检索到最新的信息 (仿newbing机制)
* [ ] 主动记忆和记忆管理功能: 让TA主动记住点什么吧！hmm让我康康你记住了什么 (计划重构，为bot接入外置记忆库)
* [ ] 图片感知: 拟使用腾讯云提供的识图api，协助bot感知图片内容
* [ ] 主动聊天参与逻辑: 尽力模仿人类的聊天参与逻辑，目标是让TA能够真正融入你的群组
* [ ] 回忆录生成: 记录你们之间的点点滴滴，获取你与TA的专属回忆

## 📕 使用方式

1. 安装本插件并启用，详见NoneBot关于插件安装的说明
2. 加载插件并启动一次NoneBot服务
3. 查看自动生成的 `config/naturel_gpt.config.yml` ，并填入你的OpenAi_Api_key
4. 在机器人所在的群组或者私聊窗口@TA或者 `提到`TA当前的 `人格名` 即开始聊天
5. 使用命令 `rg / 人格设定 / 人格 / identity` 即可查看bot信息和相关指令
6. 启用后bot会开始监听所有消息并适时作出记录和回应，如果你不希望bot处理某条消息，请在消息前加上忽视符（默认为 `#` ，可在配置文件中修改）

## 🛠️ 参数说明 — `config/naturel_gpt.config.yml`

<details> <summary>🔍点击查看可配置的参数说明</summary> <pre><code>

| 参数名                        | 类型  | 释义                                       | 默认值                         | 编辑建议                                                                             |
| ----------------------------- | ----- | ------------------------------------------ | ------------------------------ | ------------------------------------------------------------------------------------ |
| ADMIN_USERID                  | array | 管理员id，以字符串列表方式填入             | ['']                           | 只有管理员可删除预设                                                                 |
| OPENAI_API_KEYS               | array | OpenAi的 `Api_Key，以字符串列表方式填入    | ['sak-xxxx']                   | 请自行替换为你的Api_Key                                                              |
| OPENAI_TIMEOUT                | int   | 请求OpenAi的超时时间 / 秒                  | 30                             | 该选项修改不生效，原因未知                                                           |
| CHAT_ENABLE_SUMMARY_CHAT      | bool  | 是否开启会话聊天记忆总结                   | False                          | 开启后能够一定程度增强bot对话记忆能力，但也会增加token消耗                           |
| CHAT_ENABLE_RECORD_ORTHER     | bool  | 是否参考非bot相关的上下文对话              | True                           | 开启后bot回复会参考近几条非bot相关信息                                               |
| MEMORY_ACTIVE                 | bool  | 是否开启主动记忆（需要同时启用记忆扩展）   | False                          | 开启后bot会自行管理记忆                                                              |
| MEMORY_MAX_LENGTH             | int   | 主动记忆最大条数                           | False                          | 主动记忆最大条数                                                                     |
| MEMORY_ENHANCE_THRESHOLD      | float | 记忆强化阈值                               | 0.8                            | 响应内容与记忆信息匹配达到阈值(0-1)时会强化记忆                                      |
| CHAT_HISTORY_MAX_TOKENS       | int   | 上下文聊天记录最大token数                  | 2048                           |                                                                                      |
| CHAT_MAX_SUMMARY_TOKENS       | int   | 聊天记录总结最大token数                    | 512                            |                                                                                      |
| REPLY_MAX_TOKENS              | int   | 生成回复的最大token数                      | 1024                           |                                                                                      |
| REQ_MAX_TOKENS                | int   | 发起请求的最大token数（即请求+回复）       | 4096                           |                                                                                      |
| CHAT_MEMORY_MAX_LENGTH        | int   | 聊天记忆最大条数                           | 16                             | 超出此长度后会进行记忆总结并删除更早的记录                                           |
| CHAT_MEMORY_SHORT_LENGTH      | int   | 短期聊天记忆参考条数                       | 8                              |                                                                                      |
| CHAT_MODEL                    | str   | 聊天生成的语言模型                         | gpt-3.5-turbo                  | 默认使用GPT3.5的模型(推荐)                                                           |
| CHAT_FREQUENCY_PENALTY        | float | 回复内容复读惩罚                           | 0.4                            | 范围(-2~2) 越高产生的回复内容越多样化                                                |
| CHAT_PRESENCE_PENALTY         | float | 回复主题重复惩罚                           | 0.4                            | 范围(-2~2) 越高越倾向于产生新的话题                                                  |
| CHAT_TEMPERATURE              | float | 聊天生成温度: 越高越随机                   | 0.4                            |                                                                                      |
| CHAT_TOP_P                    | float | 聊天信息采样率                             | 1                              |                                                                                      |
| IGNORE_PREFIX                 | str   | 忽略前置修饰：添加此修饰的聊天信息将被忽略 | #                              |                                                                                      |
| USER_MEMORY_SUMMARY_THRESHOLD | int   | 用户聊天印象总结触发阈值                   | 16                             | 越小触发越频繁，推荐10-20                                                            |
| REPLY_ON_AT                   | bool  | 在被 `@TA` 时回复                          | True                           |                                                                                      |
| REPLY_ON_NAME_MENTION         | bool  | 在被 `提及` 时回复                         | True                           | `提及` 即用户发言中含有当前bot人格名                                                 |
| REPLY_ON_WELCOME              | bool  | 在 `新成员加入` 时回复                     | True                           |                                                                                      |
| RANDOM_CHAT_PROBABILITY       | float | 随机触发聊天概率，设为0禁用                | 0                              | 调整范围[0~1]，设置过高回复频繁，会大量消耗token                                     |
| PRESETS                       | dict  | 人格预设集合                               | 略                             | 默认有四个预设，详见生成的配置文件                                                   |
| NG_DATA_PATH                  | str   | 数据文件目录                               | ./data/naturel_gpt/            | 保存实现数据持久化                                                                   |
| NG_ENABLE_EXT                 | bool  | 是否启用聊天自定义扩展                     | True                           | 开启后bot可使用扩展功能，会额外消耗token（取决于扩展描述，如未安装任何扩展务必关闭） |
| NG_EXT_PATH                   | str   | 扩展脚本文件目录                           | ./data/naturel_gpt/extensions/ | 用于保存扩展脚本的路径                                                               |
| NG_EXT_LOAD_LIST              | str   | 加载扩展列表                               |                                | 只有在此列表中的扩展会被bot使用                                                      |
| WORD_FOR_FORBIDDEN            | array | 自定义禁止触发词，以字符串列表方式填入     | []                             | 消息中含有列表中的词将呗拒绝唤醒bot（优先级高于触发词）                              |
| WORD_FOR_WAKE_UP              | array | 自定义触发词，以字符串列表方式填入         | []                             | 消息中含有列表中的词将唤醒bot                                                        |
| NG_MSG_PRIORITY               | int   | 消息响应优先级                             | 99                             | 大于1，数值越大优先级越低                                                            |
| NG_BLOCK_OTHERS               | bool  | 是否拦截其它插件的响应                     | False                          | 开启后可能导致优先级低于本插件的其他插件不响应                                       |
| NG_MAX_RESPONSE_PER_MSG       | int   | 每条消息最大回复次数                       | 5                              | 限制bot针对每条信息最大回复次数，避免封禁                                            |
| NG_ENABLE_MSG_SPLIT           | bool  | 是否允许消息分割发送                       | True                           | 如果允许，bot有可能会在一次回复中发送多条消息                                        |
| NG_ENABLE_AWAKE_IDENTITIES    | bool  | 是否允许自动唤醒其它人格                   | True                           | 如果允许，bot在检测到未启用人格呼叫时会自动唤醒并切换人格                            |
| FORBIDDEN_USERS               | array | 黑名单用户id，以字符串列表方式填入         | ['']                           | 黑名单中的用户消息不会被记录和响应设                                                 |
| UNLOCK_CONTENT_LIMIT          | bool  | 是否解锁内容限制                           | False                          | 可能导致 OpenAi 账号风险，请自行承担后果                                             |
| OPENAI_PROXY_SERVER           | str   | 请求OpenAI的代理服务器                     | ''                             | 填写示例 '127.0.0.1:1234' 或 'username:password@127.0.0.1:1234'                      |
| \_\_DEBUG\_\_                 | bool  | 是否开启DEBUG输出                          | False                          | 开启可查看prompt模板输出                                                             |

</code> </pre> </details>

## 🪄 指令说明

### 基本命令——"rg"(需要加上在NoneBot中设定的指令前缀)

- 别称: "人格"、"人格设定"、"identity"
- 功能: 查看当前可用人格预设列表和基本的插件帮助
- (*) 管理员帮助命令——"rg admin"

## 完整命令列表

<details> <summary>🔍点击展开查看完整命令列表</summary> <pre> <code>

### 基本指令

#### 获取基本信息

- 指令: `rg`
  + 功能: 用于获取会话的基本信息，包括所有可用人格
  + 返回数据示例: {code: 200, msg: (会话信息摘要生成), data: (会话详细信息)}

#### 获取基本帮助

- 指令: `rg help <options?>`
  + 功能: 用于获取插件基本帮助
  + options - 可选项:
    - `-admin`: (可选* 是否显示管理员帮助)

#### 会话开关

- 指令: `rg <on/off> <options?>`
  + 功能: 用于启用/禁用bot处理会话
  + options - 可选项:
    - `-target`: (可选* 默认当前会话)
    - `-global`: (可选* 是否应用到全部会话)

### 人格指令

#### 人格切换

- 指令: `rg set <options?> <preset_key>`
  + 功能: 用于切换会话人格
  + options - 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
    - `-global`: (可选* 启用则应用到所有会话)
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

#### 人格创建

- 指令: `rg new <options?> <preset_key> <preset_intro>`
  + 功能: 用于新建会话人格
  + 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
    - `-global`: (可选* 启用则应用到所有会话)
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

#### 人格编辑

- 指令: `rg edit <options?> <preset_key> <preset_intro>`
  + 功能: 用于修改会话人格
  + 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
    - `-global`: (可选* 启用则应用到所有会话)
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

#### 人格删除

- 指令: `rg del <options?> <preset_key>`
  + 功能: 用于删除会话人格
  + 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
    - `-global`: (可选* 启用则应用到所有会话)
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

#### 人格查询

- 指令: `rg query <options?> <preset_key>`
  + 功能: 用于查询会话人格
  + 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
  + 返回数据示例: {code: 200, msg: (查询结果), data: (查询结果)}

#### 人格重置

- 指令: `rg reset <options?> <preset_key>`
  + 功能: 用于重置会话人格(清除除人设外的所有记忆和上下文)
  + 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
    - `-deep`: (可选* 是否清除所有上下文和印象记忆)
    - `-to_default`: (可选* 是否用默认预设替代)
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

### 扩展指令

#### 扩展查询

- 指令: `rg ext`
  + 功能: 用于查询扩展信息
  + 返回数据示例: {code: 200, msg: (查询结果), data: (查询结果dict)}

#### 添加扩展
- 指令: `rg ext add <ext_name>`
  + 功能: 从GitHub仓库中 下载/更新 指定扩展 (注: 添加扩展后仍需编辑对应配置文件启用后才会加载)
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

#### 移除扩展
- 指令: `rg ext del <ext_name>`
  + 功能: 从本地文件中删除指定扩展
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

#### 启用/禁用扩展 (开发中)
- 指令: `rg ext <on/off> <ext_name>`
  + 功能: 启用/禁用 指定扩展
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

#### 重新加载扩展
- 指令: `rg ext reload`
  + 功能: 重新读取并加载所有启用的扩展
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

### 记录管理指令 (开发中)
> "记录"是bot参考知识库的一部分，发言时会参考其中的内容

#### 记录编辑 (开发中)

- 指令: `rg note edit <options?> <preset_key> <preset_intro>`
  + 功能: 用于修改会话记录
  + 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
    - `-global`: (可选* 启用则应用到所有会话)
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

#### 记录删除 (开发中)

- 指令: `rg note del <options?> <preset_key>`
  + 功能: 用于删除会话记录
  + 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
    - `-global`: (可选* 启用则应用到所有会话)
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}
#### 记录查询 (开发中)

- 指令: `rg note query <options?> <preset_key>`
  + 功能: 用于查询会话记录
  + 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
  + 返回数据示例: {code: 200, msg: (查询结果), data: (查询结果)}

</code> </pre> </details>

### [旧版指令表](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/Document.md#%E6%97%A7%E7%89%88%E6%8C%87%E4%BB%A4%E8%A1%A8)

## 🤖 行为逻辑QA

<details> <summary>🔍点击展开查看行为逻辑QA</summary> <pre> <code>

Q: 如何区分会话？

A: 根据群组(群聊场景)、私聊(个人)区分会话，即同一群组内共享一个会话，私聊窗口独占一个会话；不同人格的会话和记忆完全独立

---

Q: TA是如何产生回复的？

A: TA会根据 对话上下文(即最近几条聊天记录 不论是否与TA相关)、过往记忆(过去聊天记录的总结)、发起 `@`或 `提及`的用户印象(根据与该用户的聊天记录总结) 生成prompt模板，然后通过 OpenAi 的接口产生对应的回复发送，并且把产生的回复再填加入相应的聊天记录中

---

Q: TA如何记忆用户印象？

A: TA根据用户的id(通常是qq号)的 对TA发起 `@`或 `提及`的聊天记录、响应和历史印象 自动总结产生bot对每个用户的印象，该印象记录与会话无关(即多个会话共享)，但各个人格之间信息相互独立

---

Q: 插件如何实现记录持久化保存？

A: 由于本项目的记忆保存与人格预设存在一定耦合，故使用了pickle直接对程序中使用的数据信息进行序列化后保存为本地文件，然后在程序启动的时候使用pickle加载，这样做的好处是代码实现简便，但由于运行过程数据信息几乎都保存在内存中，如果您的bot活跃用户过多(>1k)、或者人格预设过多(>100)，可能会造成一定的性能负担，敬请见谅！

---

Q: 为什么我在编辑了配置文件中的人格预设信息后重载插件，编辑没有生效？

A: 由于用户数据信息与人格预设信息高度绑定，如果已经生成过pickle文件后程序不会再响应配置文件中人格预设的修改，而是会直接读取已有的pickle文件中的信息，您可以尝试使用 `!rg` 指令根据响应提示直接进行编辑，或者直接删除数据目录中的 `.pkl` 文件(注意：会造成bot记忆丢失)后重载程序重新生成

</code> </pre> </details>

## 🧩 自定义扩展

> 自定义扩展指的是本插件所提供的一个扩展接口，支持加载其它自定义脚本提供的功能，并且提供一套引导流程来 `教会` Bot使用这个功能，从而在bot在与用户通过自然语言聊天时能够根据场景情况主动调用对应的扩展功能

- 扩展模块存放目录(默认): `./data/naturel_gpt/extensions/` (启动加载一次本插件会自动创建)
- 注意：启用扩展后会自动在 nonebot 根目录下创建一个名为 `ext_cache` 的文件夹，该文件夹用于暂存加载的扩展包，请不要 存入/删除 其中的文件！否则可能导致 文件被误删/插件运行出错！

### 如何使用自定义扩展

> ❗你可以使用任意来源于本仓库 `/extensions/` 目录下的扩展，也可使用其它用户自行编写的扩展，但是请注意仅从你信任的来源获取，否则可能包含**危险代码**！

#### 1. 获取扩展

> 指令安装 (仅支持2.0.2 版本及以上)
使用命令: `rg ext add <ext_name>` (需要超级管理员权限)

> 手动安装 (适用于全版本)
1. 生成扩展模块存放目录(启动一次插件)
2. 将你需要安装的扩展 (通常是 `ext_xxx.py`) 放入扩展模块存放目录(默认 `./data/naturel_gpt/extensions/`)

#### 2. 进行扩展配置
> 在本插件的配置文件中正确填写以下内容( `#` 号 后内容为注释)

```yaml
    NG_EXT_LOAD_LIST:
    - EXT_NAME: ext_random  # 扩展文件名 (不含'.py')
      IS_ACTIVE: true   # 是否启用 (设为启用才会加载扩展，同时需要保证 NG_ENABLE_EXT 项开启)
      EXT_CONFIG:       # 扩展配置 如该扩展插件无要求可不写此项
        arg: value  # 填写示例 -> 参数名: 参数值 (注意缩进必须在EXT_CONFIG下一级)
    - ... # 可填写多项
```

#### 3. 重新加载本插件自动加载扩展

### 扩展列表
> 带 `*` 号的配置项为必填
#### > 随机数生成器（仅供测试使用，不建议日常开启）

- 扩展文件: ext_random.py
- 说明: 一个示例扩展，用于引导bot调用并生成随机数

#### > 发送随机二次元图片 (与ext_lolicon_pic二选一使用)

- 扩展文件: ext_random_pic.py
- 说明: 调用 `api.ixiaowai.cn` 的接口获取一张二次元图片并发送

#### > 发送指定二次元图片 (by:CCYellowStar, 与ext_random_pic二选一使用)

- 扩展文件: ext_lolicon_pic.py
- 说明: 调用 `loliconapi`接口按指定tag获取一张二次元图片并发送
- 配置项:
  + r18: 0 (添加r18参数 0为否，1为是，2为混合)

#### > 发送表情包

- 扩展文件: ext_emoticon.py
- 说明: 调用 `alapi` 接口，搜索指定关键字(由bot自主决定)的表情包并发送
- 配置项:
  + token*: 平台 token (需自行申请)

#### > 发送语音消息——极客版 (需自定义语音api)

- 扩展文件: ext_voice.py
- 说明: 调用语音生成接口实现语音回复 (需自行准备语音合成api接口)
- 配置项:
  + ng_voice_translate_on: 是否启用腾讯翻译 (默认: false)
  + tencentcloud_common_region: 腾讯翻译-地区 (默认: ap-shanghai)
  + tencentcloud_common_secretid: 腾讯翻译-密钥id
  + tencentcloud_common_secretkey: 腾讯翻译-密钥
  + g_voice_tar: 翻译目标语言 (默认: ja)
  + is_base64: 是否使用base64解码音频 (默认: false)

#### > 发送语音消息——[VOX版](https://voicevox.hiroshiba.jp/) (docker一键部署)
> VOX docker 部署指令
```bash
STEP 1. 拉取镜像
docker pull voicevox/voicevox_engine:cpu-ubuntu20.04-latest
STEP 2. 运行镜像 (二选一执行)
(前台运行) docker run --rm -it -p '50021:50021' voicevox/voicevox_engine:cpu-ubuntu20.04-latest
(后台运行) docker run --rm -d -it -p '50021:50021' voicevox/voicevox_engine:cpu-ubuntu20.04-latest
```

- 扩展文件: ext_voice.py
- 说明: 调用语音生成接口实现语音回复 (需自行准备语音合成api接口)
- 配置项:
  + ng_voice_translate_on: 是否启用腾讯翻译 (默认: false)
  + tencentcloud_common_region: 腾讯翻译-地区 (默认: ap-shanghai)
  + tencentcloud_common_secretid: 腾讯翻译-密钥id
  + tencentcloud_common_secretkey: 腾讯翻译-密钥
  + g_voice_tar: 翻译目标语言 (默认: ja)
  + is_base64: 是否使用base64解码音频 (默认: false)
  + character: 语音角色 (默认: もち子さん)
  + api_url: 搭建VOX的服务器地址 (默认: 127.0.0.1:50021 可改远程服务器地址)

#### > 使用网易邮箱向指定地址发送邮件

- 扩展文件: ext_email.py
- 说明: 向指定邮箱地址发送邮件
- 配置项: 
  + SMTP_CODE: 邮箱SMTP授权码
  + SENDER_ADDR: 邮箱地址

#### > 主动搜索扩展模块

- 扩展文件: ext_search.py
- 说明: 赋予bot主动获取互联网新信息的能力，实现类似 New Bing 的交互体验
- 配置项:
  + proxy*: http://127.0.0.1:7890 (你的代理，不填国内无法访问)
  + max_results: 搜索保留最大结果条数 (默认: 3)

#### > 阅读链接内容扩展模块

- 扩展文件: ext_readLink.py
- 说明: 赋予bot阅读链接内容的能力，貌似只能读取那种类似知乎的文字比较多的专栏类网址
- 配置项:
  + proxy*: http://127.0.0.1:7890 (你的代理，不填国内无法访问)

#### > 定时器模块

- 扩展文件: ext_timer.py
- 说明: 赋予bot预定时间的能力，到时自动推送消息

#### > 绘图模块 (by: OREOREO)

- 扩展文件: ext_paint.py
- 说明: 调用openai绘图接口，实现自然语言调用绘画，接口共用本插件的 Api Key

#### > 主动记忆能力扩展模块 (因bot使用积极性不佳，暂移入备份，不推荐使用)

- 扩展文件: ext_remember.py & ext_forget.py
- 说明: 赋予bot主动管理记忆的能力，使用时请同时启用 记忆|遗忘 扩展

### 编写自定义扩展

> 自行编写扩展需要具有一定的 Python 编程基础，如果您有相关能力可直接参考本仓库 `/extensions/` 目录下的扩展进行编写(非常简单！) 自行编写的扩展安装流程与上述相同
> 注意：该功能尚处于早期阶段，扩展编写在未来版本有可能随时变化！

✨ 如果您想分享您自行开发的扩展，可向本仓库提交pr，将您的扩展命名为 `share_ext_xxx.py`('xxx'部分可自行命名，请勿与已存在的扩展名冲突) 并上传至本仓库的 `/share_exts/` 目录下，欢迎您成为本项目的贡献者！

#### 基本的扩展模块模板
<details> <summary>🔍点击查看扩展模块编写模板</summary> <pre><code>

```python
from .Extension import Extension

# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config:dict = {
    "name": "ExtensionName",   # 扩展名称，用于标识扩展，尽量简短
    "arguments": {  
        "arg1": "int",   # 填写期望的参数类型，尽量使用简单类型，便于ai理解含义使用
        "arg2": "int",   # 注意：实际接收到的参数类型为str(由ai生成)，需要自行转换
    },
    # 扩展的描述信息，用于提示ai理解扩展的功能 *必填* 尽量简短 使用英文更节省token，添加使用示例可提高bot调用的准确度
    "description": "send ... (use eg: /#Send&xxx#/)",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": ['use extension'],
    # 每次消息回复中最大调用次数，不填则默认为99
    "max_call_times_per_msg": 99,
    # 作者信息
    "author": "",
    # 版本
    "version": "0.0.1"
    # 扩展简介
    "intro": "简介信息（查看扩展详情显示）",
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """ 当扩展被调用时执行的函数 *由扩展自行实现*

        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息

        ### 在这里处理主要的自定义逻辑

        return {  # 返回的信息将会被发送到会话中
            'text': f"[来自扩展的消息]...", # 文字信息
            'image': f"http://...",  # 图片url
            'voice': f"http://...",  # 语音url
        }

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
```

</code></pre> </details>

## 🎢 更新日志

## [2023/3/21] v2.0.2

- 切换人格时的聊天输出改为非DEBUG模式下也会发送
- 增加了扩展 安装/删除 指令，可直接从GitHub上获取到最新扩展
- 精简了非DEBUG模式下的控制台输出

## [2023/3/20] v2.0.1

- 修正 `-global` 的控制权限和逻辑 (感谢 [@Misaka-Mikoto-Tech](https://github.com/) 提供pr)
- 增加了一个新的语音扩展 `ext_VOICEVOX` 能够更便捷地实现本地部署 (感谢 @恋如雨止 提供技术支持)
- 修正回复内容首尾的空行问题；修正短纯符号回复内容未正常过滤的问题
- 修正私聊会话权限设定

## [2023/3/18] v2.0.0 项目重构 🎉
> ❗❗❗注意：本次更新需要删除原bot记忆文件重新生成(即./data/naturel_gpt文件夹)，否则可能产生无法预计的错误，同时建议将配置文件一并删除重新生成；此操作会**丢失**所有编辑过的人格预设，如果你需要在更新后继续使用，请使用 `rg query` 查询并保存预设，更新后手动导入！

- 项目完全重构，感谢 [@Misaka-Mikoto-Tech](https://github.com/) 提供的大力支持，几乎重写了所有数据管理和代码逻辑，代码质量提升明显
- 会话人格预设集完全互相独立，每个会话可单独编辑人格互不影响
- 指令表重写，多数指令提供了 `-global` 可选项支持同时编辑所有会话设置和 `-target` 指定会话远程控制操作，新指令表更具完备性，未来可能作为api接口搭配前端页面实现插件管理可视化
- `lock` / `unlock` 指令修改为是否启用人格自动切换，lock后将不会再自动唤醒不活跃人格
- 聊天消息记录改完以会话为单位分割，而不是人格，意味着每个人格都可能看到其他人格的发言信息，上下文语境理解能力增强，如果你开启了解锁人格切换，还可以体验到到"主持会议"的感觉
- 增加聊天所有消息的时间感知
- bot对用户昵称从qq昵称改为群名片昵称，同时增加新成员入群通知的昵称获取
- @消息段解析重置成更合理的逻辑，而不是直接移除@消息段
- 修复NG_ENABLE_MSG_SPLIT为false的情况下无法正常回复的问题 (感谢 [@HyPerP](https://github.com/) 提供pr) 
- 优化debug输出，改为debug分级模式，prompt输出保存到日志中
- 大量细节修改和错误修复

## [2023/3/9] v1.5.3 定时支持

- 从bot发送的信息中过滤掉纯符号短信息
- 修复记忆删除指令无法正常工作的bug
- 增加了一个定时器扩展，并提供了相关支持

## [2023/3/8] v1.5.2 自动切换人格 | 限制解除开关

- 语音扩展增加接口返回base64支持
- 修复语音扩展默认启用翻译导致报错的问题
- 为bot增加了星期几的时间感知能力
- 增加了一个可选的内容解锁限制开关
- 增加了在 `提及` 时自动切换人格的配置开关

## [2023/3/6] v1.5.1 语音合成接入翻译

- 语音合成扩展提供接入腾讯翻译api(可选开关) (感谢 [@tonato-01](https://github.com/) 提供pr) 
- 修复部分情况下bot回答时会带上自己的人称问题
- 修复插件调用次数限制不生效
- 优化bot调用扩展时的分段问题
- 修复记忆管理的编辑指令错误的问题
- 优化记忆强化功能的文本匹配规则

## [2023/3/5] v1.5.0 记忆模块更新

- 增加了bot记忆管理能力支持和记忆管理相关指令，允许bot主动 记忆/遗忘 信息，并且能自动对记忆信息进行增强以尽可能延长记忆有效时间
- 新增了两个主动记忆管理扩展(记忆和忘却模块，推荐组合使用)
- 根据GPT3.5对话模型的特点重写了prompt提示，提高bot对扩展指令识别率

## [2023/3/3] v1.4.4 邮件扩展

- 修复了修改配置文件目录后无法读取的问题 (感谢 [@he0119](https://github.com/) 提供pr) 
- 将获取响应实现将放入线程池，减少请求超时卡死 (感谢 [@he0119](https://github.com/) 提供pr) 
- 为群聊管理员增加了bot的会话管理权限 (感谢 [@HMScygnet](https://github.com/) 提供pr)
- 优化多段回复预处理，减少了自动续写出后续无关对话的频率
- 调整指令生成匹配正则，略微放宽bot调用扩展的规范程度
- 更新代理服务器时将自动补充http协议头
- 优化对话提示prompt，提高回复质量
- 新增了一个发送邮件扩展

## [2023/3/3] v1.4.3

- 禁用了huggingface 的 tokenizer的分支化，避免死锁问题

## [2023/3/3] v1.4.2

- 修复ChatGPT模型请求时间过长不会timeout的问题，提供一个配置项，可自行指定超时时间
- 增加了一个可控制是否记录参考非bot相关消息上下文的配置选项
- 为几种常见报错增加了更直观的提示
- 修复了一个扩展模块调用出错的问题
- 调整prompt，优化bot回复质量

## [2023/3/2] v1.4.1

- 修复一个prompt描述错误
- 修复一个对话过长死循环卡死的bug

## [2023/3/2] v1.4.0 ChatGpt模型更新
> 本次更新后需要更新 OpenAi SDK 至 0.27.0 版本或以上才能使用ChatGPT系列模型

- 增加了ChatGPT系列模型的支持，并针对其特点优化了prompt设置
- 增加自动欢迎新成员可关闭的配置项
- 优化了聊天内容分段输出的逻辑
- 修复了一个聊天单条消息过长导致卡死循环的bug
- 修复代理服务器配置异常(感谢 @HMScygnet 提供的修复代码)

## [2023/3/1] v1.3.7 勤俭持家 | 代理服务更新

- 优化prompt生成，为总结聊天记忆功能增加了可选开关，关闭后可降低约30%的token消耗（经过反馈该功能在较多场景下适用性有限，总体上高成本低回报，故增加了可选关闭，用户印象总结仍然保留开启）
- 增加了扩展模块传递信息，扩展模块可获得原始请求触发信息、回复信息、bot预设名，便于实现更复杂的扩展需求
- 增加了自动欢迎新入群成员的功能
- 增加代理服务器配置

## [2023/2/25] v1.3.6

- 修复了 `rg set` 指令出错的问题

## [2023/2/24] v1.3.5 黑名单 | 指令更新

- 修复了因唤醒词设置类型不规范问题导致偶发错误的问题
- 修复第一次启动自动创建数据文件夹目录失败的问题
- 为更换人格预设增加了批量操作 `-all` 指令（限管理员可用）
- 增加了 `chats` 指令，用于查看所有会话状态
- 优化 README.md 文档
- 增加了是否开启消息切分多条发送的配置项（默认开启）
- 增加了黑名单功能，在黑名单中的用户消息不会被记录和响应

## [2023/2/20] v1.3.3 扩展 | 多段发送更新

- 优化了不启用扩展模块时bot的回复质量，减少虚空调用扩展的情况
- 优化对话生成prompt，增强了bot发送多段聊天的能力
- 增加了bot感知当前时间的能力
- 从bot的发言记录中将错误的调用指令去除，避免bot重复学习错误的扩展指令使用
- 将大多数文本生成的prompt改为英文描述，尽量降低部分tokens消耗
- 新增了一个表情包扩展模块

## [2023/2/19] v1.3.2

- 修复了yaml配置中设置禁用扩展不生效的问题
- 持续优化对话生成prompt，提高bot理解使用扩展的能力
- 为 开启/关闭 会话的指令增加了 `-all` 选项，可一次性 开启/关闭 所有会话

## [2023/2/19] v1.3.1

- 优化扩展模块的参数传递
- 修改了一些扩展插件提示，更便于bot理解扩展使用方式

## [2023/2/18] v1.3.0 扩展模块功能更新

- *扩展支持：增加了插件扩展支持(插件的插件？)，支持使用自然语言自定义扩展更多功能，提供了两个示例扩展
- 多处细节优化

## [2023/2/16] v1.2.0 异步更新

> 本次更新增加了异步能力，功能可能尚不稳定，如要继续使用旧版的记忆文件请做好备份

- 异步更新：bot的回复生成开始支持异步请求，提高了消息处理速度
- 移除双回车符的停用词限制，优化了ai对长文本的输出能力
- 优化错误输出，在api请求出错时会在控制台显示错误信息以供排查
- 优化记忆逻辑，bot在请求文本错误时不会把错误提示信息一并存入记忆

### [2023/2/12] v1.1.6

- 增加切换会话是否启用的开关功能
- 增加了记忆重置功能，可指定重置当前会话的所有人格或特定人格
- 消息拦截响应、消息处理优先级支持自定义配置
- 简化帮助命令输出，分离管理员命令的帮助信息到 `rg admin` 中

### [2023/2/9] v1.1.5 唤醒词 | 屏蔽词功能更新

- 修复未创建对话前调用bot指令报错的问题
- 增加自定义触发词唤醒的功能
- 增加自定义屏蔽词拒绝回复的功能
- 增加bot随机参与聊天功能，可选择启用
- 优化了手动 `@bot` 时的信息的聊天prompt生成逻辑，使bot回复更具有指向性
- 优化配置文件管理逻辑，更新后可继续沿用原配置文件，程序加载后会自动补充更新配置文件字段

### [2023/2/6] v1.1.4

> 注意：本次更新需要删除原bot记忆文件重新生成(即./data/naturel_gpt文件夹)，否则可能产生无法预计的错误

- 修复了bot记忆串线的问题(多个群组同时使用场景下记忆混乱)
- 优化bot生成记忆和印象摘要的逻辑，提高了bot回复的速度
- 优化了控制台输出

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

> 注意：本次更新需要删除原bot记忆文件重新生成(即./data/naturel_gpt文件夹)，否则可能产生无法预计的错误

- 新增了预设编辑功能
- 新增自定义管理员id功能，管理员可以删除预设 / 修改锁定的预设
- 增加debug开关控制生成文本时的控制台输出（默认关闭）

## ⭐ Star 历史趋势图

[![Stargazers over time](https://starchart.cc/KroMiose/nonebot_plugin_naturel_gpt.svg)](https://starchart.cc/KroMiose/nonebot_plugin_naturel_gpt)
