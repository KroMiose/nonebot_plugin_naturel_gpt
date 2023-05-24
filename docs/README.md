<!-- markdownlint-disable MD028 MD033 MD034 MD040 MD041 -->

# 🏠 首页

> [!INFO]
> 善用侧边栏导航（移动端请点击左下角三条横线）

## 🎏 NG 进化史

### 🗺️ [2023/5/21] 文档站上线

插件文档站上线，欢迎访问 [ng.kro.zone](https://ng.kro.zone) 查看插件文档，感谢 [@lgc2333](https://github.com/lgc2333) 为文档站 建设/勘误/整理 提供的大力支持

### 🏠 [2023/4/14] v2.1 Minecraft 服务器接入与游戏指令扩展支持 🗺️

本次更新后支持将 Bot [接入 MC 服务器](https://github.com/KroMiose/nonebot_plugin_naturel_gpt#%EF%B8%8F-mc-%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%94%AF%E6%8C%81)，并且支持 Bot 使用游戏内指令扩展

### 🎉 [2023/3/16] v2.0 项目重构完成 🎉

感谢 [@Misaka-Mikoto-Tech](https://github.com/Misaka-Mikoto-Tech) 大佬对项目重构提供的大力支持

### ✏️ [2023/3/2] v1.4 更新: 支持 ChatGPT 模型 ✏️

本次更新后插件开始支持官方 ChatGPT 模型接口，token 定价仅为 GPT3 的 1/10, 回复质量更高 响应速度更快

### 🧩 [2023/2/18] v1.3 更新: 自定义扩展支持 🧩

本次更新后插件开始支持[自定义扩展](extensions.md#👨‍💻-开发指南)，您可以直接通过自然语言直接调用多种扩展功能，包括 文本/图片/语音/邮件...  
提供了一些[样例扩展](extension_list.md)，支持仅使用少量的代码就能实现各种自定义功能!

## 💡 功能简介

> 以下未勾选功能仅表示未来可能开发的方向，不代表实际规划进度，具体开发事项可能随时变动
>
> 勾选: 已实现功能；  
> 未勾选: 正在开发 / 计划开发 / 待定设计

- [x] **自动切换 API Key**: 支持同时使用多个 OpenAI API Key，失效时自动切换
- [x] **自定义人格预设**: 可自定义的人格预设，打造属于你的个性化的 TA
- [x] **聊天基本上下文关联**: 群聊场景短期记忆上下文关联，尽力避免聊天出戏
- [x] **聊天记录总结记忆**: 自动总结聊天记忆，具有一定程度的长期记忆能力
- [x] **用户印象记忆**: 每个人格对每个用户单独记忆印象，让 TA 能够记住你
- [x] **数据持久化存储**: 重启后 TA 也不会忘记你
- [x] **人格切换**: 可随时切换不同人格，更多不一样的 TA
- [x] **新增/编辑人格**: 使用指令随时编辑 TA 的性格
- [x] **自定义触发词**: 希望 TA 更主动一点？或者更有目标一点？
- [x] **自定义屏蔽词**: 不想让 TA 学坏？需要更安全一点？
- [x] **随机参与聊天**: 希望 TA 主动一些？TA 会偶然在你的群组中冒泡……
- [x] **异步支持**: 赋予 TA 更强大的消息处理能力！
- [x] **可扩展功能**: 厌倦了单调的问答 AI？为 TA 解锁超能力吧！TA 能够根据你的语言主动调用扩展模块 (如:发送图片、语音、邮件等) TA 的上限取决于你的想象
- [x] **多段回复能力**: 厌倦了传统一问一答的问答式聊天？TA 能够做得更好！
- [x] **主动欢迎新群友**: 24 小时工作的全自动欢迎姬(?)
- [x] **TTS 文字转语音**: 让 TA 开口说话！(通过[扩展模块](extension_list.md)实现)
- [x] **潜在人格唤醒机制**: 当用户呼叫未启用的人格时，可自动切换人格 (可选开关)
- [x] **定时任务**: 可以用自然语言直接定时，让 TA 提醒你该吃饭了！
- [x] **在线搜索/读链接**: GPT3.5 的数据库过时了？通过主动搜索扩展让 TA 可以实时检索到最新的信息 (仿 New Bing 效果) (通过[扩展模块](extension_list.md)实现)
- [x] **输出内容转图片**: 使用 [htmlrender](https://github.com/kexue-z/nonebot-plugin-htmlrender) 将 TA 的回复转换为图片，降低风控几率 (可选开关，感谢 [@HMScygnet](https://github.com/HMScygnet) 提供 pr)
- [x] **Minecraft 服务器接入**: 让 TA 在游戏中为你服务，使用 GPT 的能力编写各种复杂的 NBT 指令
- [x] **消息节流机制**: 短时间内接受到大量消息时，只对最后一条消息进行回复 (可配置)
- [ ] **主动记忆和记忆管理功能**: 让 TA 主动记住点什么吧！hmm 让我康康你记住了什么 (计划重构，为 bot 接入外置记忆库)
- [ ] **图片感知**: 拟使用腾讯云提供的识图 api，协助 bot 感知图片内容
- [ ] **主动聊天参与逻辑**: 尽力模仿人类的聊天参与逻辑，目标是让 TA 能够真正融入你的群组
- [ ] **回忆录生成**: 记录你们之间的点点滴滴，获取你与 TA 的专属回忆

## 🤝 贡献列表

感谢以下开发者对本项目做出的贡献

<a href="https://github.com/KroMiose/nonebot_plugin_naturel_gpt/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=KroMiose/nonebot_plugin_naturel_gpt&max=1000" />
</a>

## ⭐ Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=KroMiose/nonebot_plugin_naturel_gpt&type=Date)](https://star-history.com/#KroMiose/nonebot_plugin_naturel_gpt&Date)
