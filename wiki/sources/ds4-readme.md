---
title: ds4.c 推理引擎
type: source
tags: [本地推理, 深度学习, 量化压缩]
source_count: 1
updated: 2026-05-09
---

> 一个「只做一个模型」的本地推理引擎，把 KV cache 当成磁盘一级公民，用非对称量化让 284B 参数的 MoE 模型在 128GB MacBook 上跑起来。

## 来源信息

- **原始链接**：`https://github.com/antirez/ds4/blob/main/README.md`
- **归档位置**：`raw/articles/ds4-readme.md`
- **作者**：Salvatore Sanfilippo（[[entities/antirez]]）
- **日期**：2026-05-09（基于 README 内容判断，项目较新）

## 项目定位

ds4.c 不是通用 GGUF 运行器，不是其他运行时的包装，也不是框架。它是一个**为 DeepSeek V4 Flash 量身定制的原生推理引擎**，核心路径是 DeepSeek V4 Flash 专用的 Metal 图执行器，配上 DS4 专属的加载器、提示词渲染、KV 状态管理和 server API 粘合层。

这种「窄赌注」是项目最鲜明的立场：本地推理领域有太多优秀项目，但新模型一发布，注意力立刻被下一个实现吸走。ds4.c 选择一次只做一个模型，做官方向量验证（用官方实现获取的 logits）、长上下文测试，以及足够的 agent 集成来确认它真的能用。

## 为什么选择 DeepSeek V4 Flash

antirez 在 README 里列出了 8 个理由，我觉得最值得关注的是这几条：

1. **思考长度与问题复杂度成正比**。在 thinking mode 下，如果避开 max thinking，它的思考段比其他模型短得多——甚至只有其他模型的 1/5。这让「开着 thinking 用模型」从不可能变成可行。
2. **1M tokens 上下文窗口**。配合极度压缩的 KV cache，这意味着本地计算机可以处理非常长的上下文。
3. **2-bit 量化可行**。但前提是用一种非常特殊的非对称量化方式：只有 routed MoE experts 被量化（up/gate 到 IQ2_XXS，down 到 Q2_K），而 shared experts、projections、routing 等保持原精度。这种「只压该压的部分」的思路，比均匀量化更有工程直觉。
4. ** quasi-frontier 的写作质量**。antirez 认为它在英语和意大利语上的写作质量接近前沿模型。

## KV Cache 作为磁盘一级公民

这是 ds4.c 最具架构启示的设计点。DeepSeek V4 的 KV cache 极度压缩，配合现代 MacBook 的 fast SSD，antirez 认为**KV cache 应该被视为磁盘的一级公民，而不是内存的附属品**。

ds4-server 支持磁盘 KV cache 持久化：

- 缓存键是 token ID 的 SHA1，而非原始文本
- 文件用普通 `read`/`write` I/O，而非 `mmap`，避免给已经映射了模型的大进程增加更多 VM 映射
- 缓存格式包含渲染文本（仅用于可观测性）和 DS4 会话 payload
- 支持四种保存时机：cold（首次长提示稳定后）、continued（预填充或生成推进时）、evict（无关请求替换内存会话前）、shutdown（服务器干净退出时）

这种设计让有用的前缀能在会话切换和服务器重启后存活。对于 agent 场景（比如 Claude Code 或 OpenCode），这意味着模型不需要每次从零开始预填充整个上下文。

## 官方向量验证

ds4.c 的测试策略也很值得注意。`tests/test-vectors` 包含从官方 DeepSeek V4 Flash API 捕获的短上下文和长上下文续写向量。本地用 `./ds4 --dump-logprobs` 生成向量，然后按 token bytes 比较。 tokenizer、template 或 attention 的回归在变成长生成失败之前就会被捕获。

这是一种**可复现的、基于官方行为的回归测试**，而不是依赖人工评估的「感觉差不多」。

## 与 agent 生态的集成

ds4-server 提供 OpenAI/Anthropic 兼容的 HTTP API：

- `GET /v1/models`
- `POST /v1/chat/completions`（OpenAI 风格，支持 tools、streaming）
- `POST /v1/messages`（Anthropic 风格，支持 thinking controls）
- `POST /v1/completions`

README 还提供了 opencode、Pi 和 Claude Code 的配置示例。这意味着 ds4.c 不是「又一个 CLI 玩具」，而是试图成为本地 agent 工作流的可信后端。

## 关于 AI 辅助开发的坦诚声明

README 里有一段非常直白的声明：

> This software is developed with strong assistance from GPT 5.5 and with humans leading the ideas, testing, and debugging. We say this openly because it shaped how the project was built. If you are not happy with AI-developed code, this software is not for you.

同时强调这离不开 llama.cpp 和 GGML——后者「largely written by hand」。这种「AI 辅助 + 人类主导 + 对上游手工工程的尊重」的三角关系，我觉得是当下 AI 时代开源项目的一个诚实模板。

## 性能数据

在 MacBook Pro M3 Max (128GB) 上，q2 量化：

- 短提示预填充：58.52 t/s
- 长提示（11k tokens）预填充：250.11 t/s
- 生成：21.47~26.68 t/s

在 Mac Studio M3 Ultra (512GB) 上，q4 量化：

- 短提示预填充：78.95 t/s
- 长提示（12k tokens）预填充：448.82 t/s
- 生成：26.62~35.50 t/s

这些数字是单线程 Metal CLI 的结果，不是 batched server 吞吐量。

---

来源：`raw/articles/ds4-readme.md`

相关页面：[[topics/local-llm-inference]] · [[entities/antirez]] · [[entities/deepseek]] · [[topics/ai-agent-harness]]
