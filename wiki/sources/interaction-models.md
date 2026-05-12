---
title: Interaction Models：可扩展的人机协作方式
type: source
tags: [Agent, 多模态, 实时交互, ThinkingMachinesLab]
source_count: 1
updated: 2026-05-12
---

Thinking Machines Lab 于 2026 年 5 月发布的 interaction model 研究预览，主张**交互能力应该像智能一样被原生内建到模型中**，而不是通过外部 harness 拼接。这篇文章同时展示了新架构的定性能力和定量基准结果。

## 核心主张

当前 turn-based 模型存在严重的协作带宽瓶颈：模型在用户完成输入前完全等待，在生成过程中又冻结感知。这种“单线程现实”迫使人类去适应机器的节奏，而非相反。Thinking Machines 认为，**要让人类留在 AI 协作的循环中，交互必须是模型的一级能力**，随着模型规模扩大同步提升。

## 系统架构

整个系统由两个模型协同组成：

- **Interaction model**：持续与用户进行双向实时交换，感知和响应并发进行。它处理 200ms 的 micro-turns，输入和输出 token 都被视为流，没有人工 turn boundary。
- **Background model**：当任务需要超出瞬时响应的深度推理、工具调用或长程规划时，由 interaction model 异步委托。结果流式返回，由 interaction model 在合适的时刻自然插入对话。

这个分工让用户同时获得**非思考模型的响应延迟**和**推理模型的智能深度**。

## 关键设计选择

**Time-aligned micro-turns**
：每 200ms 处理一批输入并生成一批输出，输入输出流交错成单一 token 序列。这消除了对 VAD、turn-detection 等外部 harness 的依赖，使打断、重叠语音、时间感知和视觉主动性都成为模型的原生能力。

**Encoder-free early fusion**
：音频直接以 dMel 形式输入，经轻量嵌入层进入共享 Transformer；图像拆分为 40x40 patch，由 hMLP 编码；音频解码使用 flow head。所有组件与 Transformer 从头联合训练，避免了独立的 Whisper 式编码器或 TTS 式解码器。

**Streaming sessions 推理优化**
：现有 LLM 推理库未针对频繁小 prefill 优化。他们实现了 streaming sessions，客户端每 200ms 发送一个 chunk，服务端在 GPU 内存中持久化拼接序列，避免频繁内存重分配。该功能已 upstream 到 SGLang。

**Trainer-sampler alignment**
：实现了 batch-invariant 内核，保证不同并行策略间的比特级一致，包括用 NVLS 实现的确定性 all-reduce/reduce-scatter，以及通过统一 Split-KV 策略保持 prefill 与 decode 的累积顺序一致。

## 新能力示例

- 无缝对话管理：模型隐式追踪说话者是在思考、让步、自我纠正还是邀请回应
- 口头和视觉打断：根据上下文主动插话，而非仅在用户说完后响应
- 同时语音：用户和模型可以并发说话（例如实时翻译）
- 时间感知：模型对经过时间有原生感知
- 并发工具调用、搜索和生成式 UI：在说话和倾听的同时，模型可以并行搜索或生成界面

## 评估基准

**FD-bench v1.5**：在交互质量上大幅领先现有实时模型，同时在 Audio MultiChallenge 等智能基准上保持竞争力。

**新内部基准**：
- TimeSpeak：测试模型能否在用户指定时间主动发起语音
- CueSpeak：测试模型在正确时刻说出语义正确的回应
- RepCount-A、ProactiveVideoQA、Charades：测试视觉主动性——当视觉世界变化时模型能否主动选择说话

现有商业实时 API 在这些任务上基本保持沉默或给出错误答案。

## 模型规格

`TML-Interaction-Small`：276B 参数 MoE，12B active。更大的预训练模型目前在该设置下 serving 太慢，计划年内发布更大版本。

## 局限与未来工作

- 长会话的上下文管理仍需改进
- 低延迟音频/视频流对网络连接要求高
- 实时交互对安全对齐提出新的研究问题
- Background agent 与 interaction model 的协作方式尚处早期

来源：[Interaction Models: A Scalable Approach to Human-AI Collaboration](https://thinkingmachines.ai/blog/interaction-models/#introduction)

相关页面：[[topics/interaction-models]] · [[entities/thinking-machines-lab]] · [[topics/agent-computer-interface]] · [[topics/agentic-systems]] · [[topics/multi-agent-systems]]
