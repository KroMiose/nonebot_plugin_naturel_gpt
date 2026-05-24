# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览
本仓库包含 `nonebot-plugin-naturel-gpt`，这是一个基于 NoneBot2 框架的、高度可定制的、支持多重人格的 GPT AI 聊天插件。它支持自定义人格预设、记忆管理、扩展模块（机器人的插件）以及 Minecraft 服务器接入。

## 常用命令
本项目使用 `uv` 进行依赖管理。

- **安装依赖:**
  ```bash
  uv sync
  ```
- **运行机器人:**
  ```bash
  nb run
  ```
  *(注意：你需要安装 NoneBot CLI `nb-cli`，它已包含在开发依赖中)。*

## 高层架构
代码库围绕以下几个核心组件构建：

- **入口点 (`__init__.py`)**: 初始化插件，设置 `PersistentDataManager`、`ChatManager`、`TextGenerator`，并加载扩展模块。
- **配置管理 (`config.py`)**: 使用 Pydantic 管理插件配置。配置从 `config/naturel_gpt_config.yml` 加载并保存到该文件。它定义了所有设置，包括 API 密钥、预设和扩展配置。
- **聊天管理 (`chat.py`, `chat_manager.py`)**: 处理聊天会话的核心逻辑。`ChatManager` 管理多个 `Chat` 实例（例如，每个群组或私聊对应一个实例）。每个 `Chat` 实例管理消息历史、人格预设和上下文生成。
- **数据持久化 (`persistent_data_manager.py`)**: 负责将聊天数据、记忆和预设保存到磁盘以及从磁盘加载（支持 JSON 和 pickle 格式）。
- **API 通信 (`openai_func.py`)**: 包含 `TextGenerator` 类，负责处理与 OpenAI API（或兼容的第三方 API）的异步通信。
- **扩展模块 (`Extension.py`)**: 管理扩展的加载、解析和执行。扩展允许机器人根据自然语言请求执行操作，如发送图片、发送邮件或执行系统命令。
- **命令处理 (`matcher.py`, `command_func.py`)**: 定义 NoneBot 匹配器以拦截消息和命令（如用于管理机器人的 `rg` 命令），并将它们路由到相应的处理函数。
- **Minecraft 接入 (`MCrcon/`, `matcher_MCRcon.py`)**: 提供通过 RCON 连接到 Minecraft 服务器的支持，允许机器人在游戏中执行指令。

## 开发指南
- **配置**: 当添加需要配置的新功能时，请更新 `config.py` 中的 `Config` 类和 `CONFIG_TEMPLATE`。
- **扩展模块**: 扩展是本插件的核心功能。在修改或创建扩展时，请确保它们遵循 `Extension.py` 中定义的预期接口，并正确处理异步执行。
- **数据存储**: 使用 `PersistentDataManager` 存储任何需要在机器人重启后保留的数据。除非绝对必要，否则避免直接进行文件读写操作。
- **异步代码**: 插件严重依赖 `asyncio`。请确保所有 API 调用、文件 I/O（适用时）和长时间运行的任务都是非阻塞的异步操作。