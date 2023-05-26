# 🔮 插件指令

> [!WARNING]
> 使用插件指令时，需要加上 NoneBot 配置的指令前缀（默认为 `/`）

插件的指令使用 `rg` 作为开头，也可以使用别名 `人格` / `人格设定` / `identity`

在下方的指令中，我们使用类似 Minecraft 指令的方式来表示指令参数  
其中，使用 `<` 与 `>` 包括的是必选参数，使用 `[` 与 `]` 包括的是可选参数

**例：**指令 [人格切换](#人格切换) 的可能形式：

- `rg set 白羽`
- `rg set -global 白羽`
- `rg set -target group_1145141919 白羽`

## 基本指令

### 获取基本信息

- 指令: `rg`
- 功能: 查看当前可用人格预设列表和基本的插件帮助

### 获取基本帮助

- 指令: `rg help [options]`
- 功能: 获取插件基本帮助
- 参数:
  - `options` - _(可选)_ 额外选项
    - `-admin` - 显示管理员帮助

### 重载插件配置

- 指令: `rg reload_config`
- 功能: 重新加载插件的配置文件与数据文件

## 会话管理

### 会话开关

- 指令: `rg <on|off> [options]`
- 功能: 启用/禁用 bot 处理会话
- 参数:
  - `on|off`
    - `on` - 启用该会话
    - `off` - 禁用该会话
  - `options` - _(可选)_ 额外选项
    - `-global` - 应用到全部会话
    - `-target <chat_key>` - 指定会话
      - `chat_key` - 私聊为 `private_<QQ号>`，群聊为 `group_<群号>`

### 会话查询

- 指令: `rg chats [options]`
- 功能: 查询会话列表
- 参数:
  - `options` - _(可选)_ 额外选项
    - `-show` - 显示会话完整信息

## 人格指令

### 人格切换

- 指令: `rg set [options] <preset_key>`
- 功能: 切换会话人格
- 参数:
  - `options` - _(可选)_ 额外选项
    - `-global` - 应用到所有会话
    - `-target <chat_key>` - 指定会话
      - `chat_key` - 私聊为 `private_<QQ号>`，群聊为 `group_<群号>`
  - `preset_key` - 人格名

### 人格创建

- 指令: `rg new [options] <preset_key> <preset_intro>`
- 功能: 新建会话人格
- 参数:
  - `options` - _(可选)_ 额外选项
    - `-global` - 应用到所有会话
    - `-target <chat_key>` - 指定会话
      - `chat_key` - 私聊为 `private_<QQ号>`，群聊为 `group_<群号>`
  - `preset_key` - 人格名
  - `preset_intro` - 人格自我介绍

### 人格编辑

- 指令: `rg edit [options] <preset_key> <preset_intro>`
- 功能: 修改会话人格
- 参数:
  - `options` - _(可选)_ 额外选项
    - `-global` - 应用到所有会话
    - `-target <chat_key>` - 指定会话
      - `chat_key` - 私聊为 `private_<QQ号>`，群聊为 `group_<群号>`
  - `preset_key` - 人格名
  - `preset_intro` - 人格自我介绍

### 人格删除

- 指令: `rg del [options] <preset_key>`
- 功能: 删除会话人格
- 参数:
  - `options` - _(可选)_ 额外选项
    - `-global` - 应用到所有会话
    - `-target <chat_key>` - 指定会话
      - `chat_key` - 私聊为 `private_<QQ号>`，群聊为 `group_<群号>`
  - `preset_key` - 人格名

### 人格更名

- 指令: `rg rename [options] <old_preset_key> <new_preset_key>`
- 功能: 修改会话人格名
- 参数:
  - `options` - _(可选)_ 额外选项
    - `-global` - 应用到所有会话
    - `-target <chat_key>` - 指定会话
      - `chat_key` - 私聊为 `private_<QQ号>`，群聊为 `group_<群号>`
  - `old_preset_key` - 旧人格名
  - `new_preset_key` - 新人格名

### 人格查询

- 指令: `rg query [options] <preset_key>`
- 功能: 查询会话人格
- 参数:
  - `options` - _(可选)_ 额外选项
    - `-target <chat_key>` - 指定会话
      - `chat_key` - 私聊为 `private_<QQ号>`，群聊为 `group_<群号>`
  - `preset_key` - 人格名

### 人格重置

- 指令: `rg reset [options] <preset_key>`
- 功能: 重置会话人格 (清除除人设外的所有记忆和上下文)
- 参数:
  - `options` - _(可选)_ 额外选项
    - `-deep` - 清除所有上下文和印象记忆
    - `-to_default` - 使用默认预设替代
    - `-target <chat_key>` - 指定会话
      - `chat_key` - 私聊为 `private_<QQ号>`，群聊为 `group_<群号>`
  - `preset_key` - 人格名

## 扩展指令

### 扩展查询

- 指令: `rg ext`
- 功能: 查询扩展信息

### 添加扩展

- 指令: `rg ext add <ext_name>`
- 功能: 从 GitHub 仓库中 下载/更新 指定扩展 (注: 添加扩展后仍需编辑对应配置文件启用后才会加载)
- 参数:
  - `ext_name` - 扩展名称

### 移除扩展

- 指令: `rg ext del <ext_name>`
- 功能: 从本地文件中删除指定扩展
- 参数:
  - `ext_name` - 扩展名称

### 启用/禁用扩展

- 指令: `rg ext <on|off> <ext_name>`
- 功能: 启用/禁用 指定扩展
- 参数:
  - `on|off`
    - `on` - 启用该扩展
    - `off` - 禁用该扩展
  - `ext_name` - 扩展名称

### 重新加载扩展

- 指令: `rg ext reload`
- 功能: 重新读取并加载所有启用的扩展

## 记录管理指令 (开发中)

> "记录"是 bot 参考知识库的一部分，发言时会参考其中的内容

### 记录编辑 (开发中)

- 指令: `rg note edit [options] <preset_key> <preset_record>`
- 功能: 修改会话记录
- 参数:
  - `options` - _(可选)_ 额外选项
    - `-global` - 应用到所有会话
    - `-target <chat_key>` - 指定会话
      - `chat_key` - 私聊为 `private_<QQ号>`，群聊为 `group_<群号>`
  - `preset_key` - 人格名
  - `preset_record` - 人格记录

### 记录删除 (开发中)

- 指令: `rg note del [options] <preset_key>`
- 功能: 删除会话记录
- 参数:
  - `options` - _(可选)_ 额外选项
    - `-global` - 应用到所有会话
    - `-target <chat_key>` - 指定会话
      - `chat_key` - 私聊为 `private_<QQ号>`，群聊为 `group_<群号>`
  - `preset_key` - 人格名

### 记录查询 (开发中)

- 指令: `rg note query [options] <preset_key>`
- 功能: 查询会话记录
- 参数:
  - `options` - _(可选)_ 额外选项
    - `-target <chat_key>` - 指定会话
      - `chat_key` - 私聊为 `private_<QQ号>`，群聊为 `group_<群号>`
  - `preset_key` - 人格名

## [旧版指令表](https://github.com/KroMiose/nonebot_plugin_naturel_gpt/blob/main/Document.md#%E6%97%A7%E7%89%88%E6%8C%87%E4%BB%A4%E8%A1%A8)
