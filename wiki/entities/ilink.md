---
title: 微信 iLink API
type: entity
tags: [微信, Bot, API, 即时通讯]
source_count: 1
updated: 2026-04-29
---

微信 iLink API 是微信面向 Bot 开发者提供的一套 HTTP JSON 接口，允许第三方服务以 Bot 身份与用户进行消息收发。它是微信生态中"非公众号、非小程序"的另一种接入方式，更轻量，也更接近传统 IM Bot 的交互模型。

## 核心端点

iLink API 的交互模型基于长轮询（long-polling）+ 推送确认：

- **`get_bot_qrcode`**：获取扫码登录二维码。Bot 需要先扫码授权，才能获得后续调用的 token
- **`get_qrcode_status`**：轮询二维码状态（`scaned`、`confirmed`、`expired`）
- **`getupdates`**：长轮询接收用户消息。服务端会在有新消息到达时立即返回，否则在超时后返回空响应。客户端需要把上次返回的 `get_updates_buf` 带回下一次请求，作为同步游标
- **`sendmessage`**：向指定用户发送消息。请求体需要包含 `to_user_id`、`context_token` 和 `item_list`
- **`sendtyping`**：发送"正在输入"状态指示器
- **`msg/notifystart`** / **`msg/notifystop`**：通知微信服务端 Bot 的上下线状态

## 消息结构

iLink 的消息模型对媒体类型有比较完整的支持：

| `item_list` type | 含义 |
|------------------|------|
| 1 | 文本 |
| 2 | 图片 |
| 3 | 语音（SILK 编码） |
| 4 | 文件 |
| 5 | 视频 |

媒体文件通过 CDN 传输，使用 AES-128-ECB 加密。上传前需要先调用 `getuploadurl` 获取预签名参数，然后加密上传，最后把 `encrypt_query_param` 和 `aes_key` 塞进消息体发送。

## 我在 Bridge 中的使用经验

在 Agent Bridge 的 `WeixinChannel` 实现中，iLink API 的几个特性直接影响了设计决策：

**长轮询超时**：`getupdates` 的超时通常在 35-38 秒左右。这意味着 `WeixinChannel` 的轮询循环不能简单用固定间隔，而要在每次请求后根据是否收到消息决定立即下一次请求还是等待。Bridge 用 `LONG_POLL_TIMEOUT_MS = 38_000` 配合 `silentTimeout: true` 来处理这个行为。

**Session 过期**：`errcode = 200018` 表示 session 已过期。Bridge 的处理策略是暂停 30 分钟后自动重新扫码登录，而不是立即重试。这是因为 iLink 对频繁登录有风控限制，立即重试只会加剧问题。

**消息去重**：微信在某些网络条件下会重复投递同一条消息。Bridge 用 `message_id` 或 `from_user_id:create_time_ms` 组合作为去重键，维护最近 60 秒的已见消息集合。

**Context Token**：回复消息时必须带回用户消息里的 `context_token`，否则消息会丢失对话上下文。这在 `WeixinChannel.send()` 中被显式处理。

## 与微信公众号/企业微信 API 的区别

iLink API 不是微信公众号的被动消息接口，也不是企业微信的自建应用接口。它更像是微信为"个人号 Bot"场景开放的实验性接口：

- 不需要注册公众号或企业主体
- 通过二维码扫码授权，而不是 AppID / AppSecret
- 用户 ID 格式为 `xxx@im.wechat`，不是 `openid`
- 支持的消息类型更贴近个人聊天体验（语音、文件、视频）

这种定位让它成为个人开发者做微信 Bot 的最低门槛路径，但也意味着它的稳定性和官方支持程度可能不如公众号或企业微信 API。

来源：[[sources/agent-bridge-design]]

相关页面：[[topics/agent-bridge]] · [[entities/openclaw]]
