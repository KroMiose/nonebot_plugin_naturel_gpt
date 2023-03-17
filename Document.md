<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="./image/README/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="./image/README/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<h1 align="center">
    🛠️ Naturel-GPT 重构指令表 ⚙️<br/>
</h1>

## 待定问题

1. 部分配置项是否跟随会话单独进行配置？具体可以进行哪些配置？
2. 拓展的配置问题
3. 是否能够实现完全完备性，即通过指令和执行指令的返回，能够做到尽可能完全地管理整个插件运行，为日后可能的前端页面控制提供接口基础(即向前端开发一个指令执行接口，实现或接近完全管理能力)
4. 记忆管理问题，等待记忆方案确定

## 重构指令

> - 基本原则: 为了避免与其他插件指令冲突，均以 `rg` 开头
> - chat_key: 用于区分每一个会话的唯一标识，一般以'private_xxx'或'group_xxx'形式呈现
> - 返回信息 => msg: 指令处理结果消息，通过matcher发送到聊天; data: 指令处理结果返回数据，返回给指令调用者(前端)

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

### 会话配置指令

#### 可用配置表 (待完善)

| config_key | config_value | type | 说明 |
| ---------- | ------------ | ---- | ---- |
|            |              |      |      |
|            |              |      |      |

#### 配置查询

- 指令: `rg config <options?>`
  + 功能: 用于查询会话配置
  + 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
  + 返回数据示例: {code: 200, msg: (查询结果), data: (查询结果dict)}

#### 配置设定

- 指令: `rg config set <options?>`
  + 功能: 用于设定会话配置
  + 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
    - `-<config_key> <config_value>`: (可选* 用于设定会话配置)
  + 返回数据示例: {code: 200, msg: (查询结果), data: (查询结果dict)}

### 全局配置指令

#### 配置查询

- 指令: `rg global`
  + 功能: 用于查询全局配置
  + 返回数据示例: {code: 200, msg: (查询结果), data: (查询结果dict)}

#### 配置设定
> - 可直接设定配置文件中的 int / float / str 类型值
> - 例如 `rg global set -RANDOM_CHAT_PROBABILITY 0.005` 即设定随机聊天概率为0.005

- 指令: `rg global set <options?>`
  + 功能: 用于设定全局配置
  + 可选项:
    - `-<config_key> <config_value>`: (可选* 用于设定全局配置)
  + 返回数据示例: {code: 200, msg: (查询结果), data: (查询结果dict)}

### 拓展指令

#### 拓展查询

- 指令: `rg ext`
  + 功能: 用于查询拓展信息
  + 返回数据示例: {code: 200, msg: (查询结果), data: (查询结果dict)}

#### 添加拓展
- 指令: `rg ext install <ext_name>`
  + 功能: 从GitHub仓库中 下载/更新 指定拓展
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

#### 移除拓展
- 指令: `rg ext remove <ext_name>`
  + 功能: 从本地文件中删除指定拓展
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

#### 启用/禁用拓展
- 指令: `rg ext <on/off> <ext_name>`
  + 功能: 启用/禁用 指定拓展
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

#### 重新加载拓展
- 指令: `rg ext reload`
  + 功能: 重新读取并加载所有启用的拓展
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

### 记录管理指令
> "记录"是bot参考知识库的一部分，发言时会参考其中的内容

#### 记录编辑

- 指令: `rg note edit <options?> <preset_key> <preset_intro>`
  + 功能: 用于修改会话记录
  + 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
    - `-global`: (可选* 启用则应用到所有会话)
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}

#### 记录删除

- 指令: `rg note del <options?> <preset_key>`
  + 功能: 用于删除会话记录
  + 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
    - `-global`: (可选* 启用则应用到所有会话)
  + 返回数据示例: {code: 200, msg: (是否成功), data: (是否成功)}
#### 记录查询

- 指令: `rg note query <options?> <preset_key>`
  + 功能: 用于查询会话记录
  + 可选项:
    - `-target <chat_key>`: (可选* 默认当前会话)
  + 返回数据示例: {code: 200, msg: (查询结果), data: (查询结果)}

---

## 旧版指令表 (重构更新后弃用)

- 查询基本信息——"rg <?admin>"
  + 功能: 用于查看插件当前状态和指令表
  + 使用示例: `rg ` (查看插件当前状态和指令表) | `rg admin` (查看插件当前状态和管理员指令表)
- 切换人格——"rg 设定 <-all>"
  + 别称: set
  + 功能: 用于切换当前bot人格
  + 使用示例: `rg set 白羽` (切换当前人格至白羽) | `rg set 白羽 -all` (切换并应用到所有会话)
- 查询人格——"rg 查询"
  + 别称: query
  + 功能: 用于查询bot人格预设信息
  + 使用示例: `rg query 白羽` (查询白羽的人格预设)
- 更新人格——"rg 更新"
  + 别称: update
  + 功能: 用于 更新/修改 指定bot人格预设
  + 使用示例: `rg update 白羽 白羽是一只可爱的喵星人...` (修改白羽的人格预设信息)
- 添加人格——"rg 添加"
  + 别称: new
  + 功能: 用于添加指定bot人格预设
  + 使用示例: `rg new 白羽 白羽是一只可爱的喵星人...` (新增名为"白羽"的人格预设信息)
- 删除人格——"rg 删除" (仅限bot管理员使用)
  + 别称: del
  + 功能: 用于删除指定人格预设，同时会删除该人格的相关记忆！
  + 使用示例: `rg del 白羽` (删除白羽人格预设)
- 锁定人格——"rg 锁定" (仅限bot管理员使用)
  + 别称: lock
  + 功能: 用于锁定指定人格预设，锁定后非管理员无法修改该预设
  + 使用示例: `rg lock 白羽` (锁定白羽人格预设)
- 解锁人格——"rg 解锁" (仅限bot管理员使用)
  + 别称: unlock
  + 功能: 用于解锁指定人格预设，解锁后允许所有用户修改此预设
  + 使用示例: `rg unlock 白羽` (解锁白羽人格预设)
- 查询拓展——"rg 拓展" (仅限bot管理员使用)
  + 别称: ext
  + 功能: 用于查询当前正常加载的所有拓展信息
  + 使用示例: `rg ext`
- 查询所有会话——"rg 会话" (仅限bot管理员使用)
  + 别称: chats
  + 功能: 用于查询当前所有会话状态
  + 使用示例: `rg chats`
- 开启会话——"rg 开启 <-all>" (仅限bot管理员或群组管理员使用)
  + 别称: on
  + 功能: 用于开启会话，开启后bot会开始按预定程序进行消息回应
  + 使用示例: `rg on` (开启当前会话) | `rg on -all` (开启所有会话)
- 停止会话——"rg 停止 <-all>" (仅限bot管理员或群组管理员使用)
  + 别称: off
  + 功能: 用于停止会话，停止后bot不再响应任何回复(包括记录消息)
  + 使用示例: `rg off` (关闭当前会话) | `rg off -all` (关闭所有会话)
- 重置会话——"rg 重置 [预设名]" (仅限bot管理员或群组管理员使用)
  + 别称: reset
  + 功能: 用于重置当前会话bot人格，包括当前人格的记忆和聊天记录等 (注: 不可撤回！)
  + 使用示例: `rg reset -all` (重置当前会话中的所有人格记忆) | `rg reset 白羽` (重置当前会话中的所有人格记忆)
- 查询记忆——"rg 记忆"
  + 别称: memory
  + 功能: 用于查询bot当前会话记忆
  + 使用示例: `rg memory` (查询当前会话的人格记忆)
- 更新记忆——"rg memory 编辑"
  + 别称: edit
  + 功能: 用于 编辑 当前bot会话的人格记忆
  + 使用示例: `rg memory edit fact 水是无毒的` (修改当前人格的记忆信息，`fact` 为记忆的键)
- 删除记忆——"rg memory 删除" (仅限bot管理员使用)
  + 别称: del
  + 功能: 用于删除指定记忆，同时会删除该记忆的相关记忆！
  + 使用示例: `rg memory del fact` (删除白羽对'fact'的记忆)